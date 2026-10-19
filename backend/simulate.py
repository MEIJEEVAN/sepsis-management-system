"""Real-time ICU simulator.

Talks to the REST API only (never to the database directly) so that the API,
the SQL triggers and the SSE stream are all exercised.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from dataclasses import dataclass
from datetime import date

import requests

API = os.getenv("API_URL", "http://localhost:5000/api")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@sepsis.local")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin12345")
VITAL_PERIOD = 3  # simulated seconds between vitals rounds
LAB_EVERY = 10  # every 10th vitals round -> labs every 30 simulated seconds

NORMAL_V = dict(temperature=36.8, heart_rate=76, respiratory_rate=16,
                systolic_bp=122, diastolic_bp=78, spo2=98.0, gcs=15)
NORMAL_L = dict(wbc=7.5, lactate=1.0, crp=4.0, procalcitonin=0.05,
                creatinine=0.9, bilirubin=0.7, platelets=250, inr=1.0)
SEPTIC_V = dict(temperature=39.0, heart_rate=118, respiratory_rate=25,
                systolic_bp=92, diastolic_bp=56, spo2=91.0, gcs=14)
SEPTIC_L = dict(wbc=16.5, lactate=3.4, crp=140.0, procalcitonin=4.0,
                creatinine=1.8, bilirubin=1.9, platelets=140, inr=1.5)

NAMES = [("Arjun", "Rao"), ("Meena", "Iyer"), ("Karthik", "Das"), ("Divya", "Nair"),
         ("Suresh", "Pillai"), ("Anitha", "Menon"), ("Ravi", "Kumar"), ("Lakshmi", "Bose"),
         ("Vikram", "Shah"), ("Priya", "Sen")]
NOISE = dict(temperature=0.1, heart_rate=2.0, respiratory_rate=0.7, systolic_bp=3.0,
             diastolic_bp=2.0, spo2=0.4, gcs=0.0)


@dataclass(frozen=True)
class Persona:
    """A patient trajectory: linear blend from state 0 to state 1 inside a time window."""

    idx: int
    label: str
    v0: dict[str, float]
    v1: dict[str, float]
    v_window: tuple[float, float]
    l0: dict[str, float]
    l1: dict[str, float]
    l_window: tuple[float, float]


def _v(**kw: float) -> dict[str, float]:
    """Return normal vitals overridden by ``kw``."""
    return {**NORMAL_V, **kw}


def _l(**kw: float) -> dict[str, float]:
    """Return normal labs overridden by ``kw``."""
    return {**NORMAL_L, **kw}


PERSONAS = [
    *[Persona(i, "stable post-op", NORMAL_V, NORMAL_V, (0, 1), NORMAL_L, NORMAL_L, (0, 1))
      for i in range(1, 5)],
    Persona(5, "mild deterioration", NORMAL_V,
            _v(temperature=38.2, heart_rate=105, respiratory_rate=22), (60, 90),
            NORMAL_L, _l(wbc=11.5, lactate=1.6, crp=40.0), (60, 120)),
    Persona(6, "mild deterioration", NORMAL_V,
            _v(temperature=38.3, heart_rate=108, respiratory_rate=23), (60, 100),
            NORMAL_L, _l(wbc=11.0, lactate=1.7, crp=35.0), (60, 120)),
    Persona(7, "developing sepsis", NORMAL_V,
            _v(temperature=38.7, heart_rate=114, respiratory_rate=24, systolic_bp=98,
               diastolic_bp=60, spo2=93.0, gcs=14), (45, 70),
            _l(wbc=9.0, lactate=1.8),
            _l(wbc=15.5, lactate=3.5, crp=120.0, procalcitonin=2.5, creatinine=1.6,
               bilirubin=1.8, platelets=150, inr=1.4), (45, 120)),
    Persona(8, "developing sepsis", NORMAL_V,
            _v(temperature=38.6, heart_rate=112, respiratory_rate=24, systolic_bp=99,
               diastolic_bp=62, spo2=93.0, gcs=14), (50, 75),
            _l(wbc=9.0, lactate=1.8),
            _l(wbc=14.5, lactate=3.2, crp=100.0, procalcitonin=2.0, creatinine=1.5,
               bilirubin=1.5, platelets=160, inr=1.3), (50, 120)),
    Persona(9, "septic shock", NORMAL_V,
            _v(temperature=39.4, heart_rate=128, respiratory_rate=26, systolic_bp=83,
               diastolic_bp=48, spo2=90.0, gcs=14), (30, 40),
            _l(lactate=1.4),
            _l(wbc=18.0, lactate=4.5, crp=220.0, procalcitonin=12.0, creatinine=2.8,
               bilirubin=3.0, platelets=90, inr=1.9), (30, 90)),
    Persona(10, "recovering", SEPTIC_V, NORMAL_V, (0, 150), SEPTIC_L, NORMAL_L, (0, 150)),
]


def clamp(x: float, lo: float, hi: float) -> float:
    """Limit ``x`` to the range ``[lo, hi]``."""
    return max(lo, min(hi, x))


def blend(a: dict[str, float], b: dict[str, float], f: float) -> dict[str, float]:
    """Linearly interpolate every key between ``a`` and ``b``."""
    return {k: a[k] + (b[k] - a[k]) * f for k in a}


def factor(t: float, window: tuple[float, float]) -> float:
    """Return progress 0..1 of ``t`` through ``window``."""
    t0, t1 = window
    return clamp((t - t0) / (t1 - t0), 0.0, 1.0)


def make_vitals(p: Persona, t: float, rng: random.Random) -> dict[str, float | int]:
    """Generate one vitals reading for persona ``p`` at simulated time ``t``."""
    v = blend(p.v0, p.v1, factor(t, p.v_window))
    for k, sd in NOISE.items():
        v[k] += rng.gauss(0, sd)
    return {
        "temperature": round(clamp(v["temperature"], 30, 45), 1),
        "heart_rate": int(clamp(round(v["heart_rate"]), 20, 250)),
        "respiratory_rate": int(clamp(round(v["respiratory_rate"]), 4, 60)),
        "systolic_bp": int(clamp(round(v["systolic_bp"]), 40, 300)),
        "diastolic_bp": int(clamp(round(v["diastolic_bp"]), 20, 200)),
        "spo2": round(clamp(v["spo2"], 50, 100), 1),
        "gcs": int(clamp(round(v["gcs"]), 3, 15)),
    }


def make_labs(p: Persona, t: float, rng: random.Random) -> dict[str, float | int]:
    """Generate one lab panel for persona ``p`` at simulated time ``t``."""
    lab = blend(p.l0, p.l1, factor(t, p.l_window))

    def j(x: float, pct: float) -> float:
        """Apply random jitter of up to +/- ``pct`` to ``x``."""
        return x * (1 + rng.uniform(-pct, pct))

    return {
        "wbc": round(clamp(j(lab["wbc"], 0.03), 0, 100), 1),
        "lactate": round(clamp(j(lab["lactate"], 0.02), 0, 30), 2),
        "crp": round(clamp(j(lab["crp"], 0.05), 0, 500), 2),
        "procalcitonin": round(clamp(j(lab["procalcitonin"], 0.05), 0, 100), 2),
        "creatinine": round(clamp(j(lab["creatinine"], 0.03), 0, 20), 2),
        "bilirubin": round(clamp(j(lab["bilirubin"], 0.03), 0, 30), 2),
        "platelets": int(clamp(round(j(lab["platelets"], 0.03)), 0, 1000)),
        "inr": round(clamp(j(lab["inr"], 0.02), 0.5, 10), 2),
    }


class ApiClient:
    """Tiny JWT-aware HTTP client that re-logs in once on a 401."""

    def __init__(self) -> None:
        """Create the HTTP session."""
        self.session = requests.Session()
        self.token = ""

    def login(self) -> None:
        """Authenticate as the seeded admin."""
        r = self.session.post(
            f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=10
        )
        r.raise_for_status()
        self.token = r.json()["access_token"]

    def request(self, method: str, path: str, **kw: object) -> requests.Response:
        """Send an authenticated request, retrying once after a fresh login on 401."""
        for attempt in (1, 2):
            headers = {"Authorization": f"Bearer {self.token}"}
            r = self.session.request(method, f"{API}{path}", headers=headers, timeout=10, **kw)
            if r.status_code != 401 or attempt == 2:
                return r
            self.login()
        return r  # pragma: no cover


def ensure_patients(client: ApiClient) -> dict[int, int]:
    """Create the 10 patients if missing and map persona index -> patient id."""
    existing = {p["mrn"]: p["id"] for p in client.request("GET", "/patients").json()}
    ids: dict[int, int] = {}
    for i, (first, last) in enumerate(NAMES, start=1):
        mrn = f"MRN-{i:04d}"
        if mrn in existing:
            ids[i] = existing[mrn]
            continue
        payload = {"mrn": mrn, "first_name": first, "last_name": last,
                   "dob": date(1950 + i * 3, 1 + i % 12, 10).isoformat(),
                   "gender": "Female" if i % 2 == 0 else "Male", "bed_number": f"ICU-{i}"}
        r = client.request("POST", "/patients", json=payload)
        r.raise_for_status()
        ids[i] = r.json()["id"]
        print(f"created {mrn} -> id {ids[i]} → {r.status_code}")
    return ids


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line flags."""
    ap = argparse.ArgumentParser(description="Sepsis ICU simulator")
    ap.add_argument("--seed", type=int, default=42, help="random seed (default 42)")
    ap.add_argument("--speed", type=float, default=1.0, help="time multiplier (2 = twice as fast)")
    ap.add_argument("--duration", type=float, default=0, help="stop after N simulated seconds")
    args = ap.parse_args(argv)
    if args.speed <= 0:
        ap.error("--speed must be > 0")
    return args


def send(client: ApiClient, t: float, p: Persona, kind: str, pid: int,
         payload: dict[str, float | int]) -> None:
    """POST one reading and print the HTTP status."""
    try:
        r = client.request("POST", f"/{kind}", json={"patient_id": pid, **payload})
        print(f"[t={t:.0f}s] P{p.idx} {kind[:-1] if kind == 'labs' else kind} → {r.status_code}")
    except requests.RequestException as exc:
        print(f"[t={t:.0f}s] P{p.idx} {kind} → request failed: {exc}")


def main(argv: list[str] | None = None) -> int:
    """Run the simulation loop until Ctrl+C (or ``--duration``)."""
    args = parse_args(argv)
    rngs = {p.idx: random.Random(args.seed * 1000 + p.idx) for p in PERSONAS}
    client = ApiClient()
    try:
        client.login()
        ids = ensure_patients(client)
    except requests.RequestException as exc:
        print(f"Cannot reach the API at {API}: {exc}", file=sys.stderr)
        return 1

    print(f"Simulating 10 patients (seed={args.seed}, speed={args.speed}). Ctrl+C to stop.")
    start, tick = time.monotonic(), 0
    try:
        while True:
            t = tick * VITAL_PERIOD
            if args.duration and t > args.duration:
                break
            for p in PERSONAS:
                send(client, t, p, "vitals", ids[p.idx], make_vitals(p, t, rngs[p.idx]))
            if tick % LAB_EVERY == 0:
                for p in PERSONAS:
                    send(client, t, p, "labs", ids[p.idx], make_labs(p, t, rngs[p.idx]))
            tick += 1
            time.sleep(max(0.0, start + tick * VITAL_PERIOD / args.speed - time.monotonic()))
    except KeyboardInterrupt:
        print("\nStopped by user.")
    print(f"Done after {tick} vitals rounds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
