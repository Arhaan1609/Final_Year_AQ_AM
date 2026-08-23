"""
api/routers/copilot_routes.py — REST endpoints for LLM AI Copilot and Vehicle Diagnostics.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from api.services.copilot_service import explain_vehicle_performance, chat_copilot

router = APIRouter(prefix="/copilot", tags=["AI Copilot & Vehicle Diagnostics (GPT-OSS 120B)"])


class ExplainVehicleRequest(BaseModel):
    vehicle_id: str = Field(..., example="DL1LAP5083")
    telemetry: Dict[str, Any] = Field(default_factory=dict)
    predictions: Dict[str, Any] = Field(default_factory=dict)
    force_refresh: bool = Field(default=False)


class ChatCopilotRequest(BaseModel):
    message: str = Field(..., example="Why is DL1LAP5083 in critical hold?")
    history: List[Dict[str, Any]] = Field(default_factory=list)
    active_vehicle: Optional[Dict[str, Any]] = None
    active_predictions: Optional[Dict[str, Any]] = None


@router.post("/explain-vehicle", summary="Generate Structured AI Performance & Root Cause Breakdown")
def explain_vehicle_endpoint(req: ExplainVehicleRequest):
    """
    Generates a structured 3-part diagnostic for a vehicle:
      - Executive summary of performance
      - Why it is performing this way (electro-thermal, aging, driver strain)
      - Specific root-cause factors and prescriptive action directives
    Powered by GPT-OSS 120B with high-speed caching and fallback.
    """
    try:
        return explain_vehicle_performance(
            vehicle_id=req.vehicle_id,
            telemetry=req.telemetry,
            predictions=req.predictions,
            force_refresh=req.force_refresh
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnostic generation error: {str(e)}")


@router.post("/chat", summary="Interactive Fleet Copilot Chat")
def chat_copilot_endpoint(req: ChatCopilotRequest):
    """
    Interactive conversational assistant for fleet operators, dispatchers, and engineers.
    Incorporate active vehicle telemetry and multi-zone battery models into answers.
    """
    try:
        return chat_copilot(
            message=req.message,
            history=req.history,
            active_vehicle=req.active_vehicle,
            active_predictions=req.active_predictions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copilot chat error: {str(e)}")
