"""Regras deterministicas de validacao e elegibilidade de sessoes."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from decimal import Decimal

from ev_chargeops.models import Session, Severity, ValidationIssue


def _issue(
    session: Session,
    code: str,
    message: str,
    *,
    field: str | None = None,
    severity: Severity = Severity.ERROR,
    blocks_billing: bool = True,
) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        severity=severity,
        message=message,
        field=field,
        session_id=session.session_id,
        source_row=session.source_row,
        blocks_billing=blocks_billing,
    )


def validate_sessions(
    sessions: Sequence[Session],
    *,
    prior_issues: Iterable[ValidationIssue] = (),
) -> list[ValidationIssue]:
    """Valida sessoes sem permitir que alertas de IA decidam faturamento."""

    issues = list(prior_issues)
    id_counts = Counter(session.session_id for session in sessions)

    for session in sessions:
        if not session.session_id.strip():
            issues.append(_issue(session, "missing_session_id", "ID da sessao ausente."))
        elif id_counts[session.session_id] > 1:
            issues.append(
                _issue(
                    session,
                    "duplicate_session_id",
                    "ID de sessao duplicado; todas as ocorrencias foram bloqueadas.",
                    field="session_id",
                )
            )

        if not session.charger_id.strip() or not session.charger_model.strip():
            issues.append(
                _issue(
                    session,
                    "missing_charger",
                    "Carregador ou modelo nao identificado.",
                    field="charger_id",
                )
            )
        if not session.user_id or not session.unit_id:
            issues.append(
                _issue(
                    session,
                    "missing_user_or_unit",
                    "Usuario e unidade precisam estar vinculados para faturamento.",
                    field="user_id",
                )
            )
        if session.end_at < session.start_at:
            issues.append(
                _issue(
                    session,
                    "invalid_date_range",
                    "Termino da sessao anterior ao inicio.",
                    field="end_at",
                )
            )
        if session.duration_min < 0 or session.energy_kwh < Decimal("0"):
            issues.append(
                _issue(
                    session,
                    "negative_measurement",
                    "Duracao e energia nao podem ser negativas.",
                )
            )
        if session.energy_kwh == Decimal("0"):
            issues.append(
                _issue(
                    session,
                    "zero_energy",
                    "Sessao sem energia entregue nao pode ser faturada.",
                    field="energy_kwh",
                )
            )
        if session.session_status != "completed":
            issues.append(
                _issue(
                    session,
                    "non_completed_status",
                    f"Status {session.session_status!r} nao e faturavel.",
                    field="session_status",
                )
            )
        if session.review_flag:
            issues.append(
                _issue(
                    session,
                    "manual_review_required",
                    session.review_reason or "Sessao marcada para revisao humana.",
                    field="review_flag",
                )
            )

    return issues


def blocked_session_ids(issues: Iterable[ValidationIssue]) -> set[str]:
    """Retorna IDs bloqueados somente por regras deterministicas."""

    return {
        issue.session_id
        for issue in issues
        if issue.blocks_billing and issue.session_id is not None
    }


def is_session_billable(session: Session, issues: Iterable[ValidationIssue]) -> bool:
    """Informa elegibilidade de uma sessao a partir das ocorrencias rastreaveis."""

    return session.session_id not in blocked_session_ids(issues)
