"""Composicao do dominio em um ViewModel imutavel para o Streamlit."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path
from typing import Any

from ev_chargeops.billing import calculate_billing
from ev_chargeops.importers import import_energy_csv, import_sessions_csv
from ev_chargeops.intelligence import (
    generate_energy_recommendations,
    score_session_anomalies,
)
from ev_chargeops.models import BillingPolicy, Recommendation, Session, ValidationIssue
from ev_chargeops.viewmodels import (
    DashboardViewModel,
    EnergyPointViewModel,
    InvoiceItemViewModel,
    InvoiceRowViewModel,
    KeyValueViewModel,
    MetricViewModel,
    NoticeViewModel,
    RecommendationViewModel,
    SessionRowViewModel,
    format_brl,
    format_datetime_pt_br,
    format_kwh,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSIONS_PATH = PROJECT_ROOT / "data" / "exemplo-sessoes-sense-plus.csv"
DEFAULT_ENERGY_PATH = PROJECT_ROOT / "data" / "exemplo-energia-sems.csv"

Source = bytes | bytearray | memoryview | str | Path


def build_dashboard_view(
    sessions_source: Source = DEFAULT_SESSIONS_PATH,
    energy_source: Source = DEFAULT_ENERGY_PATH,
    *,
    sessions_filename: str | None = None,
    energy_filename: str | None = None,
    tariff_per_kwh: Decimal = Decimal("0.92"),
    monthly_common_cost: Decimal = Decimal("80.00"),
) -> DashboardViewModel:
    """Executa o pipeline completo sem persistir os dados fornecidos."""

    sessions_are_demo = _is_default_source(sessions_source, DEFAULT_SESSIONS_PATH)
    energy_is_demo = _is_default_source(energy_source, DEFAULT_ENERGY_PATH)
    uses_demo_sources = sessions_are_demo and energy_is_demo
    session_import = import_sessions_csv(sessions_source, filename=sessions_filename)
    energy_import = import_energy_csv(energy_source, filename=energy_filename)
    billing = calculate_billing(
        session_import,
        BillingPolicy(
            tariff_per_kwh=tariff_per_kwh,
            monthly_common_cost=monthly_common_cost,
        ),
    )
    anomaly_by_session = {
        alert.session_id: alert for alert in score_session_anomalies(session_import.records)
    }
    recommendations = generate_energy_recommendations(energy_import.records)
    issues_by_session = _issues_by_session(billing.issues)
    blocked_ids = {session.session_id for session in billing.blocked_sessions}
    summary = billing.summary

    session_rows = tuple(
        _session_row(session, blocked_ids, issues_by_session, anomaly_by_session)
        for session in sorted(session_import.records, key=lambda item: item.start_at)
    )
    invoice_rows = tuple(
        InvoiceRowViewModel(
            unit_id=invoice.unit_id,
            sessions=str(sum(item.item_type == "energy" for item in invoice.items)),
            energy=format_kwh(invoice.total_kwh),
            energy_cost=format_brl(invoice.energy_cost),
            common_cost=format_brl(invoice.common_cost),
            idle_cost=format_brl(invoice.idle_cost) if invoice.idle_cost else "Nao calculada",
            total=format_brl(invoice.total),
        )
        for invoice in billing.invoices
    )
    invoice_items = tuple(
        _invoice_item(invoice.unit_id, item)
        for invoice in billing.invoices
        for item in invoice.items
    )
    energy_points = tuple(
        EnergyPointViewModel(
            recorded_at=format_datetime_pt_br(snapshot.recorded_at),
            solar_kw=float(snapshot.pv_power_kw),
            load_kw=float(snapshot.load_power_kw),
            grid_kw=float(snapshot.grid_power_kw),
        )
        for snapshot in energy_import.records
    )
    generated_at = max(session.imported_at for session in session_import.records)

    return DashboardViewModel(
        title="EV ChargeOps",
        subtitle="Governanca auditavel para recarga compartilhada",
        generated_at=format_datetime_pt_br(generated_at),
        sessions_source=_source_label(
            session_import.filename, session_import.file_hash, simulated=sessions_are_demo
        ),
        energy_source=_source_label(
            energy_import.filename, energy_import.file_hash, simulated=energy_is_demo
        ),
        reference_period=_reference_period(session_import.records),
        overview_metrics=(
            MetricViewModel(
                "Sessoes importadas",
                str(summary.imported_sessions),
                "Linhas recebidas no arquivo de sessoes.",
            ),
            MetricViewModel(
                "Faturaveis",
                str(summary.billable_sessions),
                "Sessoes aprovadas pelas regras deterministicas.",
            ),
            MetricViewModel(
                "Em revisao",
                str(summary.blocked_sessions),
                "Sessoes protegidas de cobranca automatica.",
            ),
            MetricViewModel(
                "Energia faturavel",
                format_kwh(summary.billable_kwh),
                "Energia presente nas faturas do periodo.",
            ),
            MetricViewModel(
                "Total do rateio",
                format_brl(summary.grand_total),
                "Energia e custo comum demonstrativo.",
            ),
        ),
        reconciliation=(
            KeyValueViewModel("Energia importada", format_kwh(summary.imported_kwh)),
            KeyValueViewModel("Energia faturavel", format_kwh(summary.billable_kwh)),
            KeyValueViewModel("Energia em revisao", format_kwh(summary.blocked_kwh)),
            KeyValueViewModel("Custo variavel", format_brl(summary.variable_total)),
            KeyValueViewModel("Custo comum", format_brl(summary.common_total)),
            KeyValueViewModel("Total", format_brl(summary.grand_total)),
        ),
        sessions=session_rows,
        invoices=invoice_rows,
        invoice_items=invoice_items,
        energy_metrics=_energy_metrics(energy_import.records),
        energy_points=energy_points,
        recommendations=tuple(_recommendation_view(item) for item in recommendations),
        notices=(
            NoticeViewModel(
                (
                    "Dados simulados: esta demonstracao nao representa uma planta real."
                    if uses_demo_sources
                    else "Dados enviados por upload: valide a origem antes de qualquer uso real."
                ),
                "warning",
            ),
            NoticeViewModel(
                "A API GoodWe/SEMS nao esta disponivel; o MVP usa adaptadores CSV.",
                "info",
            ),
            NoticeViewModel(
                "A IA apenas prioriza revisao; regras auditaveis decidem o faturamento.",
                "info",
            ),
        ),
    )


def _issues_by_session(
    issues: Sequence[ValidationIssue],
) -> dict[str, tuple[ValidationIssue, ...]]:
    grouped: dict[str, list[ValidationIssue]] = {}
    for issue in issues:
        if issue.session_id:
            grouped.setdefault(issue.session_id, []).append(issue)
    return {key: tuple(value) for key, value in grouped.items()}


def _session_row(
    session: Session,
    blocked_ids: set[str],
    issues_by_session: dict[str, tuple[ValidationIssue, ...]],
    anomaly_by_session: dict[str, Any],
) -> SessionRowViewModel:
    blocked = session.session_id in blocked_ids
    issues = issues_by_session.get(session.session_id, ())
    messages = tuple(dict.fromkeys(issue.message for issue in issues))
    anomaly = anomaly_by_session.get(session.session_id)
    return SessionRowViewModel(
        session_id=session.session_id,
        unit_id=session.unit_id or "Sem vinculo",
        started_at=format_datetime_pt_br(session.start_at),
        duration=f"{session.duration_min} min",
        energy=format_kwh(session.energy_kwh),
        status="Em revisao" if blocked else "Concluida",
        status_key="review" if blocked else "completed",
        billing_decision="Bloquear" if blocked else "Faturar",
        alert=" | ".join(messages) if messages else "Sem bloqueios determinísticos",
        anomaly=(
            "Prioridade experimental para revisao"
            if anomaly is not None and anomaly.is_anomaly
            else "Sem sinal experimental"
        ),
    )


def _invoice_item(unit_id: str, item: Any) -> InvoiceItemViewModel:
    return InvoiceItemViewModel(
        unit_id=unit_id,
        description=item.description,
        session_id=item.session_id or "—",
        quantity="—" if item.quantity is None else f"{item.quantity:.2f}",
        unit_value="—" if item.unit_value is None else format_brl(item.unit_value),
        amount=format_brl(item.amount),
    )


def _recommendation_view(recommendation: Recommendation) -> RecommendationViewModel:
    titles = {
        "uso_solar": "Priorizar excedente solar",
        "reducao_pico": "Reduzir pico noturno",
        "ajuste_horario": "Ajustar janela de recarga",
        "pre_viabilidade_solar": "Dados insuficientes para pre-viabilidade",
    }
    return RecommendationViewModel(
        title=titles.get(recommendation.recommendation_type, "Recomendacao energetica"),
        message=recommendation.message,
        evidence=recommendation.evidence,
        assumptions=recommendation.assumptions,
        priority="Revisao humana obrigatoria",
    )


def _energy_metrics(snapshots: Sequence[Any]) -> tuple[MetricViewModel, ...]:
    if not snapshots:
        return ()
    peak_solar = max(snapshot.pv_power_kw for snapshot in snapshots)
    peak_load = max(snapshot.load_power_kw for snapshot in snapshots)
    peak_grid = max(snapshot.grid_power_kw for snapshot in snapshots)
    return (
        MetricViewModel("Pico solar", f"{peak_solar:.2f} kW", "Maior potencia FV observada."),
        MetricViewModel("Pico de carga", f"{peak_load:.2f} kW", "Maior carga observada."),
        MetricViewModel("Pico de rede", f"{peak_grid:.2f} kW", "Maior importacao da rede."),
    )


def _source_label(filename: str, file_hash: str, *, simulated: bool) -> str:
    provenance = "simulado" if simulated else "upload nao persistido"
    return f"{filename} ({provenance}, SHA-256 {file_hash[:12]}...)"


def _is_default_source(source: Source, expected: Path) -> bool:
    if not isinstance(source, (str, Path)):
        return False
    return Path(source).resolve() == expected.resolve()


def _reference_period(sessions: Sequence[Session]) -> str:
    months = sorted({(item.start_at.year, item.start_at.month) for item in sessions})
    if len(months) != 1:
        return "Periodos mistos"
    year, month = months[0]
    month_names = (
        "janeiro",
        "fevereiro",
        "marco",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro",
    )
    return f"{month_names[month - 1]}/{year}"
