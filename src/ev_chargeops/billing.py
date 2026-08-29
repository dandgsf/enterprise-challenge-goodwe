"""Motor de rateio auditavel e exportacao segura das faturas."""

from __future__ import annotations

import csv
import io
from collections import defaultdict
from collections.abc import Iterable, Sequence
from decimal import ROUND_HALF_UP, Decimal

from ev_chargeops.models import (
    BillingPolicy,
    BillingResult,
    BillingSummary,
    ImportResult,
    Invoice,
    InvoiceItem,
    Session,
    ValidationIssue,
)
from ev_chargeops.validation import blocked_session_ids, validate_sessions

CENT = Decimal("0.01")
KWH_QUANTUM = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    """Arredonda valores monetarios de forma comercial e deterministica."""

    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _allocate_common_cost(total: Decimal, units: list[str]) -> dict[str, Decimal]:
    if not units or total == 0:
        return {unit: Decimal("0.00") for unit in units}
    total_cents = int((money(total) * 100).to_integral_exact())
    quotient, remainder = divmod(total_cents, len(units))
    return {
        unit: Decimal(quotient + (1 if index < remainder else 0)) / Decimal(100)
        for index, unit in enumerate(units)
    }


def _coerce_sessions(
    source: Sequence[Session] | ImportResult[Session],
    prior_issues: Iterable[ValidationIssue],
) -> tuple[list[Session], list[ValidationIssue], int]:
    if isinstance(source, ImportResult):
        sessions = list(source.records)
        issues = [*source.issues, *prior_issues]
        imported_count = source.total_rows
    else:
        sessions = list(source)
        issues = list(prior_issues)
        imported_count = len(sessions)
    return sessions, issues, imported_count


def calculate_billing(
    source: Sequence[Session] | ImportResult[Session],
    policy: BillingPolicy | None = None,
    *,
    prior_issues: Iterable[ValidationIssue] = (),
    reference_month: str | None = None,
) -> BillingResult:
    """Calcula faturas apenas para sessoes aprovadas pelas regras deterministicas."""

    active_policy = policy or BillingPolicy()
    sessions, initial_issues, imported_count = _coerce_sessions(source, prior_issues)
    issues = validate_sessions(sessions, prior_issues=initial_issues)
    blocked_ids = blocked_session_ids(issues)
    billable = [session for session in sessions if session.session_id not in blocked_ids]
    blocked = [session for session in sessions if session.session_id in blocked_ids]
    billing_month = _billing_month(billable, reference_month)

    by_unit: dict[str, list[Session]] = defaultdict(list)
    for session in billable:
        # A validacao garante que unit_id existe antes deste ponto.
        by_unit[str(session.unit_id)].append(session)

    units = sorted(by_unit)
    common_allocations = _allocate_common_cost(active_policy.monthly_common_cost, units)
    invoices: list[Invoice] = []
    for unit in units:
        unit_sessions = sorted(by_unit[unit], key=lambda item: (item.start_at, item.session_id))
        total_kwh = sum((session.energy_kwh for session in unit_sessions), Decimal("0"))
        common_cost = common_allocations[unit]
        idle_items: list[InvoiceItem] = []
        idle_cost = Decimal("0.00")
        for session in unit_sessions:
            if session.idle_minutes is None or active_policy.idle_rate_per_minute == 0:
                continue
            chargeable_minutes = max(
                session.idle_minutes - active_policy.idle_grace_minutes,
                0,
            )
            session_idle_cost = money(
                Decimal(chargeable_minutes) * active_policy.idle_rate_per_minute
            )
            idle_cost += session_idle_cost
            if session_idle_cost:
                idle_items.append(
                    InvoiceItem(
                        item_type="idle",
                        description="Ociosidade comprovada apos franquia",
                        amount=session_idle_cost,
                        quantity=Decimal(chargeable_minutes),
                        unit_value=active_policy.idle_rate_per_minute,
                        session_id=session.session_id,
                    )
                )

        energy_items = [
            InvoiceItem(
                item_type="energy",
                description="Energia entregue na sessao",
                amount=money(session.energy_kwh * active_policy.tariff_per_kwh),
                quantity=session.energy_kwh,
                unit_value=active_policy.tariff_per_kwh,
                session_id=session.session_id,
            )
            for session in unit_sessions
        ]
        # A memoria de calculo e a autoridade monetaria: a fatura soma os
        # mesmos centavos exibidos em cada sessao, sem reconciliacao implicita.
        energy_cost = sum((item.amount for item in energy_items), Decimal("0.00"))
        common_item = InvoiceItem(
            item_type="common_cost",
            description=f"Custo comum mensal ({active_policy.common_cost_rule})",
            amount=common_cost,
        )
        invoices.append(
            Invoice(
                unit_id=unit,
                reference_month=billing_month,
                total_kwh=total_kwh.quantize(KWH_QUANTUM),
                energy_cost=energy_cost,
                common_cost=common_cost,
                idle_cost=money(idle_cost),
                total=money(energy_cost + common_cost + idle_cost),
                items=[*energy_items, common_item, *idle_items],
            )
        )

    imported_kwh = sum((session.energy_kwh for session in sessions), Decimal("0"))
    billable_kwh = sum((session.energy_kwh for session in billable), Decimal("0"))
    blocked_kwh = sum((session.energy_kwh for session in blocked), Decimal("0"))
    variable_total = sum((invoice.energy_cost for invoice in invoices), Decimal("0"))
    common_total = sum((invoice.common_cost for invoice in invoices), Decimal("0"))
    grand_total = sum((invoice.total for invoice in invoices), Decimal("0"))

    return BillingResult(
        invoices=invoices,
        billable_sessions=billable,
        blocked_sessions=blocked,
        issues=issues,
        summary=BillingSummary(
            imported_sessions=imported_count,
            billable_sessions=len(billable),
            blocked_sessions=len(blocked) + max(imported_count - len(sessions), 0),
            imported_kwh=imported_kwh.quantize(KWH_QUANTUM),
            billable_kwh=billable_kwh.quantize(KWH_QUANTUM),
            blocked_kwh=blocked_kwh.quantize(KWH_QUANTUM),
            variable_total=money(variable_total),
            common_total=money(common_total),
            grand_total=money(grand_total),
        ),
    )


def _billing_month(sessions: Sequence[Session], requested_month: str | None) -> str:
    months = sorted({session.start_at.strftime("%Y-%m") for session in sessions})
    if len(months) > 1:
        raise ValueError(
            "O fechamento e mensal; arquivos com sessoes faturaveis de meses distintos "
            "precisam ser processados separadamente."
        )
    if not months:
        return requested_month or "sem-sessoes-faturaveis"
    actual_month = months[0]
    if requested_month is not None and requested_month != actual_month:
        raise ValueError(
            f"Mes de referencia {requested_month!r} nao corresponde aos dados {actual_month!r}."
        )
    return actual_month


def sanitize_csv_cell(value: object) -> str:
    """Neutraliza celulas que planilhas poderiam interpretar como formulas."""

    text = "" if value is None else str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r")):
        return "'" + text
    return text


def export_invoices_csv(result: BillingResult) -> bytes:
    """Exporta resumo das faturas como UTF-8, neutralizando CSV injection."""

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "unit_id",
            "reference_month",
            "total_kwh",
            "energy_cost_brl",
            "common_cost_brl",
            "idle_cost_brl",
            "total_brl",
        ]
    )
    for invoice in result.invoices:
        writer.writerow(
            [
                sanitize_csv_cell(invoice.unit_id),
                sanitize_csv_cell(invoice.reference_month),
                f"{invoice.total_kwh:.2f}",
                f"{invoice.energy_cost:.2f}",
                f"{invoice.common_cost:.2f}",
                f"{invoice.idle_cost:.2f}",
                f"{invoice.total:.2f}",
            ]
        )
    return output.getvalue().encode("utf-8-sig")


# Alias explicito para consumidores que preferem o vocabulario do dominio.
calculate_invoices = calculate_billing
billing_to_csv = export_invoices_csv
