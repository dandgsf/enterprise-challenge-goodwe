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


def test_missing_user_is_blocked_with_explicit_reason() -> None:
    sessions = import_sessions_csv(DATA_PATH).records
    missing_user = next(session for session in sessions if session.session_id == "SES-2026-06-007")

    issues = validate_sessions([missing_user])

    issues_by_code = {issue.code: issue for issue in issues}
    assert issues_by_code["missing_user_or_unit"].blocks_billing is True


def test_failed_zero_kwh_session_has_both_blocking_reasons() -> None:
    sessions = import_sessions_csv(DATA_PATH).records
    failed = next(session for session in sessions if session.session_id == "SES-2026-06-005")

    issues = validate_sessions([failed])

    issues_by_code = {issue.code: issue for issue in issues}
    assert issues_by_code["zero_energy"].blocks_billing is True
    assert issues_by_code["non_completed_status"].blocks_billing is True
