from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from ev_chargeops.importers import CsvImportError, import_energy_csv, import_sessions_csv

DATA_DIR = Path(__file__).parents[1] / "data"


def test_imports_demo_sessions_from_path_with_hash_and_normalization() -> None:
    path = DATA_DIR / "exemplo-sessoes-sense-plus.csv"

    result = import_sessions_csv(path)

    assert result.total_rows == 10
    assert result.rejected_rows == 0
    assert len(result.records) == 10
    assert result.file_hash == hashlib.sha256(path.read_bytes()).hexdigest()
    assert result.records[0].session_status == "completed"
    assert result.records[0].review_flag is False
    assert result.records[2].session_status == "review"
    assert result.records[2].review_flag is True
    assert result.records[6].user_id is None


def test_imports_energy_from_bytes_without_persisting_upload() -> None:
    payload = (DATA_DIR / "exemplo-energia-sems.csv").read_bytes()

    result = import_energy_csv(payload, filename="energia-upload.csv")

    assert result.filename == "energia-upload.csv"
    assert result.total_rows == 4
    assert result.rejected_rows == 0
    assert result.records[0].source_review_required is True
    assert str(result.records[0].grid_power_kw) == "-1.40"


@pytest.mark.parametrize("payload", [b"", b"\x00bad", b"\xff\xfe"])
def test_rejects_empty_binary_or_non_utf8_files(payload: bytes) -> None:
    with pytest.raises(CsvImportError):
        import_sessions_csv(payload)


def test_rejects_missing_required_columns() -> None:
    with pytest.raises(CsvImportError, match="colunas obrigatorias ausentes"):
        import_sessions_csv(b"session_id,energy_kwh\nS-1,2.5\n")


def test_rejects_header_only_csv() -> None:
    header = (DATA_DIR / "exemplo-sessoes-sense-plus.csv").read_bytes().splitlines()[0]

    with pytest.raises(CsvImportError, match="nao contem linhas"):
        import_sessions_csv(header + b"\n")


def test_quarantines_invalid_rows_and_preserves_valid_rows() -> None:
    original = (DATA_DIR / "exemplo-sessoes-sense-plus.csv").read_text(encoding="utf-8")
    header, first, *_ = original.splitlines()
    invalid = first.replace(",15.80,",",-15.80,")
    payload = f"{header}\n{first}\n{invalid}\n".encode()

    result = import_sessions_csv(payload)

    assert result.total_rows == 2
    assert len(result.records) == 1
    assert result.rejected_rows == 1
    assert result.issues[0].code == "invalid_row"
    assert result.issues[0].source_row == 3
    assert result.issues[0].blocks_billing is True


def test_rejects_malformed_boolean_in_row() -> None:
    original = (DATA_DIR / "exemplo-sessoes-sense-plus.csv").read_text(encoding="utf-8")
    header, first, *_ = original.splitlines()
    invalid = first.replace(",não,", ",talvez,")

    result = import_sessions_csv(f"{header}\n{invalid}\n".encode())

    assert result.rejected_rows == 1
    assert result.records == []


def test_quarantines_end_before_start() -> None:
    original = (DATA_DIR / "exemplo-sessoes-sense-plus.csv").read_text(encoding="utf-8")
    header, first, *_ = original.splitlines()
    invalid = first.replace("2026-06-03 22:05:00", "2026-06-03 18:05:00")

    result = import_sessions_csv(f"{header}\n{invalid}\n".encode())

    assert result.rejected_rows == 1
    assert result.issues[0].code == "invalid_row"
