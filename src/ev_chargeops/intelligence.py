"""Inteligencia consultiva e explicavel do EV ChargeOps.

As regras deste modulo apenas produzem recomendacoes e priorizam revisoes.
Nenhum resultado altera elegibilidade ou valores do motor de faturamento.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from sklearn.ensemble import IsolationForest

from ev_chargeops.models import AnomalyAlert, EnergySnapshot, Recommendation, Session

MINIMUM_ANOMALY_SAMPLE = 5
ANOMALY_CONTAMINATION = 0.2
ANOMALY_RANDOM_STATE = 42


def generate_energy_recommendations(
    snapshots: Sequence[EnergySnapshot],
) -> list[Recommendation]:
    """Recalcula recomendacoes auditaveis a partir de leituras energeticas.

    O campo ``source_recommendation_type`` e preservado apenas como contexto de
    origem: a classificacao e a evidencia sao derivadas novamente dos numeros.
    """

    return [_recommendation_for_snapshot(snapshot) for snapshot in snapshots]


def score_session_anomalies(sessions: Sequence[Session]) -> list[AnomalyAlert]:
    """Prioriza sessoes para revisao sem interferir no faturamento.

    Uma amostra pequena demais nao sustenta o ajuste do IsolationForest; nesse
    caso cada sessao recebe um alerta neutro e uma explicacao explicita.
    """

    if not sessions:
        return []

    if len(sessions) < MINIMUM_ANOMALY_SAMPLE:
        return [
            AnomalyAlert(
                session_id=session.session_id,
                anomaly_score=0.0,
                is_anomaly=False,
                explanation=(
                    "Amostra insuficiente para o IsolationForest; resultado neutro e "
                    "consultivo, sem impacto no faturamento."
                ),
            )
            for session in sessions
        ]

    features = [_session_features(session) for session in sessions]
    model = IsolationForest(
        contamination=ANOMALY_CONTAMINATION,
        random_state=ANOMALY_RANDOM_STATE,
    )
    predictions = model.fit_predict(features)
    # decision_function e positivo para observacoes mais normais. Inverter o
    # sinal torna o score maior para sessoes mais atipicas, facilitando a leitura.
    anomaly_scores = -model.decision_function(features)

    return [
        AnomalyAlert(
            session_id=session.session_id,
            anomaly_score=float(score),
            is_anomaly=prediction == -1,
            explanation=(
                "Priorizacao experimental baseada em duracao, energia e potencia; "
                "requer revisao humana e nunca altera o faturamento."
            ),
        )
        for session, prediction, score in zip(sessions, predictions, anomaly_scores, strict=True)
    ]


def _recommendation_for_snapshot(snapshot: EnergySnapshot) -> Recommendation:
    evidence = _energy_evidence(snapshot)
    assumptions = (
        "Snapshot pontual, sinais de rede conforme a fonte e tarifa estimada; "
        "confirmar serie historica, capacidade eletrica e operacao local."
    )

    if snapshot.source_recommendation_type == "pre_viabilidade_solar":
        return Recommendation(
            recommendation_type="pre_viabilidade_solar",
            recorded_at=snapshot.recorded_at,
            message=(
                "Dados insuficientes para pre-viabilidade fotovoltaica. Reunir uma serie "
                "historica representativa e solicitar validacao tecnica antes de decidir."
            ),
            evidence=evidence,
            assumptions=assumptions,
        )

    if snapshot.recorded_at.hour >= 18 and snapshot.grid_power_kw > 0:
        return Recommendation(
            recommendation_type="reducao_pico",
            recorded_at=snapshot.recorded_at,
            message=(
                "Escalonar as recargas no inicio da noite para reduzir a concentracao de "
                "demanda importada da rede."
            ),
            evidence=evidence,
            assumptions=assumptions,
        )

    # ``feed_in_kwh`` pode ser acumulado no dia. A decisao sobre excedente
    # instantaneo usa o sinal de potencia da rede para evitar falso positivo.
    if snapshot.grid_power_kw < 0:
        return Recommendation(
            recommendation_type="uso_solar",
            recorded_at=snapshot.recorded_at,
            message=(
                "Priorizar recargas proximas desta janela para aproveitar o excedente solar, "
                "sujeito a confirmacao recorrente do perfil de geracao."
            ),
            evidence=evidence,
            assumptions=assumptions,
        )

    return Recommendation(
        recommendation_type="ajuste_horario",
        recorded_at=snapshot.recorded_at,
        message=(
            "Avaliar o deslocamento de parte das recargas para uma janela com maior geracao "
            "solar e menor dependencia da rede."
        ),
        evidence=evidence,
        assumptions=assumptions,
    )


def _energy_evidence(snapshot: EnergySnapshot) -> str:
    return (
        f"PV {snapshot.pv_power_kw:.2f} kW; carga {snapshot.load_power_kw:.2f} kW; "
        f"rede {snapshot.grid_power_kw:.2f} kW; injecao acumulada "
        f"{snapshot.feed_in_kwh:.2f} kWh."
    )


def _session_features(session: Session) -> list[float]:
    duration_hours = Decimal(session.duration_min) / Decimal(60)
    calculated_power = session.energy_kwh / duration_hours if duration_hours > 0 else Decimal("0")
    average_power = session.avg_power_kw if session.avg_power_kw is not None else calculated_power
    maximum_power = session.max_power_kw if session.max_power_kw is not None else average_power
    current = session.current_a if session.current_a is not None else Decimal("0")

    return [
        float(session.duration_min),
        float(session.energy_kwh),
        float(average_power),
        float(maximum_power),
        float(current),
    ]
