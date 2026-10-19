"""Reproducible paired-policy experiments and metric aggregation."""

import random
from collections.abc import Sequence

from .scenarios import SCENARIOS, get_scenario
from .schemas import (
    EvaluationEpisodeRecord,
    EvaluationRequest,
    EvaluationResponse,
    PolicyMetrics,
    PolicyName,
    SimulationInputs,
)
from .simulation import simulate

POLICIES: tuple[PolicyName, ...] = ("baseline", "safety_aware")
METRIC_DEFINITIONS = {
    "collision_rate_pct": "Colliding episodes divided by all episodes, multiplied by 100.",
    "near_miss_rate_pct": (
        "Episodes with minimum separation greater than 0 m and at most 3 m, "
        "without a collision, divided by all episodes, multiplied by 100."
    ),
    "unnecessary_braking_rate_pct": (
        "Episodes in which the policy commanded an emergency stop despite no relevant "
        "in-path obstacle, divided by all episodes, multiplied by 100."
    ),
    "average_reaction_time_s": (
        "Mean policy reaction delay for episodes with a relevant hazard and a "
        "slow-down, brake, or stop response; null when there are no such responses."
    ),
    "average_stopping_distance_m": (
        "Mean distance traveled after braking begins in episodes where the vehicle "
        "actually stops; null when no episode stops."
    ),
}


def calculate_metrics(records: Sequence[EvaluationEpisodeRecord]) -> PolicyMetrics:
    total = len(records)
    if total == 0:
        return PolicyMetrics(
            total_episodes=0,
            collision_rate_pct=None,
            near_miss_rate_pct=None,
            unnecessary_braking_rate_pct=None,
            average_reaction_time_s=None,
            average_stopping_distance_m=None,
        )
    reaction_times = [
        record.reaction_time_s for record in records if record.reaction_time_s is not None
    ]
    stopping_distances = [
        record.stopping_distance_m
        for record in records
        if record.stopping_distance_m is not None
    ]
    return PolicyMetrics(
        total_episodes=total,
        collision_rate_pct=round(100.0 * sum(record.collision for record in records) / total, 2),
        near_miss_rate_pct=round(100.0 * sum(record.near_miss for record in records) / total, 2),
        unnecessary_braking_rate_pct=round(
            100.0
            * sum(record.unnecessary_emergency_braking for record in records)
            / total,
            2,
        ),
        average_reaction_time_s=round(sum(reaction_times) / len(reaction_times), 3)
        if reaction_times
        else None,
        average_stopping_distance_m=round(
            sum(stopping_distances) / len(stopping_distances), 3
        )
        if stopping_distances
        else None,
    )


def _bounded(value: float, lower: float, upper: float) -> float:
    return min(max(value, lower), upper)


def _make_inputs(
    scenario_id: str,
    scenario_name: str,
    policy: PolicyName,
    values: dict[str, object],
) -> SimulationInputs:
    return SimulationInputs(
        scenario_id=scenario_id,
        scenario_name=scenario_name,
        policy=policy,
        **values,
    )


def run_evaluation(request: EvaluationRequest) -> EvaluationResponse:
    selected_ids = request.scenario_ids or [scenario.id for scenario in SCENARIOS]
    scenarios = []
    for scenario_id in selected_ids:
        scenario = get_scenario(scenario_id)
        if scenario is None:
            raise ValueError(f"Unknown scenario ID: {scenario_id}")
        scenarios.append(scenario)

    rng = random.Random(request.seed)
    records: list[EvaluationEpisodeRecord] = []
    for scenario in scenarios:
        for episode_index in range(request.episodes_per_scenario):
            shared_values: dict[str, object] = {
                "speed_kmh": round(
                    _bounded(
                        scenario.default_speed_kmh * rng.uniform(0.9, 1.1),
                        1.0,
                        200.0,
                    ),
                    2,
                ),
                "obstacle_distance_m": round(
                    _bounded(
                        scenario.default_obstacle_distance_m * rng.uniform(0.85, 1.15),
                        0.0,
                        1000.0,
                    ),
                    2,
                ),
                "visibility": round(
                    _bounded(scenario.default_visibility + rng.uniform(-0.1, 0.1), 0.0, 1.0),
                    3,
                ),
                "closing_speed_kmh": round(
                    _bounded(
                        scenario.default_closing_speed_kmh + rng.uniform(-5.0, 5.0),
                        0.0,
                        200.0,
                    ),
                    2,
                ),
                "hazard_severity": scenario.default_hazard_severity,
                "in_predicted_path": scenario.default_in_predicted_path,
                "perception_confidence": round(
                    _bounded(
                        scenario.default_perception_confidence + rng.uniform(-0.08, 0.08),
                        0.0,
                        1.0,
                    ),
                    3,
                ),
                "obstacle_present": scenario.default_obstacle_present,
            }

            for policy in POLICIES:
                simulation = simulate(
                    _make_inputs(scenario.id, scenario.name, policy, shared_values)
                )
                records.append(
                    EvaluationEpisodeRecord(
                        episode_index=episode_index,
                        scenario_id=scenario.id,
                        scenario_name=scenario.name,
                        policy=policy,
                        speed_kmh=simulation.inputs.speed_kmh,
                        obstacle_distance_m=simulation.inputs.obstacle_distance_m,
                        visibility=simulation.inputs.visibility,
                        closing_speed_kmh=simulation.inputs.closing_speed_kmh,
                        hazard_severity=simulation.inputs.hazard_severity,
                        in_predicted_path=simulation.inputs.in_predicted_path,
                        perception_confidence=simulation.inputs.perception_confidence,
                        obstacle_present=simulation.inputs.obstacle_present,
                        risk_score=simulation.risk.risk_score,
                        action=simulation.action,
                        outcome=simulation.outcome,
                        collision=simulation.collision,
                        near_miss=simulation.near_miss,
                        unnecessary_emergency_braking=(
                            simulation.unnecessary_emergency_braking
                        ),
                        minimum_separation_m=simulation.minimum_separation_m,
                        reaction_time_s=simulation.reaction_time_s,
                        stopping_distance_m=simulation.stopping_distance_m,
                    )
                )

    by_policy = {
        policy: calculate_metrics([record for record in records if record.policy == policy])
        for policy in POLICIES
    }
    per_scenario = {
        scenario.id: {
            policy: calculate_metrics(
                [
                    record
                    for record in records
                    if record.scenario_id == scenario.id and record.policy == policy
                ]
            )
            for policy in POLICIES
        }
        for scenario in scenarios
    }
    return EvaluationResponse(
        seed=request.seed,
        episodes_per_scenario=request.episodes_per_scenario,
        total_episodes_per_policy=request.episodes_per_scenario * len(scenarios),
        scenario_ids=[scenario.id for scenario in scenarios],
        variation_description=(
            "Each episode uses seeded, bounded variations in speed, obstacle distance, "
            "visibility, closing speed, and perception confidence. Both policies receive "
            "the exact same generated inputs for each scenario and episode."
        ),
        metric_definitions=METRIC_DEFINITIONS,
        metrics_by_policy=by_policy,
        per_scenario_metrics=per_scenario,
        episode_records=records,
    )
