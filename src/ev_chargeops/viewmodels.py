"""Contratos de apresentacao prontos para consumo pelo dashboard.

Este modulo nao conhece importadores, regras de rateio ou modelos de machine
learning. A camada de composicao converte resultados do dominio para estes
objetos; a interface apenas os renderiza.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


def format_decimal_pt_br(value: Decimal, decimal_places: int = 2) -> str:
    """Formata um decimal sem depender do locale instalado no sistema."""
    quantizer = Decimal(1).scaleb(-decimal_places)
    raw = f"{value.quantize(quantizer):,.{decimal_places}f}"
    return raw.translate(str.maketrans({",": ".", ".": ","}))


def format_brl(value: Decimal) -> str:
    """Formata valor monetario no padrao exibido pelo MVP."""
    return f"R$ {format_decimal_pt_br(value)}"


def format_kwh(value: Decimal) -> str:
    """Formata energia com unidade explicita."""
    return f"{format_decimal_pt_br(value)} kWh"


def format_datetime_pt_br(value: datetime) -> str:
    """Formata instante no padrao brasileiro, preservando precisao de minuto."""
    return value.strftime("%d/%m/%Y %H:%M")


@dataclass(frozen=True, slots=True)
class MetricViewModel:
    """Indicador de alto nivel com contexto sobre a sua definicao."""

    label: str
    value: str
    context: str


@dataclass(frozen=True, slots=True)
class KeyValueViewModel:
    """Linha curta usada em reconciliacoes e premissas."""

    label: str
    value: str


@dataclass(frozen=True, slots=True)
class SessionRowViewModel:
    """Sessao pronta para exibicao e filtro visual."""

    session_id: str
    unit_id: str
    started_at: str
    duration: str
    energy: str
    status: str
    status_key: str
    billing_decision: str
    alert: str
    anomaly: str = "Nao sinalizada"

    def as_table_row(self) -> dict[str, str]:
        return {
            "Sessao": self.session_id,
            "Unidade": self.unit_id,
            "Inicio": self.started_at,
            "Duracao": self.duration,
            "Energia": self.energy,
            "Status": self.status,
            "Decisao": self.billing_decision,
            "Alerta": self.alert,
            "IA consultiva": self.anomaly,
        }


@dataclass(frozen=True, slots=True)
class InvoiceRowViewModel:
    """Fechamento por unidade, ja calculado e arredondado pelo dominio."""

    unit_id: str
    sessions: str
    energy: str
    energy_cost: str
    common_cost: str
    idle_cost: str
    total: str

    def as_table_row(self) -> dict[str, str]:
        return {
            "Unidade": self.unit_id,
            "Sessoes": self.sessions,
            "Energia": self.energy,
            "Custo de energia": self.energy_cost,
            "Custo comum": self.common_cost,
            "Ociosidade": self.idle_cost,
            "Total": self.total,
        }


@dataclass(frozen=True, slots=True)
class InvoiceItemViewModel:
    """Item auditavel da fatura selecionada."""

    unit_id: str
    description: str
    session_id: str
    quantity: str
    unit_value: str
    amount: str

    def as_table_row(self) -> dict[str, str]:
        return {
            "Descricao": self.description,
            "Sessao": self.session_id,
            "Quantidade": self.quantity,
            "Valor unitario": self.unit_value,
            "Valor": self.amount,
        }


@dataclass(frozen=True, slots=True)
class EnergyPointViewModel:
    """Ponto numerico de uma serie energetica ja selecionada."""

    recorded_at: str
    solar_kw: float
    load_kw: float
    grid_kw: float

    def as_chart_row(self) -> dict[str, str | float]:
        return {
            "Horario": self.recorded_at,
            "Solar (kW)": self.solar_kw,
            "Carga (kW)": self.load_kw,
            "Rede (kW)": self.grid_kw,
        }


@dataclass(frozen=True, slots=True)
class RecommendationViewModel:
    """Recomendacao explicavel e sujeita a revisao humana."""

    title: str
    message: str
    evidence: str
    assumptions: str
    priority: str


@dataclass(frozen=True, slots=True)
class NoticeViewModel:
    """Aviso contextual com semantica de renderizacao."""

    message: str
    level: str = "info"


@dataclass(frozen=True, slots=True)
class DashboardViewModel:
    """Snapshot imutavel e completo da pagina do EV ChargeOps."""

    title: str
    subtitle: str
    generated_at: str
    sessions_source: str
    energy_source: str
    overview_metrics: tuple[MetricViewModel, ...] = field(default_factory=tuple)
    reconciliation: tuple[KeyValueViewModel, ...] = field(default_factory=tuple)
    sessions: tuple[SessionRowViewModel, ...] = field(default_factory=tuple)
    invoices: tuple[InvoiceRowViewModel, ...] = field(default_factory=tuple)
    invoice_items: tuple[InvoiceItemViewModel, ...] = field(default_factory=tuple)
    energy_metrics: tuple[MetricViewModel, ...] = field(default_factory=tuple)
    energy_points: tuple[EnergyPointViewModel, ...] = field(default_factory=tuple)
    recommendations: tuple[RecommendationViewModel, ...] = field(default_factory=tuple)
    notices: tuple[NoticeViewModel, ...] = field(default_factory=tuple)
    reference_period: str = "Nao informado"
    idle_measurement: str = "Nao calculada por falta de evidencia (idle_minutes ausente)."


def empty_dashboard_view_model() -> DashboardViewModel:
    """Estado inicial seguro enquanto a composicao de dominio nao foi injetada."""
    return DashboardViewModel(
        title="EV ChargeOps",
        subtitle="Governanca auditavel para recarga compartilhada",
        generated_at="Aguardando processamento",
        sessions_source="Dados simulados incluidos no repositorio",
        energy_source="Dados simulados incluidos no repositorio",
        notices=(
            NoticeViewModel(
                "Os dados desta demonstracao sao simulados e nao representam uma planta real.",
                "warning",
            ),
            NoticeViewModel(
                "A API GoodWe/SEMS nao esta disponivel neste MVP; a entrada ocorre por CSV.",
                "info",
            ),
        ),
    )
