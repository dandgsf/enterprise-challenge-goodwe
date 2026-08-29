from decimal import Decimal

import pytest
from pydantic import ValidationError

from ev_chargeops.models import BillingPolicy


def test_default_billing_policy_is_explicit() -> None:
    policy = BillingPolicy()

    assert policy.tariff_per_kwh == Decimal("0.92")
    assert policy.monthly_common_cost == Decimal("80.00")
    assert policy.idle_rate_per_minute == Decimal("0.00")


def test_common_cost_rule_cannot_claim_an_unimplemented_algorithm() -> None:
    with pytest.raises(ValidationError):
        BillingPolicy(common_cost_rule="consumption_share")  # type: ignore[arg-type]
