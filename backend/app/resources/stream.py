"""Server-Sent Events stream fed by PostgreSQL LISTEN/NOTIFY."""

import queue
import threading
from collections.abc import Iterator
from typing import Any

from flask import Blueprint, Response, current_app, jsonify, request, stream_with_context
from flask_jwt_extended import decode_token

from ..utils.sse import listen_worker

bp = Blueprint("stream", __name__, url_prefix="/api/stream")


@bp.get("/alerts")
def stream_alerts() -> Any:
    """Stream alert notifications; the access token is passed as ``?token=``."""
    try:
        if decode_token(request.args.get("token", "")).get("type") != "access":
            raise ValueError("not an access token")
    except Exception:  # noqa: BLE001 - any decode failure means unauthorised
        return jsonify(error="invalid or missing token"), 401

    out: queue.Queue[str | None] = queue.Queue()
    stop = threading.Event()
    dsn = current_app.config["SSE_DSN"]
    threading.Thread(target=listen_worker, args=(dsn, out, stop), daemon=True).start()

    def generate() -> Iterator[str]:
        try:
            yield "retry: 3000\n\n"
            while True:
                try:
                    payload = out.get(timeout=15)
                except queue.Empty:
                    yield ": ping\n\n"
                    continue
                if payload is None:
                    return
                yield f"data: {payload}\n\n"
        finally:
            stop.set()

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
