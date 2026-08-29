"""Leitura antecipadamente limitada de uploads mantidos em memória."""

from __future__ import annotations

from typing import Protocol

from ev_chargeops.importers import MAX_CSV_BYTES


class Upload(Protocol):
    """Contrato mínimo fornecido por ``streamlit.UploadedFile``."""

    name: str
    size: int

    def getvalue(self) -> bytes: ...


def read_upload_pair(sessions_upload: Upload, energy_upload: Upload) -> tuple[bytes, bytes]:
    """Valida o tamanho antes de alocar o conteúdo integral dos dois uploads."""

    oversized = [
        upload.name
        for upload in (sessions_upload, energy_upload)
        if upload.size > MAX_CSV_BYTES
    ]
    if oversized:
        raise ValueError(
            f"CSV excede o limite de {MAX_CSV_BYTES // (1024 * 1024)} MB: "
            + ", ".join(oversized)
        )
    return sessions_upload.getvalue(), energy_upload.getvalue()
