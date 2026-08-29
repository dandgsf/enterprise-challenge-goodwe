from datetime import datetime
from decimal import Decimal

import pytest
from streamlit.testing.v1 import AppTest

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
    format_decimal_pt_br,
    format_kwh,
)


@pytest.fixture
def dashboard_view_model() -> DashboardViewModel:
    return DashboardViewModel(
        title="EV ChargeOps",
        subtitle="Governança auditável para recarga compartilhada",
        generated_at="29/08/2026 14:30",
        sessions_source="exemplo-sessoes-sense-plus.csv (simulado)",
        energy_source="exemplo-energia-sems.csv (simulado)",
        reference_period="junho/2026",
        overview_metrics=(
            MetricViewModel("Sessões", "10", "Todas as sessões importadas"),
            MetricViewModel("Faturáveis", "7", "Sessões elegíveis"),
            MetricViewModel("Protegido", "14,40 kWh", "Energia não cobrada"),
            MetricViewModel("Total", "R$ 159,21", "Energia e custo comum"),
        ),
        reconciliation=(
            KeyValueViewModel("Energia importada", "100,50 kWh"),
            KeyValueViewModel("Energia faturável", "86,10 kWh"),
        ),
        sessions=(
            SessionRowViewModel(
                "SES-001",
                "APT-1201",
                "01/06/2026 08:00",
                "120 min",
                "20,00 kWh",
                "Concluída",
                "completed",
                "Faturar",
                "Sem bloqueios",
            ),
            SessionRowViewModel(
                "SES-002",
                "Sem vínculo",
                "02/06/2026 09:00",
                "30 min",
                "14,40 kWh",
                "Em revisão",
                "review",
                "Bloquear",
                "RFID sem usuario",
                "Prioridade experimental alta",
            ),
        ),
        invoices=(
            InvoiceRowViewModel(
                "APT-1201", "3", "45,70 kWh", "R$ 42,04", "R$ 20,00", "Não calculada", "R$ 62,04"
            ),
        ),
        invoice_items=(
            InvoiceItemViewModel(
                "APT-1201",
                "Energia da sessão",
                "SES-001",
                "20,00 kWh",
                "R$ 0,92/kWh",
                "R$ 18,40",
            ),
        ),
        energy_metrics=(
            MetricViewModel("Pico solar", "8,20 kW", "Maior potência fotovoltaica"),
            MetricViewModel("Pico de carga", "11,30 kW", "Maior demanda observada"),
        ),
        energy_points=(
            EnergyPointViewModel("08:00", 2.0, 5.0, 3.0),
            EnergyPointViewModel("12:00", 8.2, 6.0, -2.2),
        ),
        recommendations=(
            RecommendationViewModel(
                "Priorizar excedente solar",
                "Agendar parte das recargas para o meio-dia.",
                "Excedente observado de 2,20 kW às 12:00.",
                "Snapshot simulado; validar capacidade e recorrência.",
                "Alta",
            ),
        ),
        notices=(
            NoticeViewModel("Os dados desta demonstração são simulados.", "warning"),
            NoticeViewModel("A API GoodWe/SEMS não está disponível neste MVP.", "info"),
        ),
    )


def test_pt_br_formatters() -> None:
    assert format_decimal_pt_br(Decimal("1234.5")) == "1.234,50"
    assert format_brl(Decimal("159.21")) == "R$ 159,21"
    assert format_kwh(Decimal("86.1")) == "86,10 kWh"
    assert format_datetime_pt_br(datetime(2026, 8, 29, 14, 30)) == "29/08/2026 14:30"


def test_dashboard_smoke_renders_all_sections(
    dashboard_view_model: DashboardViewModel,
) -> None:
    def app(view_model) -> None:
        from ev_chargeops.dashboard import render_dashboard

        render_dashboard(view_model)

    dashboard = AppTest.from_function(app, args=(dashboard_view_model,), default_timeout=10).run()

    assert not dashboard.exception
    assert dashboard.header[0].value == "EV ChargeOps"
    assert len(dashboard.tabs) == 4
    assert [tab.label for tab in dashboard.tabs] == [
        "Visão geral",
        "Sessões e alertas",
        "Rateio e faturas",
        "Energia e recomendações",
    ]
    assert {metric.value for metric in dashboard.metric} >= {"10", "7", "R$ 159,21"}
    assert len(dashboard.file_uploader) == 2
    assert len(dashboard.dataframe) == 2
    assert len(dashboard.table) == 2
    assert [choice.label for choice in dashboard.radio] == ["Visualização energética"]


def test_session_filter_does_not_change_global_metrics(
    dashboard_view_model: DashboardViewModel,
) -> None:
    def app(view_model) -> None:
        from ev_chargeops.dashboard import render_dashboard

        render_dashboard(view_model)

    dashboard = AppTest.from_function(app, args=(dashboard_view_model,), default_timeout=10).run()
    original_metrics = tuple(metric.value for metric in dashboard.metric)

    dashboard.selectbox(key="session_status_filter").select("Em revisão").run()

    assert not dashboard.exception
    assert tuple(metric.value for metric in dashboard.metric) == original_metrics
    assert any("Exibindo 1 de 2 sessões" in caption.value for caption in dashboard.caption)


def test_empty_state_is_explicit() -> None:
    empty = DashboardViewModel(
        title="EV ChargeOps",
        subtitle="Sem dados",
        generated_at="Agora",
        sessions_source="Nenhuma",
        energy_source="Nenhuma",
    )

    def app(view_model) -> None:
        from ev_chargeops.dashboard import render_dashboard

        render_dashboard(view_model)

    dashboard = AppTest.from_function(app, args=(empty,), default_timeout=10).run()

    assert not dashboard.exception
    assert any("Nenhuma sessão disponível" in info.value for info in dashboard.info)
    assert any("Nenhum snapshot energético" in info.value for info in dashboard.info)
