from decimal import Decimal
from pathlib import Path

from streamlit.testing.v1 import AppTest

from ev_chargeops.billing import calculate_billing
from ev_chargeops.composition import build_dashboard_view
from ev_chargeops.importers import import_sessions_csv
from ev_chargeops.models import BillingPolicy

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_sample_data_matches_pitch_acceptance_numbers() -> None:
    imported = import_sessions_csv(PROJECT_ROOT / "data" / "exemplo-sessoes-sense-plus.csv")
    result = calculate_billing(imported, BillingPolicy())

    assert result.summary.imported_sessions == 10
    assert result.summary.billable_sessions == 7
    assert result.summary.blocked_sessions == 3
    assert result.summary.imported_kwh == Decimal("100.50")
    assert result.summary.billable_kwh == Decimal("86.10")
    assert result.summary.blocked_kwh == Decimal("14.40")
    assert result.summary.variable_total == Decimal("79.21")
    assert result.summary.common_total == Decimal("80.00")
    assert result.summary.grand_total == Decimal("159.21")

    invoices = {invoice.unit_id: invoice for invoice in result.invoices}
    assert (invoices["APT-1201"].total_kwh, invoices["APT-1201"].total) == (
        Decimal("45.70"),
        Decimal("62.04"),
    )
    assert (invoices["APT-0810"].total_kwh, invoices["APT-0810"].total) == (
        Decimal("16.00"),
        Decimal("34.72"),
    )
    assert (invoices["APT-0911"].total_kwh, invoices["APT-0911"].total) == (
        Decimal("17.90"),
        Decimal("36.47"),
    )
    assert (invoices["APT-0504"].total_kwh, invoices["APT-0504"].total) == (
        Decimal("6.50"),
        Decimal("25.98"),
    )


def test_tariff_changes_money_without_changing_energy_or_common_denominator() -> None:
    baseline = build_dashboard_view()
    changed = build_dashboard_view(
        tariff_per_kwh=Decimal("1.00"),
        monthly_common_cost=Decimal("80.00"),
    )

    baseline_by_unit = {row.unit_id: row for row in baseline.invoices}
    changed_by_unit = {row.unit_id: row for row in changed.invoices}
    assert len(baseline_by_unit) == len(changed_by_unit) == 4
    assert changed_by_unit["APT-1201"].energy == baseline_by_unit["APT-1201"].energy
    assert changed_by_unit["APT-1201"].energy_cost == "R$ 45,70"
    assert all(row.common_cost == "R$ 20,00" for row in changed.invoices)


def test_real_app_starts_with_useful_default_data() -> None:
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=20).run()

    assert not app.exception
    assert app.title[0].value == "EV ChargeOps"
    assert len(app.tabs) == 4
    values = {metric.value for metric in app.metric}
    assert {"10", "7", "3", "86,10 kWh", "R$ 159,21"} <= values
    assert len(app.file_uploader) == 2
    assert len(app.number_input) == 2


def test_real_app_recalculates_when_tariff_changes() -> None:
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=20).run()

    app.number_input[0].set_value(1.0)
    app.button[0].click().run()

    assert not app.exception
    assert "R$ 166,10" in {metric.value for metric in app.metric}
    assert any("Arquivos processados" in item.value for item in app.success)
