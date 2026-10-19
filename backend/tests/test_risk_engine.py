from backend.app.risk_engine import assess_risk


def assess(**overrides):
    values = {
        "obstacle_distance_m": 50,
        "speed_kmh": 60,
        "closing_speed_kmh": 20,
        "visibility": 1.0,
        "hazard_severity": 0.8,
        "in_predicted_path": True,
        "perception_confidence": 0.9,
        "obstacle_present": True,
    }
    values.update(overrides)
    return assess_risk(**values)


def test_risk_score_is_bounded_and_categorized():
    assert assess(obstacle_distance_m=0, closing_speed_kmh=200).risk_score <= 100
    assert assess(obstacle_distance_m=1000, closing_speed_kmh=0).risk_score >= 0
    assert assess(obstacle_distance_m=0, closing_speed_kmh=200).risk_category == "high"


def test_closer_relevant_obstacle_increases_risk():
    assert assess(obstacle_distance_m=20).risk_score > assess(obstacle_distance_m=80).risk_score


def test_higher_closing_speed_increases_risk():
    assert assess(closing_speed_kmh=70).risk_score > assess(closing_speed_kmh=5).risk_score


def test_higher_vehicle_speed_increases_relevant_hazard_risk():
    assert assess(speed_kmh=120).risk_score > assess(speed_kmh=20).risk_score


def test_poor_visibility_increases_risk():
    assert assess(visibility=0.2).risk_score > assess(visibility=1.0).risk_score


def test_uncertainty_increases_hazard_risk_without_clearing_it():
    result = assess(perception_confidence=0.1)
    assert result.risk_score > assess(perception_confidence=1.0).risk_score
    assert "hazard is in the predicted path" in result.explanation


def test_obstacle_outside_path_does_not_create_emergency_level_risk():
    result = assess(in_predicted_path=False, obstacle_distance_m=1, closing_speed_kmh=200)
    assert result.risk_score < 30
    assert result.component_scores["distance"] == 0
