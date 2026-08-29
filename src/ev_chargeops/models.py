"""Contratos compartilhados entre dominio, inteligencia e apresentacao."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field


class Severity(StrEnum):
    """Severidade de uma ocorrencia de validacao."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ValidationIssue(BaseModel):
    """Problema rastreavel encontrado durante importacao ou validacao."""

    model_config = ConfigDict(frozen=True)

    code: str
    severity: Severity
    message: str
    field: str | None = None
    session_id: str | None = None
    source_row: int | None = None
    blocks_billing: bool = False


class Session(BaseModel):
    """Sessao normalizada de recarga."""

    model_config = ConfigDict(frozen=True)

    session_id: str
    charger_id: str
    charger_model: str
    rfid_masked: str | None = None
    user_id: str | None = None
    unit_id: str | None = None
    start_at: datetime
    end_at: datetime
    duration_min: int = Field(ge=0)
    energy_kwh: Decimal = Field(ge=0)
    avg_power_kw: Decimal | None = Field(default=None, ge=0)
    max_power_kw: Decimal | None = Field(default=None, ge=0)
    current_a: Decimal | None = Field(default=None, ge=0)
    operation_mode: str | None = None
    session_status: str
    source_file: str
    imported_at: datetime
    review_flag: bool = False
    review_reason: str | None = None
    idle_minutes: int | None = Field(default=None, ge=0)
    source_row: int | None = None


class EnergySnapshot(BaseModel):
    """Leitura energetica normalizada da planta."""

    model_config = ConfigDict(frozen=True)

    snapshot_id: str
    plant_id: str
    recorded_at: datetime
    pv_power_kw: Decimal
    load_power_kw: Decimal
    grid_power_kw: Decimal
    battery_power_kw: Decimal
    pv_generation_kwh: Decimal = Field(ge=0)
    load_consumption_kwh: Decimal = Field(ge=0)
    grid_consumption_kwh: Decimal = Field(ge=0)
    feed_in_kwh: Decimal = Field(ge=0)
    estimated_tariff_brl_kwh: Decimal | None = Field(default=None, ge=0)
    source_recommendation_type: str | None = None
    source_recommendation_summary: str | None = None
    source_review_required: bool = False
    source_row: int | None = None


RecordT = TypeVar("RecordT")


class ImportResult[RecordT](BaseModel):
    """Resultado imutavel de uma importacao em memoria."""

    model_config = ConfigDict(frozen=True)

    filename: str
    file_hash: str
    records: list[RecordT]
    issues: list[ValidationIssue] = Field(default_factory=list)
    total_rows: int
    rejected_rows: int = 0


class BillingPolicy(BaseModel):
    """Premissas explicitas de uma execucao de rateio."""

    model_config = ConfigDict(frozen=True)

    tariff_per_kwh: Decimal = Field(default=Decimal("0.92"), ge=0)
    monthly_common_cost: Decimal = Field(default=Decimal("80.00"), ge=0)
    common_cost_rule: str = "active_units"
    idle_grace_minutes: int = Field(default=0, ge=0)
    idle_rate_per_minute: Decimal = Field(default=Decimal("0.00"), ge=0)


class InvoiceItem(BaseModel):
    """Linha auditavel de uma fatura."""

    model_config = ConfigDict(frozen=True)

    item_type: str
    description: str
    amount: Decimal
    quantity: Decimal | None = None
    unit_value: Decimal | None = None
    session_id: str | None = None


class Invoice(BaseModel):
    """Fatura mensal agregada por unidade."""

    model_config = ConfigDict(frozen=True)

    unit_id: str
    reference_month: str
    total_kwh: Decimal
    energy_cost: Decimal
    common_cost: Decimal
    idle_cost: Decimal = Decimal("0.00")
    total: Decimal
    items: list[InvoiceItem]


class BillingSummary(BaseModel):
    """Totais reconciliaveis do fechamento mensal."""

    model_config = ConfigDict(frozen=True)

    imported_sessions: int
    billable_sessions: int
    blocked_sessions: int
    imported_kwh: Decimal
    billable_kwh: Decimal
    blocked_kwh: Decimal
    variable_total: Decimal
    common_total: Decimal
    grand_total: Decimal


class BillingResult(BaseModel):
    """Faturas, exclusoes e resumo de uma execucao."""

    model_config = ConfigDict(frozen=True)

    invoices: list[Invoice]
    billable_sessions: list[Session]
    blocked_sessions: list[Session]
    issues: list[ValidationIssue]
    summary: BillingSummary


class Recommendation(BaseModel):
    """Recomendacao explicavel, sempre sujeita a validacao humana."""

    model_config = ConfigDict(frozen=True)

    recommendation_type: str
    recorded_at: datetime
    message: str
    evidence: str
    assumptions: str
    review_required: bool = True


class AnomalyAlert(BaseModel):
    """Score consultivo que nunca altera faturamento automaticamente."""

    model_config = ConfigDict(frozen=True)

    session_id: str
    anomaly_score: float
    is_anomaly: bool
    model_name: str = "IsolationForest"
    model_version: str = "experimental-mvp"
    explanation: str
