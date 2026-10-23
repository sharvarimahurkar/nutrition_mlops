"""Shared feature definitions + preprocessing helpers (used by training AND serving,
so training and inference stay consistent - see slide 3)."""
import pandas as pd

DISEASES = [
    "diabetes", "hypertension", "high_cholesterol", "heart_disease", "thyroid",
    "pcos", "anemia", "obesity", "kidney_disease", "gastritis_acidity",
    "gout_uric_acid", "lactose_intolerance", "gluten_intolerance",
]

DIET_TYPES = ["vegan", "vegetarian", "eggetarian", "non_vegetarian"]
GOALS = ["lose_weight", "maintain", "gain_weight"]
ACTIVITY = {1: "Sedentary", 2: "Lightly active", 3: "Moderately active", 4: "Very active"}

NUMERIC = ["age", "gender", "bmi", "activity_level", "sleep_hours",
           "water_litres", "junk_food_per_week", "n_diseases"]
FEATURES = NUMERIC + ["has_" + d for d in DISEASES]
TARGET = "risk_level"          # 0 = Low, 1 = Moderate, 2 = High
RISK_LABELS = {0: "Low", 1: "Moderate", 2: "High"}


def bmi_of(weight_kg: float, height_cm: float) -> float:
    return weight_kg / ((height_cm / 100.0) ** 2)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def build_row(p: dict) -> pd.DataFrame:
    """Turn a user profile dict into the one-row feature frame the model expects."""
    diseases = set(p.get("diseases", []))
    row = {
        "age": p["age"],
        "gender": 1 if p["gender"] == "male" else 0,
        "bmi": bmi_of(p["weight_kg"], p["height_cm"]),
        "activity_level": p["activity_level"],
        "sleep_hours": p["sleep_hours"],
        "water_litres": p["water_litres"],
        "junk_food_per_week": p["junk_food_per_week"],
        "n_diseases": len(diseases),
    }
    for d in DISEASES:
        row["has_" + d] = int(d in diseases)
    return pd.DataFrame([row])[FEATURES]
