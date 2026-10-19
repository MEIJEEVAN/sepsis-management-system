"""Background LISTEN worker that feeds PostgreSQL notifications into a queue."""

import queue
import threading

import psycopg


def listen_worker(dsn: str, out: "queue.Queue[str | None]", stop: threading.Event) -> None:
    """LISTEN on ``alerts_channel`` and push each payload onto ``out``.

    A ``None`` item is queued if the connection fails so the SSE generator can end.
    """
    try:
        with psycopg.connect(dsn, autocommit=True, application_name="sepsis_sse") as conn:
            conn.execute("LISTEN alerts_channel")
            while not stop.is_set():
                for note in conn.notifies(timeout=1.0):
                    out.put(note.payload)
    except psycopg.Error:
        out.put(None)
