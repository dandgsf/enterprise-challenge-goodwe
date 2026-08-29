"""Importadores seguros e auditaveis para os CSVs do MVP."""

from __future__ import annotations

import hashlib
import io
import unicodedata
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import ValidationError

from ev_chargeops.models import (
    EnergySnapshot,
    ImportResult,
    Session,
    Severity,
    ValidationIssue,
)

MAX_CSV_BYTES = 5 * 1024 * 1024

SESSION_REQUIRED_COLUMNS = frozenset(
    {
        "session_id",
        "charger_id",
        "charger_model",
        "rfid_masked",
        "user_id",
        "unit_id",
        "start_at",
        "end_at",
        "duration_min",
        "energy_kwh",
        "avg_power_kw",
        "max_power_kw",
        "current_a",
        "operation_mode",
        "session_status",
        "source_file",
        "imported_at",
        "review_flag",
        "review_reason",
    }
)

ENERGY_REQUIRED_COLUMNS = frozenset(
    {
        "snapshot_id",
        "plant_id",
        "recorded_at",
        "pv_power_kw",
        "load_power_kw",
        "grid_power_kw",
        "battery_power_kw",
        "pv_generation_kwh",
        "load_consumption_kwh",
        "grid_consumption_kwh",
        "feed_in_kwh",
        "estimated_tariff_brl_kwh",
        "recommendation_type",
        "recommendation_summary",
        "review_required",
    }
)


class CsvImportError(ValueError):
    """Falha que impede confiar na estrutura do arquivo inteiro."""


def _strip_accents(value: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )


def normalize_optional_text(value: Any) -> str | None:
    """Converte campos vazios do CSV em ``None`` e remove espacos externos."""

    if value is None or pd.isna(value):
        return None
    normalized = str(value).strip()
    return normalized or None


def normalize_boolean(value: Any) -> bool:
    """Normaliza variantes portuguesas e inglesas de sim/nao."""

    text = normalize_optional_text(value)
    if text is None:
        return False
    token = _strip_accents(text).casefold()
    if token in {"sim", "s", "true", "1", "yes", "y"}:
        return True
    if token in {"nao", "n", "false", "0", "no"}:
        return False
    raise ValueError(f"valor booleano invalido: {text!r}")


def normalize_session_status(value: Any) -> str:
    """Mapeia status de fontes heterogeneas para o vocabulario do dominio."""

    text = normalize_optional_text(value)
    if text is None:
        raise ValueError("status da sessao ausente")
    token = _strip_accents(text).casefold().replace(" ", "_")
    aliases = {
        "concluida": "completed",
        "concluido": "completed",
        "completed": "completed",
        "complete": "completed",
        "revisao": "review",
        "em_revisao": "review",
        "review": "review",
        "falha": "failed",
        "failed": "failed",
        "error": "failed",
        "cancelada": "cancelled",
        "cancelado": "cancelled",
        "cancelled": "cancelled",
        "canceled": "cancelled",
    }
    return aliases.get(token, token)


def _read_source(source: bytes | bytearray | memoryview | str | Path) -> tuple[bytes, str]:
    if isinstance(source, (bytes, bytearray, memoryview)):
        payload = bytes(source)
        filename = "upload.csv"
    else:
        path = Path(source)
        if not path.is_file():
            raise CsvImportError(f"arquivo CSV nao encontrado: {path}")
        payload = path.read_bytes()
        filename = path.name

    if not payload:
        raise CsvImportError("arquivo CSV vazio")
    if len(payload) > MAX_CSV_BYTES:
        raise CsvImportError(f"arquivo CSV excede o limite de {MAX_CSV_BYTES} bytes")
    if b"\x00" in payload:
        raise CsvImportError("arquivo CSV contem bytes nulos")
    return payload, filename


def _read_frame(payload: bytes) -> pd.DataFrame:
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CsvImportError("arquivo CSV deve usar codificacao UTF-8") from exc
    try:
        frame = pd.read_csv(
            io.StringIO(text),
            dtype=str,
            keep_default_na=False,
            na_filter=False,
            engine="python",
            on_bad_lines="error",
        )
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeError) as exc:
        raise CsvImportError("arquivo CSV vazio ou malformado") from exc
    frame.columns = [str(column).removeprefix("\ufeff").strip() for column in frame.columns]
    if frame.columns.duplicated().any():
        duplicates = sorted(set(frame.columns[frame.columns.duplicated()].tolist()))
        raise CsvImportError(f"cabecalho contem colunas duplicadas: {', '.join(duplicates)}")
    if frame.empty:
        raise CsvImportError("arquivo CSV nao contem linhas de dados")
    return frame


def _require_columns(frame: pd.DataFrame, required: frozenset[str]) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise CsvImportError(f"colunas obrigatorias ausentes: {', '.join(missing)}")


def _decimal(value: Any, *, required: bool = True) -> Decimal | None:
    text = normalize_optional_text(value)
    if text is None:
        if required:
            raise ValueError("valor decimal ausente")
        return None
    try:
        result = Decimal(text.replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError(f"valor decimal invalido: {text!r}") from exc
    if not result.is_finite():
        raise ValueError(f"valor decimal deve ser finito: {text!r}")
    return result


def _integer(value: Any, *, required: bool = True) -> int | None:
    text = normalize_optional_text(value)
    if text is None:
        if required:
            raise ValueError("valor inteiro ausente")
        return None
    try:
        return int(text)
    except ValueError as exc:
        raise ValueError(f"valor inteiro invalido: {text!r}") from exc


def _datetime(value: Any) -> datetime:
    text = normalize_optional_text(value)
    if text is None:
        raise ValueError("data/hora ausente")
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"data/hora invalida: {text!r}") from exc


def _parse_session(row: dict[str, Any], source_row: int) -> Session:
    start_at = _datetime(row["start_at"])
    end_at = _datetime(row["end_at"])
    if end_at < start_at:
        raise ValueError("termino da sessao anterior ao inicio")
    return Session(
        session_id=normalize_optional_text(row["session_id"]) or "",
        charger_id=normalize_optional_text(row["charger_id"]) or "",
        charger_model=normalize_optional_text(row["charger_model"]) or "",
        rfid_masked=normalize_optional_text(row["rfid_masked"]),
        user_id=normalize_optional_text(row["user_id"]),
        unit_id=normalize_optional_text(row["unit_id"]),
        start_at=start_at,
        end_at=end_at,
        duration_min=_integer(row["duration_min"]),
        energy_kwh=_decimal(row["energy_kwh"]),
        avg_power_kw=_decimal(row["avg_power_kw"], required=False),
        max_power_kw=_decimal(row["max_power_kw"], required=False),
        current_a=_decimal(row["current_a"], required=False),
        operation_mode=normalize_optional_text(row["operation_mode"]),
        session_status=normalize_session_status(row["session_status"]),
        source_file=normalize_optional_text(row["source_file"]) or "unknown.csv",
        imported_at=_datetime(row["imported_at"]),
        review_flag=normalize_boolean(row["review_flag"]),
        review_reason=normalize_optional_text(row["review_reason"]),
        idle_minutes=_integer(row.get("idle_minutes"), required=False),
        source_row=source_row,
    )


def _parse_energy_snapshot(row: dict[str, Any], source_row: int) -> EnergySnapshot:
    return EnergySnapshot(
        snapshot_id=normalize_optional_text(row["snapshot_id"]) or "",
        plant_id=normalize_optional_text(row["plant_id"]) or "",
        recorded_at=_datetime(row["recorded_at"]),
        pv_power_kw=_decimal(row["pv_power_kw"]),
        load_power_kw=_decimal(row["load_power_kw"]),
        grid_power_kw=_decimal(row["grid_power_kw"]),
        battery_power_kw=_decimal(row["battery_power_kw"]),
        pv_generation_kwh=_decimal(row["pv_generation_kwh"]),
        load_consumption_kwh=_decimal(row["load_consumption_kwh"]),
        grid_consumption_kwh=_decimal(row["grid_consumption_kwh"]),
        feed_in_kwh=_decimal(row["feed_in_kwh"]),
        estimated_tariff_brl_kwh=_decimal(
            row["estimated_tariff_brl_kwh"], required=False
        ),
        source_recommendation_type=normalize_optional_text(row["recommendation_type"]),
        source_recommendation_summary=normalize_optional_text(row["recommendation_summary"]),
        source_review_required=normalize_boolean(row["review_required"]),
        source_row=source_row,
    )


def _import_records[RecordT](
    source: bytes | bytearray | memoryview | str | Path,
    *,
    filename: str | None,
    required_columns: frozenset[str],
    parser: Callable[[dict[str, Any], int], RecordT],
    record_id_field: str,
) -> ImportResult[RecordT]:
    payload, inferred_filename = _read_source(source)
    frame = _read_frame(payload)
    _require_columns(frame, required_columns)

    records: list[RecordT] = []
    issues: list[ValidationIssue] = []
    for zero_index, row in frame.iterrows():
        source_row = int(zero_index) + 2
        row_dict = row.to_dict()
        try:
            record = parser(row_dict, source_row)
        except (KeyError, TypeError, ValueError, ValidationError) as exc:
            record_id = normalize_optional_text(row_dict.get(record_id_field))
            issues.append(
                ValidationIssue(
                    code="invalid_row",
                    severity=Severity.ERROR,
                    message=f"Linha rejeitada: {exc}",
                    session_id=record_id if record_id_field == "session_id" else None,
                    source_row=source_row,
                    blocks_billing=True,
                )
            )
            continue
        records.append(record)

    return ImportResult[RecordT](
        filename=filename or inferred_filename,
        file_hash=hashlib.sha256(payload).hexdigest(),
        records=records,
        issues=issues,
        total_rows=len(frame),
        rejected_rows=len(issues),
    )


def import_sessions_csv(
    source: bytes | bytearray | memoryview | str | Path,
    *,
    filename: str | None = None,
) -> ImportResult[Session]:
    """Importa sessoes de um caminho ou de bytes, sem persistir uploads."""

    return _import_records(
        source,
        filename=filename,
        required_columns=SESSION_REQUIRED_COLUMNS,
        parser=_parse_session,
        record_id_field="session_id",
    )


def import_energy_csv(
    source: bytes | bytearray | memoryview | str | Path,
    *,
    filename: str | None = None,
) -> ImportResult[EnergySnapshot]:
    """Importa snapshots energeticos de um caminho ou de bytes."""

    return _import_records(
        source,
        filename=filename,
        required_columns=ENERGY_REQUIRED_COLUMNS,
        parser=_parse_energy_snapshot,
        record_id_field="snapshot_id",
    )


# Nomes curtos para consumidores do dominio e da apresentacao.
load_sessions = import_sessions_csv
load_energy_snapshots = import_energy_csv
