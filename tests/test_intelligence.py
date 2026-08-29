from __future__ import annotations

import math
from datetime import datetime
from decimal import Decimal

from ev_chargeops.intelligence import (
    generate_energy_recommendations,
    score_session_anomalies,
)
from ev_chargeops.models import EnergySnapshot, Session


def _snapshot(
    snapshot_id: str,
    hour: int,
    pv: str,
    load: str,
    grid: str,
    feed_in: str,
    source_type: str,
) -> EnergySnapshot:
    return EnergySnapshot(
        snapshot_id=snapshot_id,
        plant_id="LAB-FIAP-ECO-SMART",
        recorded_at=datetime(2026, 6, 3, hour),
        pv_power_kw=Decimal(pv),
        load_power_kw=Decimal(load),
        grid_power_kw=Decimal(grid),
        battery_power_kw=Decimal("0"),
        pv_generation_kwh=Decimal("18.60"),
        load_consumption_kwh=Decimal("7.20"),
        grid_consumption_kwh=Decimal("1.10"),
        feed_in_kwh=Decimal(feed_in),
        estimated_tariff_brl_kwh=Decimal("0.92"),
        source_recommendation_type=source_type,
    )


def _session(index: int, duration: int, energy: str, avg_power: str) -> Session:
    return Session(
        session_id=f"SES-{index:03d}",
        charger_id="CHG-01",
        charger_model="GW7K HC20/HCA G2",
        rfid_masked=f"RFID-{index:03d}-MASK",
        user_id=f"USR-{index:03d}",
        unit_id=f"APT-{index:04d}",
        start_at=datetime(2026, 6, index, 8),
        end_at=datetime(2026, 6, index, 10),
        duration_min=duration,
        energy_kwh=Decimal(energy),
        avg_power_kw=Decimal(avg_power),
        max_power_kw=Decimal("6.70"),
        current_a=Decimal("29.00"),
        session_status="concluida",
        source_file="teste.csv",
        imported_at=datetime(2026, 6, 20, 10),
    )


def test_recommendations_recalculate_all_four_snapshot_scenarios() -> None:
    snapshots = [
        _snapshot("ENE-001", 12, "4.80", "2.10", "-1.40", "5.40", "uso_solar"),
        _snapshot("ENE-002", 19, "0.00", "6.70", "6.70", "5.40", "reducao_pico"),
        _snapshot("ENE-003", 10, "3.20", "1.80", "-0.60", "2.20", "pre_viabilidade_solar"),
        _snapshot("ENE-004", 8, "1.10", "4.90", "3.80", "0.00", "ajuste_horario"),
    ]

    recommendations = generate_energy_recommendations(snapshots)

    assert [item.recommendation_type for item in recommendations] == [
        "uso_solar",
        "reducao_pico",
        "pre_viabilidade_solar",
        "ajuste_horario",
    ]
    assert all(item.review_required for item in recommendations)
    assert all("PV" in item.evidence and "rede" in item.evidence for item in recommendations)
    assert all("Snapshot pontual" in item.assumptions for item in recommendations)
    assert "Dados insuficientes" in recommendations[2].message
    assert "validação técnica" in recommendations[2].message


def test_isolation_forest_scores_are_finite_deterministic_and_consultative() -> None:
    sessions = [
        _session(1, 175, "15.80", "5.42"),
        _session(2, 105, "8.40", "4.80"),
        _session(3, 315, "4.10", "0.78"),
        _session(4, 165, "13.20", "4.80"),
        _session(5, 75, "0.00", "0.00"),
        _session(6, 90, "7.60", "5.07"),
        _session(7, 140, "10.30", "4.41"),
        _session(8, 200, "17.90", "5.37"),
        _session(9, 80, "6.50", "4.88"),
        _session(10, 220, "16.70", "4.55"),
    ]

    first = score_session_anomalies(sessions)
    second = score_session_anomalies(sessions)

    assert len(first) == len(sessions)
    assert [item.anomaly_score for item in first] == [item.anomaly_score for item in second]
    assert all(math.isfinite(item.anomaly_score) for item in first)
    assert sum(item.is_anomaly for item in first) == 2
    assert all("nunca altera o faturamento" in item.explanation for item in first)


def test_small_anomaly_sample_returns_explained_neutral_scores() -> None:
    sessions = [_session(1, 175, "15.80", "5.42")]

    alerts = score_session_anomalies(sessions)

    assert alerts[0].anomaly_score == 0.0
    assert alerts[0].is_anomaly is False
    assert "Amostra insuficiente" in alerts[0].explanation


def test_empty_inputs_return_empty_outputs() -> None:
    assert generate_energy_recommendations([]) == []
    assert score_session_anomalies([]) == []
