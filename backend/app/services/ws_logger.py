import json
import time
from typing import Any, Dict


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


async def send_ws_log(level: str, message: str, extra: Dict[str, Any] | None = None) -> None:
    """Print a log line and broadcast it to connected WebSocket clients.

    level: INFO, DEBUG, WARN, ERROR
    message: short message
    extra: optional dict with extra fields
    """
    log = {
        "ts": _now(),
        "level": level,
        "message": message,
    }
    if extra:
        log.update(extra)

    # Print to console for server-side visibility
    print(f"[{log['ts']}] {level}: {message}", json.dumps(extra) if extra else "")

    # Broadcast via WebSocket manager if available
    try:
        # Lazy import to avoid circular dependency
        from app.main import get_ws_manager
        manager = get_ws_manager()
        await manager.broadcast({"type": "log", "payload": log})
    except Exception:
        # Non-fatal: just continue if WS not available
        pass
