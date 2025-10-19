from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field

from ..services.llm_agent import run_agent_workflow
from ..services.ws_logger import send_ws_log


router = APIRouter()


class QueryPayload(BaseModel):
    type: str = Field(..., description="Type of analysis: url|text|image|video")
    payload: Dict[str, Any] = Field(..., description="Payload to analyze")


@router.post("/query")
async def query(payload: QueryPayload, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Accepts an analysis request and runs the full AI verification workflow.
    
    Returns actual analysis results from Gemini AI, sentiment analysis, and evidence.
    """
    import time
    request_start = time.time()
    
    print(f"\n{'#'*80}")
    print(f"📥 [API REQUEST] Received query - Type: {payload.type}")
    print(f"📦 [API REQUEST] Payload: {payload.payload}")
    print(f"{'#'*80}")
    # Broadcast start to UI
    try:
        await send_ws_log("INFO", "Received query", {"type": payload.type, "payload_preview": str(payload.payload)[:200]})
    except Exception:
        pass
    
    # Run the full agent workflow synchronously to return real results
    result = await run_agent_workflow(payload.type, payload.payload)
    
    request_end = time.time()
    print(f"\n{'#'*80}")
    print(f"📤 [API RESPONSE] Returning result - Total API time: {request_end - request_start:.2f}s")
    print(f"{'#'*80}\n")
    # Broadcast completion to UI
    try:
        await send_ws_log("INFO", "Returning analysis result", {"type": payload.type, "duration_s": round(request_end - request_start, 2), "verdict": result.get("verdict")})
    except Exception:
        pass
    
    return result


