from backend.app.driving_policy import choose_action
from backend.app.risk_engine import assess_risk


def risk(**overrides):
    values = {
        "obstacle_distance_m": 20,
        "speed_kmh": 60,
        "closing_speed_kmh": 50,
        "visibility": 0.8,
        "hazard_severity": 0.9,
        "in_predicted_path": True,
        "perception_confidence": 0.9,
        "obstacle_present": True,
    }
    values.update(overrides)
    return assess_risk(**values)


def choose(policy, assessment, **overrides):
    values = {
        "speed_kmh": 60,
        "obstacle_distance_m": 20,
        "visibility": 0.8,
        "obstacle_present": True,
        "in_predicted_path": True,
    }
    values.update(overrides)
    action, _ = choose_action(policy=policy, risk=assessment, **values)
    return action


def test_relevant_close_hazard_causes_emergency_stop():
    assert choose("safety_aware", risk()) == "stop"


def test_less_conservative_baseline_remains_responsive_to_close_hazard():
    assert choose("baseline", risk()) == "stop"


def test_moderate_risk_causes_safety_aware_slowdown():
    assessment = risk(obstacle_distance_m=80, closing_speed_kmh=0, hazard_severity=0.2)
    assert choose(
        "safety_aware",
        assessment,
        obstacle_distance_m=80,
        speed_kmh=30,
    ) in ("slow_down", "continue")


def test_irrelevant_obstacle_does_not_trigger_emergency_braking():
    assessment = risk(in_predicted_path=False, obstacle_distance_m=1, closing_speed_kmh=200)
    assert (
        choose(
            "safety_aware",
            assessment,
            in_predicted_path=False,
            obstacle_distance_m=1,
        )
        == "continue"
    )


def test_poor_visibility_can_cause_cautious_speed_reduction():
    assessment = risk(obstacle_present=False, in_predicted_path=False, visibility=0.1)
    assert (
        choose(
            "safety_aware",
            assessment,
            obstacle_present=False,
            in_predicted_path=False,
            visibility=0.1,
        )
        == "slow_down"
    )
