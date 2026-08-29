from decimal import Decimal

from ev_chargeops.models import BillingPolicy


def test_default_billing_policy_is_explicit() -> None:
    policy = BillingPolicy()

    assert policy.tariff_per_kwh == Decimal("0.92")
    assert policy.monthly_common_cost == Decimal("80.00")
    assert policy.idle_rate_per_minute == Decimal("0.00")

