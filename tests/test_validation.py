from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from ev_chargeops.importers import import_sessions_csv
from ev_chargeops.validation import blocked_session_ids, validate_sessions

DATA_PATH = Path(__file__).parents[1] / "data" / "exemplo-sessoes-sense-plus.csv"


def test_demo_blocks_only_the_three_expected_sessions() -> None:
    sessions = import_sessions_csv(DATA_PATH).records

    issues = validate_sessions(sessions)

    assert blocked_session_ids(issues) == {
        "SES-2026-06-003",
        "SES-2026-06-005",
        "SES-2026-06-007",
    }


def test_duplicate_ids_block_all_occurrences() -> None:
    session = import_sessions_csv(DATA_PATH).records[0]
    duplicate = session.model_copy(update={"energy_kwh": session.energy_kwh + 1})

    issues = validate_sessions([session, duplicate])

    duplicate_issues = [issue for issue in issues if issue.code == "duplicate_session_id"]
    assert len(duplicate_issues) == 2
    assert all(issue.blocks_billing for issue in duplicate_issues)


def test_end_before_start_is_blocked() -> None:
    session = import_sessions_csv(DATA_PATH).records[0]
    invalid = session.model_copy(update={"end_at": session.start_at - timedelta(minutes=1)})

    issues = validate_sessions([invalid])

    assert any(issue.code == "invalid_date_range" for issue in issues)
