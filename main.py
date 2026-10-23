"""FastAPI service: serves the frontend + REST API + monitoring endpoints.

  GET  /              -> web form (frontend/)
  POST /api/plan      -> ML risk assessment + weekly timetable (JSON)
  GET  /health        -> health check
  GET  /model-info    -> selected model + evaluation table
  GET  /metrics       -> Prometheus-format metrics
  GET  /drift         -> data-drift report
  GET  /docs          -> auto-generated Swagger UI
"""
import csv
import json
import logging
import os
import threading
import time
from typing import List, Literal, Optional

import joblib
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.data_gen import ROOT
from src.drift import LOG_PATH, drift_report
from src.features import DISEASES, FEATURES, NUMERIC, RISK_LABELS, build_row
from src.planner import build_plan, lifestyle_findings

MODEL_PATH = os.path.join(ROOT, "models", "model.joblib")
METRICS_PATH = os.path.join(ROOT, "models", "metrics.json")
FRONTEND = os.path.join(ROOT, "frontend")

os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
logging.basicConfig(filename=os.path.join(ROOT, "logs", "app.log"), level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("nutrition")

app = FastAPI(title="ML-Based Lifestyle & Nutritional Assessment Framework", version="1.0.0")
_lock = threading.Lock()
STATS = {"requests": 0, "errors": 0, "latency_sum": 0.0, "pred": {0: 0, 1: 0, 2: 0}}
_model = None


def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):          # first run: train automatically
            from src.train import main as train
            train()
        try:
            _model = joblib.load(MODEL_PATH)
        except Exception as e:                      # e.g. saved with another scikit-learn version
            log.warning("model could not be loaded (%s) - retraining", e)
            _retrain()
    return _model


def _retrain():
    global _model
    from src.train import main as train
    train()
    _model = joblib.load(MODEL_PATH)


class Profile(BaseModel):
    name: str = Field("User", max_length=60)
    age: int = Field(..., ge=10, le=100)
    gender: Literal["male", "female"]
    height_cm: float = Field(..., ge=100, le=230)
    weight_kg: float = Field(..., ge=25, le=250)
    activity_level: int = Field(2, ge=1, le=4)
    diet: Literal["vegan", "vegetarian", "eggetarian", "non_vegetarian"]
    goal: Literal["lose_weight", "maintain", "gain_weight"] = "maintain"
    diseases: List[str] = []
    wake_time: str = Field("06:30", pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    sleep_hours: float = Field(7, ge=3, le=12)
    water_litres: float = Field(2, ge=0, le=8)
    junk_food_per_week: int = Field(2, ge=0, le=21)
    dislikes: Optional[str] = Field("", max_length=200)


@app.middleware("http")
async def track(request: Request, call_next):
    t0 = time.time()
    try:
        response = await call_next(request)
    except Exception:
        with _lock:
            STATS["errors"] += 1
        raise
    if request.url.path.startswith("/api/"):
        with _lock:
            STATS["requests"] += 1
            STATS["latency_sum"] += time.time() - t0
            if response.status_code >= 400:
                STATS["errors"] += 1
    return response


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": os.path.exists(MODEL_PATH)}


@app.get("/model-info")
def model_info():
    get_model()
    return json.load(open(METRICS_PATH))


@app.get("/api/options")
def options():
    return {"diseases": DISEASES}


@app.post("/api/plan")
def plan(profile: Profile):
    p = profile.model_dump()
    unknown = [d for d in p["diseases"] if d not in DISEASES]
    if unknown:
        raise HTTPException(422, f"Unknown disease keys: {unknown}")
    model = get_model()
    row = build_row(p)
    try:
        risk = int(model.predict(row[FEATURES])[0])
        proba = model.predict_proba(row[FEATURES])[0].tolist()
    except Exception as e:                          # incompatible / corrupt model -> retrain once
        log.warning("prediction failed (%s) - retraining", e)
        _retrain()
        model = _model
        risk = int(model.predict(row[FEATURES])[0])
        proba = model.predict_proba(row[FEATURES])[0].tolist()
    result = build_plan(p)
    result["assessment"] = {
        "risk_level": RISK_LABELS[risk],
        "risk_index": risk,
        "probabilities": {RISK_LABELS[i]: round(v, 3) for i, v in enumerate(proba)},
        "findings": lifestyle_findings(p, result["targets"]),
    }
    result["profile"] = {"name": p["name"], "diet": p["diet"], "goal": p["goal"], "diseases": p["diseases"]}

    # log the request features (used for drift monitoring)
    try:
        with _lock:
            STATS["pred"][risk] += 1
            new = not os.path.exists(LOG_PATH)
            with open(LOG_PATH, "a", newline="") as f:
                w = csv.writer(f)
                if new:
                    w.writerow(NUMERIC + ["risk_pred"])
                w.writerow([float(row.iloc[0][c]) for c in NUMERIC] + [risk])
    except Exception as e:                              # logging must never break serving
        log.warning("could not write request log: %s", e)
    log.info("plan generated diet=%s risk=%s", p["diet"], RISK_LABELS[risk])
    return result


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    with _lock:
        n, err, lat = STATS["requests"], STATS["errors"], STATS["latency_sum"]
        pred = dict(STATS["pred"])
    out = [
        "# TYPE nutrition_requests_total counter", f"nutrition_requests_total {n}",
        "# TYPE nutrition_errors_total counter", f"nutrition_errors_total {err}",
        "# TYPE nutrition_response_seconds_avg gauge",
        f"nutrition_response_seconds_avg {(lat / n) if n else 0:.6f}",
        "# TYPE nutrition_predictions_total counter",
    ]
    out += [f'nutrition_predictions_total{{risk="{RISK_LABELS[k]}"}} {v}' for k, v in pred.items()]
    return "\n".join(out) + "\n"


@app.get("/drift")
def drift():
    return drift_report()


@app.get("/")
def index():
    return FileResponse(os.path.join(FRONTEND, "index.html"))


app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
