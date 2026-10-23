"""Train + compare models, pick the best by cross-validated F1, save it.

Run:  python -m src.train
Outputs: models/model.joblib, models/metrics.json, models/reference_stats.json
Logs every run to MLflow automatically if `mlflow` is installed (optional).
"""
import json
import os
import time

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.data_gen import DATA_PATH, ROOT, generate
from src.features import FEATURES, NUMERIC, TARGET

MODEL_DIR = os.path.join(ROOT, "models")


def load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        generate().to_csv(DATA_PATH, index=False)
        print("No data/nutrition.csv found -> generated synthetic dataset.")
    df = pd.read_csv(DATA_PATH)
    # --- data validation ---
    missing_cols = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset is missing columns: {missing_cols}")
    df = df.drop_duplicates().dropna(subset=FEATURES + [TARGET])   # duplicates + NaN
    return df


def main():
    df = load_data()
    X, y = df[FEATURES], df[TARGET]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42, stratify=y)

    candidates = {
        "LogisticRegression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        "RandomForest": RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=-1),
        "GradientBoosting": GradientBoostingClassifier(random_state=42),
    }

    try:
        import mlflow
        mlflow.set_tracking_uri("file:" + os.path.join(ROOT, "mlruns"))
        mlflow.set_experiment("nutrition-lifestyle-assessment")
    except Exception:
        mlflow = None

    results, fitted = [], {}
    for name, model in candidates.items():
        t0 = time.time()
        cv = cross_val_score(model, Xtr, ytr, cv=5, scoring="f1_macro").mean()
        model.fit(Xtr, ytr)
        pred = model.predict(Xte)
        r = {
            "model": name,
            "cv_f1_macro": round(float(cv), 4),
            "accuracy": round(float(accuracy_score(yte, pred)), 4),
            "precision": round(float(precision_score(yte, pred, average="macro")), 4),
            "recall": round(float(recall_score(yte, pred, average="macro")), 4),
            "f1": round(float(f1_score(yte, pred, average="macro")), 4),
            "train_seconds": round(time.time() - t0, 2),
        }
        results.append(r)
        fitted[name] = model
        print(r)
        if mlflow:
            with mlflow.start_run(run_name=name):
                mlflow.log_param("model", name)
                mlflow.log_metrics({k: v for k, v in r.items() if k != "model"})

    best = max(results, key=lambda r: r["cv_f1_macro"])      # selection by CV, not train score
    for r in results:
        r["selected"] = r["model"] == best["model"]

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(fitted[best["model"]], os.path.join(MODEL_DIR, "model.joblib"))
    meta = {"best_model": best["model"], "n_rows": int(len(df)), "n_features": len(FEATURES),
            "selection_metric": "cv_f1_macro", "results": results,
            "trained_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(meta, f, indent=2)

    # reference distribution of the training data -> used for drift detection
    ref = {c: {"mean": float(df[c].mean()), "std": float(df[c].std() or 1.0),
               "bins": [float(v) for v in df[c].quantile([0, .2, .4, .6, .8, 1]).tolist()]}
           for c in NUMERIC}
    with open(os.path.join(MODEL_DIR, "reference_stats.json"), "w") as f:
        json.dump(ref, f, indent=2)
    print(f"\nBest model: {best['model']}  (CV F1 {best['cv_f1_macro']})  -> models/model.joblib")


if __name__ == "__main__":
    main()
