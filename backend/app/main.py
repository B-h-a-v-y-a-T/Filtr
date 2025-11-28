import asyncio
import json
import logging
from typing import Any, Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables early (root .env and backend/.env if present)
load_dotenv()  # project root .env
backend_env = Path(__file__).resolve().parents[1] / ".env"
if backend_env.exists():
    load_dotenv(backend_env)

from .routers.analysis import router as analysis_router
from .services.db import init_db


logger = logging.getLogger(__name__)


class ConnectionManager:
    """Tracks active WebSocket connections and provides broadcast helpers."""

    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        if not self.active_connections:
            return
        data = json.dumps(message)
        send_tasks = []
        for connection in list(self.active_connections):
            send_tasks.append(self._safe_send(connection, data))
        await asyncio.gather(*send_tasks, return_exceptions=True)

    async def _safe_send(self, websocket: WebSocket, data: str) -> None:
        try:
            await websocket.send_text(data)
        except Exception:
            # Drop bad connection silently
            self.disconnect(websocket)



# (Already loaded above)

manager = ConnectionManager()

app = FastAPI(title="Aletheia Sentinel Backend", version="0.1.0")

# CORS: allow all for prototype; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(analysis_router, prefix="/api/v1", tags=["analysis"])


@app.websocket("/ws/threats")
async def websocket_threats(websocket: WebSocket) -> None:
    """Simple WebSocket pushing demo threat alerts periodically."""
    await manager.connect(websocket)
    logger.info("WebSocket connected: %s", getattr(websocket, "client", None))
    try:
        await websocket.send_text(
            json.dumps(
                {
                    "type": "system",
                    "message": "WebSocket heartbeat established",
                }
            )
        )
        # Keep the connection alive and send periodic pings
        while True:
            await asyncio.sleep(15)
            await manager.broadcast(
                {
                    "type": "threat",
                    "level": "L3",
                    "message": "Rising sentiment anomaly detected",
                }
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected: %s", getattr(websocket, "client", None))


# Optional: mount a static dir if present
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


# Expose manager to other modules
def get_ws_manager() -> ConnectionManager:
    return manager


@app.on_event("startup")
async def on_startup() -> None:
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Run sandbox tests if enabled
    from .services.analysis_engine import SANDBOX_MODE, run_sandbox_tests
    if SANDBOX_MODE:
        logger.info("SANDBOX_MODE enabled - running stress tests on startup")
        asyncio.create_task(run_sandbox_tests())


