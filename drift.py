"""Simple data-drift check: Population Stability Index (PSI) between the training
data (models/reference_stats.json) and the requests the API has actually received
(logs/requests.csv). PSI > 0.2 on a feature => significant drift => retrain."""
import json
import os

import numpy as np
import pandas as pd

from src.data_gen import ROOT
from src.features import NUMERIC

REF_PATH = os.path.join(ROOT, "models", "reference_stats.json")
LOG_PATH = os.path.join(ROOT, "logs", "requests.csv")
THRESHOLD = 0.2
MIN_ROWS = 30


def psi(ref_bins, actual) -> float:
    edges = np.array(ref_bins, dtype=float)
    edges[0], edges[-1] = -np.inf, np.inf
    edges = np.unique(edges)
    if len(edges) < 3:
        return 0.0
    exp = np.full(len(edges) - 1, 1.0 / (len(edges) - 1))
    act = np.histogram(actual, bins=edges)[0] / max(len(actual), 1)
    act = np.clip(act, 1e-4, None)
    exp = np.clip(exp, 1e-4, None)
    return float(np.sum((act - exp) * np.log(act / exp)))


def drift_report() -> dict:
    if not os.path.exists(REF_PATH):
        return {"status": "no_reference", "message": "Train the model first (python -m src.train)."}
    if not os.path.exists(LOG_PATH):
        return {"status": "insufficient_data", "rows": 0, "min_rows": MIN_ROWS, "features": {}}
    df = pd.read_csv(LOG_PATH)
    if len(df) < MIN_ROWS:
        return {"status": "insufficient_data", "rows": int(len(df)), "min_rows": MIN_ROWS, "features": {}}
    ref = json.load(open(REF_PATH))
    feats = {c: round(psi(ref[c]["bins"], df[c].dropna().values), 4) for c in NUMERIC if c in df and c in ref}
    drifted = [c for c, v in feats.items() if v > THRESHOLD]
    return {"status": "drift_detected" if drifted else "ok", "rows": int(len(df)),
            "threshold": THRESHOLD, "features": feats, "drifted_features": drifted,
            "action": "Retrain: python -m src.train" if drifted else "No action needed"}
