from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ev_chargeops.billing import calculate_billing, export_invoices_csv, sanitize_csv_cell
from ev_chargeops.importers import import_sessions_csv
from ev_chargeops.models import BillingPolicy

DATA_PATH = Path(__file__).parents[1] / "data" / "exemplo-sessoes-sense-plus.csv"


def test_demo_reconciles_exact_acceptance_values() -> None:
    imported = import_sessions_csv(DATA_PATH)

    result = calculate_billing(imported)

    assert result.summary.imported_sessions == 10
    assert result.summary.billable_sessions == 7
    assert result.summary.blocked_sessions == 3
    assert result.summary.imported_kwh == Decimal("100.50")
    assert result.summary.billable_kwh == Decimal("86.10")
    assert result.summary.blocked_kwh == Decimal("14.40")
    assert result.summary.variable_total == Decimal("79.21")
    assert result.summary.common_total == Decimal("80.00")
    assert result.summary.grand_total == Decimal("159.21")

    by_unit = {invoice.unit_id: invoice for invoice in result.invoices}
    assert (by_unit["APT-1201"].total_kwh, by_unit["APT-1201"].total) == (
        Decimal("45.70"),
        Decimal("62.04"),
    )
    assert (by_unit["APT-0810"].total_kwh, by_unit["APT-0810"].total) == (
        Decimal("16.00"),
        Decimal("34.72"),
    )
    assert (by_unit["APT-0911"].total_kwh, by_unit["APT-0911"].total) == (
        Decimal("17.90"),
        Decimal("36.47"),
    )
    assert (by_unit["APT-0504"].total_kwh, by_unit["APT-0504"].total) == (
        Decimal("6.50"),
        Decimal("25.98"),
    )


def test_tariff_change_recalculates_energy_but_not_common_cost() -> None:
    imported = import_sessions_csv(DATA_PATH)
    policy = BillingPolicy(tariff_per_kwh=Decimal("1.00"))

    result = calculate_billing(imported, policy)

    assert result.summary.variable_total == Decimal("86.10")
    assert result.summary.common_total == Decimal("80.00")
    assert result.summary.grand_total == Decimal("166.10")


def test_no_valid_sessions_does_not_allocate_common_cost() -> None:
    sessions = import_sessions_csv(DATA_PATH).records
    blocked_only = [session for session in sessions if session.review_flag]

    result = calculate_billing(blocked_only)

    assert result.invoices == []
    assert result.summary.billable_sessions == 0
    assert result.summary.common_total == Decimal("0.00")
    assert result.summary.grand_total == Decimal("0.00")


def test_common_cost_rounding_preserves_total_cent_for_three_units() -> None:
    sessions = import_sessions_csv(DATA_PATH).records
    one_per_unit = [sessions[0], sessions[1], sessions[7]]
    policy = BillingPolicy(monthly_common_cost=Decimal("1.00"))

    result = calculate_billing(one_per_unit, policy)

    assert [invoice.common_cost for invoice in result.invoices] == [
        Decimal("0.34"),
        Decimal("0.33"),
        Decimal("0.33"),
    ]
    assert result.summary.common_total == Decimal("1.00")


def test_csv_export_neutralizes_formula_injection() -> None:
    session = import_sessions_csv(DATA_PATH).records[0]
    malicious = session.model_copy(update={"unit_id": '=HYPERLINK("https://invalid")'})
    result = calculate_billing([malicious])

    exported = export_invoices_csv(result).decode("utf-8-sig")

    assert "'=HYPERLINK" in exported
    assert sanitize_csv_cell(" +SUM(A1:A2)") == "' +SUM(A1:A2)"
    assert sanitize_csv_cell("APT-1201") == "APT-1201"


def test_rejects_mixed_months_in_one_monthly_closing() -> None:
    session = import_sessions_csv(DATA_PATH).records[0]
    next_month = session.model_copy(
        update={
            "session_id": "SES-NEXT-MONTH",
            "start_at": session.start_at.replace(month=7),
            "end_at": session.end_at.replace(month=7),
        }
    )

    with pytest.raises(ValueError, match="meses distintos"):
        calculate_billing([session, next_month])


def test_reference_month_must_match_the_billable_data() -> None:
    session = import_sessions_csv(DATA_PATH).records[0]

    with pytest.raises(ValueError, match="nao corresponde"):
        calculate_billing([session], reference_month="2026-07")


def test_invoice_total_reconciles_with_rounded_line_items() -> None:
    session = import_sessions_csv(DATA_PATH).records[0]
    sessions = [
        session.model_copy(update={"session_id": f"ROUND-{index}", "energy_kwh": Decimal("0.50")})
        for index in range(3)
    ]
    policy = BillingPolicy(
        tariff_per_kwh=Decimal("0.01"),
        monthly_common_cost=Decimal("0.00"),
    )

    result = calculate_billing(sessions, policy)
    invoice = result.invoices[0]

    assert invoice.energy_cost == Decimal("0.03")
    assert invoice.total == sum((item.amount for item in invoice.items), Decimal("0.00"))
