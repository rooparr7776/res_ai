"""Baseline and safety-aware decision rules."""

from dataclasses import dataclass

from .schemas import DrivingAction, PolicyName, RiskAssessment


@dataclass(frozen=True)
class PolicyParameters:
    reaction_delay_s: float
    brake_deceleration_mps2: float
    slow_deceleration_mps2: float
    brake_risk_threshold: int
    slow_risk_threshold: int
    low_visibility_threshold: float


POLICY_PARAMETERS: dict[PolicyName, PolicyParameters] = {
    "baseline": PolicyParameters(
        reaction_delay_s=0.8,
        brake_deceleration_mps2=3.5,
        slow_deceleration_mps2=2.5,
        brake_risk_threshold=60,
        slow_risk_threshold=40,
        low_visibility_threshold=0.15,
    ),
    "safety_aware": PolicyParameters(
        reaction_delay_s=0.4,
        brake_deceleration_mps2=5.0,
        slow_deceleration_mps2=2.0,
        brake_risk_threshold=55,
        slow_risk_threshold=30,
        low_visibility_threshold=0.25,
    ),
}


def required_stopping_distance_m(
    speed_mps: float, reaction_delay_s: float, deceleration_mps2: float
) -> float:
    """Include distance traveled during reaction and idealized braking distance."""
    if speed_mps <= 0:
        return 0.0
    return speed_mps * reaction_delay_s + speed_mps**2 / (2.0 * deceleration_mps2)


def choose_action(
    *,
    policy: PolicyName,
    risk: RiskAssessment,
    speed_kmh: float,
    obstacle_distance_m: float,
    visibility: float,
    obstacle_present: bool,
    in_predicted_path: bool,
) -> tuple[DrivingAction, str]:
    parameters = POLICY_PARAMETERS[policy]
    relevant_hazard = obstacle_present and in_predicted_path
    speed_mps = speed_kmh / 3.6

    if relevant_hazard:
        emergency_distance = required_stopping_distance_m(
            speed_mps,
            parameters.reaction_delay_s,
            parameters.brake_deceleration_mps2,
        )
        if obstacle_distance_m <= emergency_distance + 2.0:
            return (
                "stop",
                f"The relevant hazard is within the estimated stopping envelope "
                f"({emergency_distance:.1f} m plus a 2 m margin), so the policy commands "
                "an emergency stop.",
            )
        mild_deceleration_distance = required_stopping_distance_m(
            speed_mps,
            parameters.reaction_delay_s,
            parameters.slow_deceleration_mps2,
        )
        if obstacle_distance_m <= mild_deceleration_distance + 5.0:
            return (
                "brake",
                "The hazard is closer than the mild-deceleration stopping envelope, "
                "so the policy applies controlled braking.",
            )
        if risk.risk_score >= parameters.brake_risk_threshold:
            return "brake", "Elevated risk for a relevant hazard calls for controlled braking."
        if risk.risk_score >= parameters.slow_risk_threshold:
            return "slow_down", "Moderate risk calls for reducing speed while monitoring the hazard."
        return "continue", "Risk is below this policy's intervention thresholds."

    if visibility <= parameters.low_visibility_threshold:
        return "slow_down", "Very poor visibility calls for a cautious speed reduction."
    if obstacle_present and not in_predicted_path:
        return "continue", "The object is outside the predicted path; emergency braking is not warranted."
    return "continue", "No relevant hazard requires an intervention."
