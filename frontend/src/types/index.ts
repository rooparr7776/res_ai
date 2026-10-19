export type PolicyName = 'baseline' | 'safety_aware'
export type DrivingAction = 'continue' | 'slow_down' | 'brake' | 'stop'
export type RiskCategory = 'low' | 'medium' | 'high'
export type EpisodeOutcome = 'no_hazard' | 'safe' | 'near_miss' | 'collision'

export interface Scenario {
  id: string
  name: string
  description: string
  hazard_type: string
  default_speed_kmh: number
  default_obstacle_distance_m: number
  default_visibility: number
  default_hazard_severity: number
  default_in_predicted_path: boolean
  default_perception_confidence: number
  default_closing_speed_kmh: number
  default_obstacle_present: boolean
}

export interface SimulationRequest {
  scenario_id: string
  policy: PolicyName
  speed_kmh: number
  obstacle_distance_m: number
  visibility: number
}

export interface RiskAssessment {
  risk_score: number
  risk_category: RiskCategory
  component_scores: Record<string, number>
  explanation: string
}

export interface TimelineStep {
  time_s: number
  vehicle_position_m: number
  vehicle_speed_mps: number
  obstacle_position_m: number | null
  separation_m: number | null
  action: DrivingAction
}

export interface DecisionLogEntry {
  time_s: number
  event: string
  risk_score: number
  action: DrivingAction
  explanation: string
}

export interface SimulationResult {
  inputs: {
    scenario_id: string
    scenario_name: string
    policy: PolicyName
    speed_kmh: number
    obstacle_distance_m: number
    visibility: number
    closing_speed_kmh: number
    hazard_severity: number
    in_predicted_path: boolean
    perception_confidence: number
    obstacle_present: boolean
  }
  risk: RiskAssessment
  action: DrivingAction
  explanation: string
  decision_log: DecisionLogEntry[]
  timeline: TimelineStep[]
  outcome: EpisodeOutcome
  collision: boolean
  near_miss: boolean
  unnecessary_emergency_braking: boolean
  minimum_separation_m: number | null
  reaction_time_s: number | null
  reaction_distance_m: number | null
  stopping_distance_m: number | null
}

export interface PolicyMetrics {
  total_episodes: number
  collision_rate_pct: number | null
  near_miss_rate_pct: number | null
  unnecessary_braking_rate_pct: number | null
  average_reaction_time_s: number | null
  average_stopping_distance_m: number | null
}

export interface EpisodeRecord {
  episode_index: number
  scenario_id: string
  scenario_name: string
  policy: PolicyName
  speed_kmh: number
  obstacle_distance_m: number
  visibility: number
  closing_speed_kmh: number
  hazard_severity: number
  in_predicted_path: boolean
  perception_confidence: number
  obstacle_present: boolean
  risk_score: number
  action: DrivingAction
  outcome: EpisodeOutcome
  collision: boolean
  near_miss: boolean
  unnecessary_emergency_braking: boolean
  minimum_separation_m: number | null
  reaction_time_s: number | null
  stopping_distance_m: number | null
}

export interface EvaluationResult {
  seed: number
  episodes_per_scenario: number
  total_episodes_per_policy: number
  scenario_ids: string[]
  variation_description: string
  metric_definitions: Record<string, string>
  metrics_by_policy: Record<PolicyName, PolicyMetrics>
  per_scenario_metrics: Record<string, Record<PolicyName, PolicyMetrics>>
  episode_records: EpisodeRecord[]
}

export interface Controls {
  scenarioId: string
  speedKmh: number
  obstacleDistanceM: number
  visibility: number
  policy: PolicyName
}
