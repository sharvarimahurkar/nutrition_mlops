"""Generates a synthetic nutrition / lifestyle dataset (data/nutrition.csv).

The Kaggle dataset used in the report can be dropped in at data/nutrition.csv as
long as it has the columns listed in src/features.py (FEATURES + risk_level).
If that file exists, training uses it instead of the synthetic one.
"""
import os
import numpy as np
import pandas as pd
from src.features import DISEASES, FEATURES, TARGET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "nutrition.csv")

# rough prevalence of each condition in a general adult population
PREV = {"diabetes": .10, "hypertension": .18, "high_cholesterol": .14, "heart_disease": .05,
        "thyroid": .08, "pcos": .06, "anemia": .12, "obesity": .12, "kidney_disease": .03,
        "gastritis_acidity": .12, "gout_uric_acid": .04, "lactose_intolerance": .08,
        "gluten_intolerance": .02}
# how much each condition adds to risk
WEIGHT = {"diabetes": 2.0, "hypertension": 1.6, "high_cholesterol": 1.3, "heart_disease": 2.4,
          "thyroid": .8, "pcos": 1.0, "anemia": .9, "obesity": 1.6, "kidney_disease": 2.2,
          "gastritis_acidity": .5, "gout_uric_acid": .9, "lactose_intolerance": .2,
          "gluten_intolerance": .3}


def generate(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "age": rng.integers(15, 80, n),
        "gender": rng.integers(0, 2, n),
        "bmi": np.clip(rng.normal(25, 5, n), 15, 45).round(1),
        "activity_level": rng.integers(1, 5, n),
        "sleep_hours": np.clip(rng.normal(6.8, 1.3, n), 3.5, 10).round(1),
        "water_litres": np.clip(rng.normal(2.2, .8, n), .5, 5).round(1),
        "junk_food_per_week": rng.integers(0, 15, n),
    })
    for d in DISEASES:
        df["has_" + d] = (rng.random(n) < PREV[d]).astype(int)
    df["n_diseases"] = df[["has_" + d for d in DISEASES]].sum(axis=1)

    score = (
        np.abs(df.bmi - 22) * .22
        + (df.age - 30).clip(lower=0) * .035
        + (4 - df.activity_level) * .55
        + (7.5 - df.sleep_hours).clip(lower=0) * .45
        + (2.5 - df.water_litres).clip(lower=0) * .4
        + df.junk_food_per_week * .17
    )
    for d in DISEASES:
        score += df["has_" + d] * WEIGHT[d]
    score += rng.normal(0, .6, n)
    q1, q2 = np.quantile(score, [.45, .80])
    df[TARGET] = np.where(score < q1, 0, np.where(score < q2, 1, 2))
    return df[FEATURES + [TARGET]]


if __name__ == "__main__":
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    d = generate()
    d.to_csv(DATA_PATH, index=False)
    print(f"Wrote {len(d)} rows -> {DATA_PATH}")
