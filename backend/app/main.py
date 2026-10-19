"""FastAPI application for DriveGuard AI."""

import csv
import io

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .evaluation import run_evaluation
from .scenarios import SCENARIOS, get_scenario
from .schemas import (
    EvaluationRequest,
    EvaluationResponse,
    HealthResponse,
    ScenarioDefinition,
    SimulationInputs,
    SimulationRequest,
    SimulationResponse,
)
from .simulation import simulate

app = FastAPI(
    title="DriveGuard AI API",
    description=(
        "Educational rule-based autonomous-driving simulation. It is not validated "
        "for real-world driving or a reproduction of Tesla Autopilot."
    ),
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
_latest_evaluation: EvaluationResponse | None = None


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "DriveGuard AI API",
        "status": "ok",
        "docs": "/docs",
        "health": "/api/health",
        "scenarios": "/api/scenarios",
    }


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="DriveGuard AI API")


@app.get("/api/scenarios", response_model=list[ScenarioDefinition])
def scenarios() -> list[ScenarioDefinition]:
    return list(SCENARIOS)


def _resolve_inputs(request: SimulationRequest) -> SimulationInputs:
    scenario = get_scenario(request.scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"Unknown scenario ID: {request.scenario_id}")
    return SimulationInputs(
        scenario_id=scenario.id,
        scenario_name=scenario.name,
        policy=request.policy,
        speed_kmh=request.speed_kmh
        if request.speed_kmh is not None
        else scenario.default_speed_kmh,
        obstacle_distance_m=request.obstacle_distance_m
        if request.obstacle_distance_m is not None
        else scenario.default_obstacle_distance_m,
        visibility=request.visibility
        if request.visibility is not None
        else scenario.default_visibility,
        closing_speed_kmh=request.closing_speed_kmh
        if request.closing_speed_kmh is not None
        else scenario.default_closing_speed_kmh,
        hazard_severity=request.hazard_severity
        if request.hazard_severity is not None
        else scenario.default_hazard_severity,
        in_predicted_path=request.in_predicted_path
        if request.in_predicted_path is not None
        else scenario.default_in_predicted_path,
        perception_confidence=request.perception_confidence
        if request.perception_confidence is not None
        else scenario.default_perception_confidence,
        obstacle_present=request.obstacle_present
        if request.obstacle_present is not None
        else scenario.default_obstacle_present,
    )


@app.post("/api/simulate", response_model=SimulationResponse)
def simulate_episode(request: SimulationRequest) -> SimulationResponse:
    return simulate(_resolve_inputs(request))


@app.post("/api/evaluate", response_model=EvaluationResponse)
def evaluate(request: EvaluationRequest) -> EvaluationResponse:
    global _latest_evaluation
    try:
        result = run_evaluation(request)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    _latest_evaluation = result
    return result


@app.get("/api/results/export")
def export_results() -> StreamingResponse:
    if _latest_evaluation is None:
        raise HTTPException(
            status_code=404,
            detail="No evaluation results are available; run /api/evaluate first.",
        )
    output = io.StringIO(newline="")
    fieldnames = list(_latest_evaluation.episode_records[0].model_dump().keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for record in _latest_evaluation.episode_records:
        writer.writerow(record.model_dump())
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="driveguard-evaluation.csv"'},
    )
