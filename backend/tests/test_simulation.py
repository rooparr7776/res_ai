from backend.app.evaluation import calculate_metrics, run_evaluation
from backend.app.schemas import (
    EvaluationEpisodeRecord,
    EvaluationRequest,
    SimulationInputs,
)
from backend.app.simulation import simulate


def inputs(**overrides):
    values = {
        "scenario_id": "pedestrian_crossing",
        "scenario_name": "Pedestrian crossing",
        "policy": "safety_aware",
        "speed_kmh": 40,
        "obstacle_distance_m": 35,
        "visibility": 0.9,
        "closing_speed_kmh": 40,
        "hazard_severity": 0.9,
        "in_predicted_path": True,
        "perception_confidence": 0.9,
        "obstacle_present": True,
    }
    values.update(overrides)
    return SimulationInputs(**values)


def test_simulation_is_reproducible_and_has_decision_log():
    first = simulate(inputs())
    second = simulate(inputs())
    assert first.model_dump() == second.model_dump()
    assert first.decision_log[0].event == "decision"
    assert first.decision_log[-1].event == "episode_complete"
    assert first.timeline[-1].time_s > 0


def test_high_risk_is_not_itself_recorded_as_a_collision():
    result = simulate(
        inputs(
            speed_kmh=200,
            obstacle_distance_m=1000,
            closing_speed_kmh=200,
            visibility=0,
            hazard_severity=1.0,
            perception_confidence=0,
        )
    )
    assert result.risk.risk_score >= 60
    assert result.collision is False


def test_collision_is_determined_by_the_kinematic_episode():
    result = simulate(inputs(obstacle_distance_m=2))
    assert result.risk.risk_score < 100
    assert result.collision is True
    assert result.outcome == "collision"


def test_clear_road_has_no_collision_and_no_separation_metric():
    result = simulate(
        inputs(
            scenario_id="clear_road",
            scenario_name="Clear road",
            obstacle_present=False,
            in_predicted_path=False,
            hazard_severity=0,
            obstacle_distance_m=120,
        )
    )
    assert result.outcome == "no_hazard"
    assert result.minimum_separation_m is None
    assert result.collision is False


def test_evaluation_is_seeded_and_pairs_identical_inputs():
    request = EvaluationRequest(scenario_ids=["sudden_braking"], episodes_per_scenario=3, seed=17)
    first = run_evaluation(request)
    second = run_evaluation(request)
    assert first.model_dump() == second.model_dump()
    baseline = [r for r in first.episode_records if r.policy == "baseline"]
    aware = [r for r in first.episode_records if r.policy == "safety_aware"]
    assert len(baseline) == len(aware) == 3
    for baseline_record, aware_record in zip(baseline, aware):
        assert baseline_record.episode_index == aware_record.episode_index
        assert (
            baseline_record.speed_kmh,
            baseline_record.obstacle_distance_m,
            baseline_record.visibility,
            baseline_record.closing_speed_kmh,
            baseline_record.hazard_severity,
            baseline_record.in_predicted_path,
            baseline_record.perception_confidence,
            baseline_record.obstacle_present,
        ) == (
            aware_record.speed_kmh,
            aware_record.obstacle_distance_m,
            aware_record.visibility,
            aware_record.closing_speed_kmh,
            aware_record.hazard_severity,
            aware_record.in_predicted_path,
            aware_record.perception_confidence,
            aware_record.obstacle_present,
        )


def test_metric_calculations_use_actual_episode_counts_and_null_empty_means():
    common = {
        "episode_index": 0,
        "scenario_id": "test",
        "scenario_name": "Test",
        "policy": "baseline",
        "speed_kmh": 20,
        "obstacle_distance_m": 10,
        "visibility": 1,
        "closing_speed_kmh": 10,
        "hazard_severity": 0.5,
        "in_predicted_path": True,
        "perception_confidence": 1,
        "obstacle_present": True,
        "risk_score": 50,
        "action": "brake",
        "outcome": "safe",
        "collision": False,
        "near_miss": False,
        "unnecessary_emergency_braking": False,
        "minimum_separation_m": 5,
        "reaction_time_s": 0.8,
        "stopping_distance_m": 4.0,
    }
    records = [
        EvaluationEpisodeRecord(**common),
        EvaluationEpisodeRecord(
            **{
                **common,
                "episode_index": 1,
                "collision": True,
                "outcome": "collision",
                "near_miss": False,
                "reaction_time_s": None,
                "stopping_distance_m": None,
            }
        ),
    ]
    metrics = calculate_metrics(records)
    assert metrics.total_episodes == 2
    assert metrics.collision_rate_pct == 50
    assert metrics.near_miss_rate_pct == 0
    assert metrics.average_reaction_time_s == 0.8
    assert metrics.average_stopping_distance_m == 4
    empty = calculate_metrics([])
    assert empty.collision_rate_pct is None
    assert empty.average_reaction_time_s is None
