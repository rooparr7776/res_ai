"""Transparent, illustrative rule-based risk scoring."""

from .schemas import RiskAssessment


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return min(max(value, lower), upper)


def risk_category(score: int) -> str:
    if score < 30:
        return "low"
    if score < 60:
        return "medium"
    return "high"


def assess_risk(
    *,
    obstacle_distance_m: float,
    speed_kmh: float,
    closing_speed_kmh: float,
    visibility: float,
    hazard_severity: float,
    in_predicted_path: bool,
    perception_confidence: float,
    obstacle_present: bool,
) -> RiskAssessment:
    """Calculate an experimental score:

    35*distance pressure + 10*vehicle-speed pressure + 25*closing-speed pressure
    + 20*severity + 7*visibility loss + 3*perception uncertainty.
    Each pressure is normalized to [0, 1]; the weights sum to 100.
    """
    obstacle_distance_m = max(0.0, obstacle_distance_m)
    speed_kmh = max(0.0, speed_kmh)
    closing_speed_kmh = max(0.0, closing_speed_kmh)
    visibility = _clamp(visibility)
    hazard_severity = _clamp(hazard_severity)
    perception_confidence = _clamp(perception_confidence)
    relevant_hazard = obstacle_present and in_predicted_path
    visibility_penalty = (1.0 - visibility) * 7.0

    if relevant_hazard:
        distance_pressure = _clamp(1.0 - obstacle_distance_m / 100.0)
        vehicle_speed_pressure = _clamp((speed_kmh / 3.6) / 30.0)
        closing_pressure = _clamp((closing_speed_kmh / 3.6) / 20.0)
        uncertainty_pressure = 1.0 - perception_confidence
        components = {
            "distance": 35.0 * distance_pressure,
            "vehicle_speed": 10.0 * vehicle_speed_pressure,
            "closing_speed": 25.0 * closing_pressure,
            "hazard_severity": 20.0 * hazard_severity,
            "visibility": visibility_penalty,
            "perception_uncertainty": 3.0 * uncertainty_pressure,
        }
    else:
        # Uncertainty only adds caution when there is an object to assess.
        uncertainty_penalty = 5.0 * (1.0 - perception_confidence) if obstacle_present else 0.0
        components = {
            "distance": 0.0,
            "vehicle_speed": 0.0,
            "closing_speed": 0.0,
            "hazard_severity": 0.0,
            "visibility": visibility_penalty,
            "perception_uncertainty": uncertainty_penalty * 0.6,
        }

    score = round(_clamp(sum(components.values()), 0.0, 100.0))
    if relevant_hazard:
        explanation = (
            "A hazard is in the predicted path; the score combines distance, closing speed, "
            "severity, visibility, and perception uncertainty."
        )
    elif obstacle_present:
        explanation = (
            "The detected object is outside the predicted path; it does not add distance, "
            "closing-speed, or severity risk. Visibility and uncertainty still add caution."
        )
    else:
        explanation = (
            "No obstacle is present in the scenario; only reduced visibility contributes "
            "background caution."
        )

    return RiskAssessment(
        risk_score=score,
        risk_category=risk_category(score),
        component_scores={key: round(value, 2) for key, value in components.items()},
        explanation=explanation,
    )
