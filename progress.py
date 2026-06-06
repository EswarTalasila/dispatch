"""Shared progress state for the manual refresh, read by the API for the UI."""

import threading
from datetime import datetime

_lock = threading.Lock()
_state = {
    "running": False,
    "stage": "",
    "percent": 0,
    "message": "",
    "finished_at": None,
}


def try_start():
    """Begin a run if one isn't already going. Returns False if already running."""
    with _lock:
        if _state["running"]:
            return False
        _state.update(
            running=True, stage="Starting…", percent=2, message="", finished_at=None
        )
        return True


def update(stage=None, percent=None):
    with _lock:
        if stage is not None:
            _state["stage"] = stage
        if percent is not None:
            _state["percent"] = max(0, min(100, int(percent)))


def finish(message):
    with _lock:
        _state.update(
            running=False,
            stage="Done",
            percent=100,
            message=message,
            finished_at=datetime.now().isoformat(timespec="seconds"),
        )


def snapshot():
    with _lock:
        return dict(_state)
