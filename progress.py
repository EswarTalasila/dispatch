"""Shared progress state for the manual refresh, read by the API for the UI."""

import threading
from datetime import datetime


class Cancelled(Exception):
    """Raised at a checkpoint when the user cancels a running job."""


_lock = threading.Lock()
_state = {
    "running": False,
    "stage": "",
    "percent": 0,
    "message": "",
    "finished_at": None,
    "cancel": False,
}


def try_start():
    """Begin a run if one isn't already going. Returns False if already running."""
    with _lock:
        if _state["running"]:
            return False
        _state.update(
            running=True, stage="Starting…", percent=2, message="",
            finished_at=None, cancel=False,
        )
        return True


def update(stage=None, percent=None):
    with _lock:
        if stage is not None:
            _state["stage"] = stage
        if percent is not None:
            _state["percent"] = max(0, min(100, int(percent)))


def request_cancel():
    """Ask a running job to stop at its next checkpoint. False if nothing's running."""
    with _lock:
        if not _state["running"]:
            return False
        _state["cancel"] = True
        _state["stage"] = "Cancelling…"
        return True


def cancelled():
    with _lock:
        return _state["cancel"]


def raise_if_cancelled():
    """Pipeline checkpoints call this to bail out early when cancelled."""
    if cancelled():
        raise Cancelled()


def finish(message):
    with _lock:
        _state.update(
            running=False,
            stage="Done",
            percent=100,
            message=message,
            finished_at=datetime.now().isoformat(timespec="seconds"),
            cancel=False,
        )


def snapshot():
    with _lock:
        return dict(_state)
