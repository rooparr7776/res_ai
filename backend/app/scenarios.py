"""Built-in deterministic scenarios for the educational simulator."""

from .schemas import ScenarioDefinition

SCENARIOS: tuple[ScenarioDefinition, ...] = (
    ScenarioDefinition(
        id="clear_road",
        name="Clear road",
        description="No obstacle is present in the vehicle's predicted path.",
        hazard_type="none",
        default_speed_kmh=60,
        default_obstacle_distance_m=120,
        default_visibility=1.0,
        default_hazard_severity=0.0,
        default_in_predicted_path=False,
        default_perception_confidence=0.99,
        default_closing_speed_kmh=0,
        default_obstacle_present=False,
    ),
    ScenarioDefinition(
        id="pedestrian_crossing",
        name="Pedestrian crossing",
        description="A pedestrian is crossing ahead within the predicted path.",
        hazard_type="pedestrian",
        default_speed_kmh=40,
        default_obstacle_distance_m=35,
        default_visibility=0.9,
        default_hazard_severity=0.9,
        default_in_predicted_path=True,
        default_perception_confidence=0.9,
        default_closing_speed_kmh=40,
        default_obstacle_present=True,
    ),
    ScenarioDefinition(
        id="sudden_braking",
        name="Sudden braking by vehicle ahead",
        description="A lead vehicle brakes, creating a closing-speed hazard.",
        hazard_type="vehicle",
        default_speed_kmh=80,
        default_obstacle_distance_m=55,
        default_visibility=0.95,
        default_hazard_severity=0.85,
        default_in_predicted_path=True,
        default_perception_confidence=0.95,
        default_closing_speed_kmh=35,
        default_obstacle_present=True,
    ),
    ScenarioDefinition(
        id="poor_visibility",
        name="Poor visibility",
        description="A road hazard is harder to perceive because of poor visibility.",
        hazard_type="road_hazard",
        default_speed_kmh=60,
        default_obstacle_distance_m=70,
        default_visibility=0.25,
        default_hazard_severity=0.55,
        default_in_predicted_path=True,
        default_perception_confidence=0.65,
        default_closing_speed_kmh=60,
        default_obstacle_present=True,
    ),
    ScenarioDefinition(
        id="partially_obscured",
        name="Partially obscured obstacle",
        description="An obstacle is partly hidden and has low perception confidence.",
        hazard_type="obscured_obstacle",
        default_speed_kmh=50,
        default_obstacle_distance_m=40,
        default_visibility=0.65,
        default_hazard_severity=0.75,
        default_in_predicted_path=True,
        default_perception_confidence=0.45,
        default_closing_speed_kmh=50,
        default_obstacle_present=True,
    ),
)


def get_scenario(scenario_id: str) -> ScenarioDefinition | None:
    """Return a scenario by its stable ID."""
    return next((scenario for scenario in SCENARIOS if scenario.id == scenario_id), None)
