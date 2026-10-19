"""Pydantic models shared by the API and simulation modules."""

from typing import Literal

from pydantic import BaseModel, Field

PolicyName = Literal["baseline", "safety_aware"]
RiskCategory = Literal["low", "medium", "high"]
DrivingAction = Literal["continue", "slow_down", "brake", "stop"]
EpisodeOutcome = Literal["no_hazard", "safe", "near_miss", "collision"]


class ScenarioDefinition(BaseModel):
    id: str
    name: str
    description: str
    hazard_type: str
    default_speed_kmh: float
    default_obstacle_distance_m: float
    default_visibility: float
    default_hazard_severity: float
    default_in_predicted_path: bool
    default_perception_confidence: float
    default_closing_speed_kmh: float
    default_obstacle_present: bool


class SimulationRequest(BaseModel):
    scenario_id: str
    policy: PolicyName = "safety_aware"
    speed_kmh: float | None = Field(default=None, gt=0, le=200)
    obstacle_distance_m: float | None = Field(default=None, ge=0, le=1000)
    visibility: float | None = Field(default=None, ge=0, le=1)
    closing_speed_kmh: float | None = Field(default=None, ge=0, le=200)
    hazard_severity: float | None = Field(default=None, ge=0, le=1)
    in_predicted_path: bool | None = None
    perception_confidence: float | None = Field(default=None, ge=0, le=1)
    obstacle_present: bool | None = None


class EvaluationRequest(BaseModel):
    scenario_ids: list[str] | None = Field(default=None, min_length=1)
    episodes_per_scenario: int = Field(default=20, ge=1, le=50)
    seed: int = 42


class SimulationInputs(BaseModel):
    scenario_id: str
    scenario_name: str
    policy: PolicyName
    speed_kmh: float
    obstacle_distance_m: float
    visibility: float = Field(ge=0, le=1)
    closing_speed_kmh: float = Field(ge=0, le=200)
    hazard_severity: float = Field(ge=0, le=1)
    in_predicted_path: bool
    perception_confidence: float = Field(ge=0, le=1)
    obstacle_present: bool


class RiskAssessment(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_category: RiskCategory
    component_scores: dict[str, float]
    explanation: str


class TimelineStep(BaseModel):
    time_s: float
    vehicle_position_m: float
    vehicle_speed_mps: float
    obstacle_position_m: float | None
    separation_m: float | None
    action: DrivingAction


class DecisionLogEntry(BaseModel):
    time_s: float
    event: str
    risk_score: int
    action: DrivingAction
    explanation: str


class SimulationResponse(BaseModel):
    inputs: SimulationInputs
    risk: RiskAssessment
    action: DrivingAction
    explanation: str
    decision_log: list[DecisionLogEntry]
    timeline: list[TimelineStep]
    outcome: EpisodeOutcome
    collision: bool
    near_miss: bool
    unnecessary_emergency_braking: bool
    minimum_separation_m: float | None
    reaction_time_s: float | None
    reaction_distance_m: float | None
    stopping_distance_m: float | None


class PolicyMetrics(BaseModel):
    total_episodes: int
    collision_rate_pct: float | None
    near_miss_rate_pct: float | None
    unnecessary_braking_rate_pct: float | None
    average_reaction_time_s: float | None
    average_stopping_distance_m: float | None


class EvaluationEpisodeRecord(BaseModel):
    episode_index: int
    scenario_id: str
    scenario_name: str
    policy: PolicyName
    speed_kmh: float
    obstacle_distance_m: float
    visibility: float
    closing_speed_kmh: float
    hazard_severity: float
    in_predicted_path: bool
    perception_confidence: float
    obstacle_present: bool
    risk_score: int
    action: DrivingAction
    outcome: EpisodeOutcome
    collision: bool
    near_miss: bool
    unnecessary_emergency_braking: bool
    minimum_separation_m: float | None
    reaction_time_s: float | None
    stopping_distance_m: float | None


class EvaluationResponse(BaseModel):
    seed: int
    episodes_per_scenario: int
    total_episodes_per_policy: int
    scenario_ids: list[str]
    variation_description: str
    metric_definitions: dict[str, str]
    metrics_by_policy: dict[PolicyName, PolicyMetrics]
    per_scenario_metrics: dict[str, dict[PolicyName, PolicyMetrics]]
    episode_records: list[EvaluationEpisodeRecord]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
