"""Deterministic, simplified one-dimensional kinematic episode simulation."""

from .driving_policy import POLICY_PARAMETERS, choose_action
from .risk_engine import assess_risk
from .schemas import (
    DecisionLogEntry,
    SimulationInputs,
    SimulationResponse,
    TimelineStep,
)

TIME_STEP_S = 0.1
MAX_SIMULATION_TIME_S = 20.0
COLLISION_THRESHOLD_M = 0.0
NEAR_MISS_THRESHOLD_M = 3.0
ACTION_DECELERATION_MPS2 = {
    "baseline": {"continue": 0.0, "slow_down": 1.5, "brake": 3.5, "stop": 6.0},
    "safety_aware": {"continue": 0.0, "slow_down": 2.0, "brake": 5.0, "stop": 7.0},
}


def simulate(inputs: SimulationInputs) -> SimulationResponse:
    speed_mps = inputs.speed_kmh / 3.6
    risk = assess_risk(
        obstacle_distance_m=inputs.obstacle_distance_m,
        speed_kmh=inputs.speed_kmh,
        closing_speed_kmh=inputs.closing_speed_kmh,
        visibility=inputs.visibility,
        hazard_severity=inputs.hazard_severity,
        in_predicted_path=inputs.in_predicted_path,
        perception_confidence=inputs.perception_confidence,
        obstacle_present=inputs.obstacle_present,
    )
    action, explanation = choose_action(
        policy=inputs.policy,
        risk=risk,
        speed_kmh=inputs.speed_kmh,
        obstacle_distance_m=inputs.obstacle_distance_m,
        visibility=inputs.visibility,
        obstacle_present=inputs.obstacle_present,
        in_predicted_path=inputs.in_predicted_path,
    )
    relevant_hazard = inputs.obstacle_present and inputs.in_predicted_path
    reaction_delay = POLICY_PARAMETERS[inputs.policy].reaction_delay_s
    deceleration = ACTION_DECELERATION_MPS2[inputs.policy][action]
    obstacle_velocity_mps = speed_mps - inputs.closing_speed_kmh / 3.6

    vehicle_position = 0.0
    obstacle_position = inputs.obstacle_distance_m
    current_speed = speed_mps
    minimum_separation: float | None = inputs.obstacle_distance_m if relevant_hazard else None
    timeline: list[TimelineStep] = [
        TimelineStep(
            time_s=0.0,
            vehicle_position_m=0.0,
            vehicle_speed_mps=round(current_speed, 3),
            obstacle_position_m=round(obstacle_position, 3) if relevant_hazard else None,
            separation_m=round(obstacle_position, 3) if relevant_hazard else None,
            action=action,
        )
    ]
    collision = relevant_hazard and obstacle_position <= COLLISION_THRESHOLD_M
    stopped_at_s: float | None = 0.0 if current_speed <= 0.05 else None
    brake_start_position_m: float | None = None
    if deceleration > 0 and reaction_delay == 0:
        brake_start_position_m = vehicle_position

    step_count = int(MAX_SIMULATION_TIME_S / TIME_STEP_S)
    for step in range(1, step_count + 1):
        if collision or stopped_at_s is not None:
            break
        time_s = step * TIME_STEP_S
        active_deceleration = deceleration if time_s >= reaction_delay else 0.0
        if active_deceleration > 0 and brake_start_position_m is None:
            brake_start_position_m = vehicle_position

        distance_this_step = current_speed * TIME_STEP_S - (
            0.5 * active_deceleration * TIME_STEP_S**2
        )
        distance_this_step = max(0.0, distance_this_step)
        vehicle_position += distance_this_step
        current_speed = max(0.0, current_speed - active_deceleration * TIME_STEP_S)
        if relevant_hazard:
            obstacle_position += obstacle_velocity_mps * TIME_STEP_S
            separation = obstacle_position - vehicle_position
            minimum_separation = (
                separation
                if minimum_separation is None
                else min(minimum_separation, separation)
            )
            if separation <= COLLISION_THRESHOLD_M:
                collision = True

        timeline.append(
            TimelineStep(
                time_s=round(time_s, 2),
                vehicle_position_m=round(vehicle_position, 3),
                vehicle_speed_mps=round(current_speed, 3),
                obstacle_position_m=round(obstacle_position, 3) if relevant_hazard else None,
                separation_m=round(obstacle_position - vehicle_position, 3)
                if relevant_hazard
                else None,
                action=action,
            )
        )
        if current_speed <= 0.05:
            current_speed = 0.0
            stopped_at_s = time_s
            timeline[-1] = timeline[-1].model_copy(update={"vehicle_speed_mps": 0.0})

    near_miss = (
        relevant_hazard
        and not collision
        and minimum_separation is not None
        and COLLISION_THRESHOLD_M < minimum_separation <= NEAR_MISS_THRESHOLD_M
    )
    outcome = (
        "collision"
        if collision
        else "near_miss"
        if near_miss
        else "safe"
        if relevant_hazard
        else "no_hazard"
    )
    reaction_time = (
        reaction_delay
        if relevant_hazard and action in ("slow_down", "brake", "stop")
        else None
    )
    reaction_distance = (
        round(speed_mps * reaction_delay, 3) if reaction_time is not None else None
    )
    stopping_distance = (
        round(max(0.0, vehicle_position - (brake_start_position_m or 0.0)), 3)
        if stopped_at_s is not None and deceleration > 0
        else None
    )
    unnecessary_emergency_braking = (
        action == "stop" and not relevant_hazard
    )

    decision_log = [
        DecisionLogEntry(
            time_s=0.0,
            event="decision",
            risk_score=risk.risk_score,
            action=action,
            explanation=explanation,
        ),
        DecisionLogEntry(
            time_s=round(timeline[-1].time_s, 2),
            event="episode_complete",
            risk_score=risk.risk_score,
            action=action,
            explanation=(
                f"Episode outcome: {outcome}; minimum separation: "
                f"{minimum_separation:.2f} m."
                if minimum_separation is not None
                else f"Episode outcome: {outcome}; no relevant obstacle was simulated."
            ),
        ),
    ]

    return SimulationResponse(
        inputs=inputs,
        risk=risk,
        action=action,
        explanation=explanation,
        decision_log=decision_log,
        timeline=timeline,
        outcome=outcome,
        collision=collision,
        near_miss=near_miss,
        unnecessary_emergency_braking=unnecessary_emergency_braking,
        minimum_separation_m=round(minimum_separation, 3)
        if minimum_separation is not None
        else None,
        reaction_time_s=reaction_time,
        reaction_distance_m=reaction_distance,
        stopping_distance_m=stopping_distance,
    )
