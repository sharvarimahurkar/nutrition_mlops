"""Builds the personalised weekly TIMETABLE (meals + water + exercise + sleep)
from the user's profile, diet type and diseases."""
from __future__ import annotations

from src.features import ACTIVITY, bmi_category, bmi_of
from src.foods import DIET_LEVEL, DISEASE_RULES, FOODS

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SLOT_SHARE = {"breakfast": .25, "snack1": .10, "lunch": .30, "snack2": .10, "dinner": .25}
ACTIVITY_FACTOR = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725}


# ------------------------------------------------------------------ helpers
def fmt(minutes_after_midnight: float) -> str:
    m = int(round(minutes_after_midnight)) % (24 * 60)
    h, mm = divmod(m, 60)
    suffix = "AM" if h < 12 else "PM"
    return f"{(h % 12) or 12}:{mm:02d} {suffix}"


def _gl(n):
    return f"{n} glass" if n == 1 else f"{n} glasses"


def parse_time(t: str) -> int:
    h, m = t.split(":")[:2]
    return int(h) * 60 + int(m)


# ------------------------------------------------------------------ nutrition numbers
def nutrition_targets(p: dict) -> dict:
    w, h, age = p["weight_kg"], p["height_cm"], p["age"]
    bmr = 10 * w + 6.25 * h - 5 * age + (5 if p["gender"] == "male" else -161)
    tdee = bmr * ACTIVITY_FACTOR[p["activity_level"]]
    bmi = bmi_of(w, h)
    cat = bmi_category(bmi)
    diseases = set(p.get("diseases", []))
    goal = p["goal"]
    notes = []
    if cat == "Underweight" and goal == "lose_weight":
        goal = "maintain"
        notes.append("You are underweight, so the weight-loss goal was changed to 'maintain'.")
    if "obesity" in diseases and goal == "maintain" and cat in ("Overweight", "Obese"):
        goal = "lose_weight"
        notes.append("Obesity selected: plan switched to a gentle calorie deficit.")
    kcal = tdee + {"lose_weight": -450, "maintain": 0, "gain_weight": 400}[goal]
    floor = 1500 if p["gender"] == "male" else 1200
    kcal = max(kcal, floor)
    protein_per_kg = 0.8 if "kidney_disease" in diseases else (1.4 if goal == "gain_weight" else 1.0)
    protein_g = protein_per_kg * w
    fat_g = kcal * 0.25 / 9
    carb_g = max((kcal - protein_g * 4 - fat_g * 9) / 4, 0)
    water_ml = int(round(w * 35 / 250.0) * 250)
    if "gout_uric_acid" in diseases:
        water_ml = max(water_ml, 2500)
    return {
        "bmi": round(bmi, 1), "bmi_category": cat, "bmr": round(bmr), "tdee": round(tdee),
        "goal_used": goal, "calories": int(round(kcal / 10.0) * 10),
        "protein_g": round(protein_g), "carbs_g": round(carb_g), "fat_g": round(fat_g),
        "water_ml": water_ml, "notes": notes,
    }


# ------------------------------------------------------------------ food selection
def _allowed_foods(p: dict, slot: str):
    level = DIET_LEVEL[p["diet"]]
    diseases = [d for d in p.get("diseases", []) if d in DISEASE_RULES]
    excluded = {f for d in diseases for f in DISEASE_RULES[d]["exclude"]}
    prefer = [f for d in diseases for f in DISEASE_RULES[d]["prefer"]]
    dislikes = [x.strip().lower() for x in (p.get("dislikes") or "").split(",") if x.strip()]
    if p["goal"] == "lose_weight":
        prefer += ["light", "fiber"]
    elif p["goal"] == "gain_weight":
        prefer += ["protein"]
    out = []
    for name, s, kcal, lvl, flags, prefs in FOODS:
        if s != slot or lvl > level:
            continue
        if excluded.intersection(flags):
            continue
        if any(d in name.lower() for d in dislikes):
            continue
        score = sum(prefs.count(x) for x in prefer) * 2 + len(set(prefs) & set(prefer))
        out.append((score, name, kcal))
    # best matches first; stable alphabetical tie-break keeps output deterministic
    out.sort(key=lambda t: (-t[0], t[1]))
    return out


def _pool(p: dict, slot: str, size: int = 7):
    items = _allowed_foods(p, slot)
    if not items:
        return []
    top = items[0][0]
    good = [i for i in items if i[0] >= max(top - 2, 0)] or items
    if len(good) < 4:
        good = items
    return good[:size + 3]


def _serving(target_kcal: float, kcal: int, lo=0.5, hi=2.0) -> float:
    s = round(target_kcal / kcal * 2) / 2
    return min(max(s, lo), hi)


def _pick(pool, day: int, offset: int):
    if not pool:
        return None
    if offset == 4:                      # 2nd snack: always a different item than the 1st
        offset = max(1, len(pool) // 2)
    return pool[(day + offset) % len(pool)]


# ------------------------------------------------------------------ exercise
GENTLE = [
    ("Brisk walk", "easy pace, you should be able to talk"),
    ("Yoga & stretching", "gentle asanas, breathing focus"),
    ("Walk", "easy pace"),
    ("Pranayama + light stretching", "anulom-vilom, bhramari"),
    ("Walk", "easy pace, flat route"),
    ("Light yoga", "Surya namaskar (slow) / chair yoga"),
    ("Rest day", "gentle stretching only"),
]
STANDARD = [
    ("Brisk walk / jog", "steady pace"),
    ("Strength training", "bodyweight: squats, push-ups, planks"),
    ("Yoga", "Surya namaskar + flexibility"),
    ("Cycling / swimming / brisk walk", "moderate effort"),
    ("Strength training", "upper body + core"),
    ("Sport / long walk", "enjoyable activity of your choice"),
    ("Rest day", "gentle stretching or a leisurely walk"),
]
WEIGHT_GAIN = [
    ("Strength training", "upper body, compound lifts"),
    ("Light walk", "20 min, easy"),
    ("Strength training", "lower body"),
    ("Yoga", "mobility and stretching"),
    ("Strength training", "full body"),
    ("Light sport / walk", "easy effort"),
    ("Rest day", "recovery + good sleep"),
]


def exercise_plan(p: dict):
    d = set(p.get("diseases", []))
    bmi = bmi_of(p["weight_kg"], p["height_cm"])
    gentle = bool(d & {"heart_disease", "hypertension", "kidney_disease"}) or bmi >= 35 or p["age"] >= 60
    if gentle:
        base = GENTLE
    elif p["goal"] == "gain_weight":
        base = WEIGHT_GAIN
    else:
        base = STANDARD
    mins = {1: 20, 2: 30, 3: 40, 4: 50}[p["activity_level"]]
    if gentle:
        mins = min(mins, 30)
    return base, mins, gentle


# ------------------------------------------------------------------ main
def build_plan(p: dict) -> dict:
    t = nutrition_targets(p)
    diseases = [d for d in p.get("diseases", []) if d in DISEASE_RULES]
    wake = parse_time(p["wake_time"])           # minutes after midnight
    sleep_len = p["sleep_hours"] * 60
    bed_rel = 24 * 60 - sleep_len               # bedtime, minutes AFTER wake-up

    ex_base, ex_min, gentle = exercise_plan(p)
    pools = {
        "breakfast": _pool(p, "breakfast"), "snack": _pool(p, "snack", 9),
        "lunch": _pool(p, "lunch"), "dinner": _pool(p, "dinner"),
    }
    warnings = list(t["notes"])
    for slot, pool in pools.items():
        if not pool:
            warnings.append(f"No {slot} option fits all your restrictions - please consult a dietitian for this meal.")

    # clock times (minutes after wake-up)
    r_ex = 30
    r_bf = r_ex + ex_min + 30
    r_s1 = r_bf + 150
    r_lunch = max(r_bf + 300, r_s1 + 120)
    r_s2 = r_lunch + 210
    r_dinner = min(max(bed_rel - 180, r_s2 + 120), bed_rel - 90)
    r_dinner = max(r_dinner, r_s2 + 90)
    glasses = max(int(round(t["water_ml"] / 250)), 6)
    w_split = [.2, .15, .2, .25, .2]
    w_counts = [max(1, round(glasses * x)) for x in w_split]

    days = []
    for i, day in enumerate(DAYS):
        ev = []
        add = lambda rel, kind, title, detail="", kcal=None: ev.append(
            {"time": fmt(wake + rel), "_rel": rel, "kind": kind, "title": title, "detail": detail, "kcal": kcal})

        add(0, "wake", "Wake up", f"Start with {w_counts[0]} glasses of water (about {w_counts[0] * 250} ml).")
        name, detail = ex_base[i]
        if name == "Rest day":
            add(r_ex, "exercise", "Rest / recovery", detail)
        else:
            add(r_ex, "exercise", f"{name} - {ex_min} min", detail)

        meal_plan = [("breakfast", r_bf, "Breakfast", "breakfast", 0, "breakfast"),
                     ("snack1", r_s1, "Mid-morning snack", "snack", 0, "snack"),
                     ("lunch", r_lunch, "Lunch", "lunch", 2, "lunch"),
                     ("snack2", r_s2, "Evening snack", "snack", 4, "snack"),
                     ("dinner", r_dinner, "Dinner", "dinner", 1, "dinner")]
        total = 0
        for key, rel, label, pool_key, off, _ in meal_plan:
            item = _pick(pools[pool_key], i, off)
            if not item:
                add(rel, "meal", label, "No suitable option - consult a dietitian.", None)
                continue
            _, fname, kcal = item
            target = t["calories"] * SLOT_SHARE[key]
            lo, hi = (0.5, 2.0)
            sv = _serving(target, kcal, lo, hi)
            sv_txt = "1 serving" if sv == 1 else f"{sv:g} servings"
            kc = int(round(kcal * sv))
            total += kc
            add(rel, "meal", f"{label}: {fname}", f"{sv_txt}", kc)

        # water reminders
        add(r_s1 - 20, "water", "Water", _gl(w_counts[1]))
        add(r_lunch - 30, "water", "Water before lunch", _gl(w_counts[2]))
        add(r_s2 - 20, "water", "Water", _gl(w_counts[3]))
        add(min(r_dinner + 60, bed_rel - 45), "water", "Water (sip, don't gulp before bed)", _gl(w_counts[4]))

        # disease-specific timetable items
        if "diabetes" in diseases:
            add(r_lunch + 30, "walk", "Post-meal walk", "10-15 minutes - helps blood sugar")
            add(r_dinner + 30, "walk", "Post-dinner walk", "10-15 minutes")
        if "thyroid" in diseases:
            add(r_bf - 45, "medicine", "Thyroid medicine (if prescribed)", "Empty stomach, 30-60 min before breakfast - as advised by your doctor")
        if "gastritis_acidity" in diseases:
            add(r_dinner + 120, "tip", "Stay upright", "Avoid lying down for 2-3 hours after dinner")
        if "hypertension" in diseases or "heart_disease" in diseases:
            add(r_dinner + 90, "tip", "Wind-down", "5 min slow breathing (pranayama) to lower stress & BP")
        add(bed_rel - 30, "tip", "Screens off", "Dim lights, no phone; prepare for sleep")
        add(bed_rel, "sleep", "Sleep", f"Target {p['sleep_hours']:g} hours of sleep")

        ev.sort(key=lambda e: e["_rel"])
        for e in ev:
            e.pop("_rel")
        days.append({"day": day, "total_kcal": total, "events": ev})

    guidance = [{"disease": d, "label": DISEASE_RULES[d]["label"], "avoid": DISEASE_RULES[d]["avoid"],
                 "include": DISEASE_RULES[d]["include"], "tips": DISEASE_RULES[d]["tips"]} for d in diseases]

    return {"targets": t, "days": days, "guidance": guidance, "warnings": warnings,
            "gentle_exercise": gentle, "exercise_minutes": ex_min,
            "activity_label": ACTIVITY[p["activity_level"]]}


def lifestyle_findings(p: dict, targets: dict) -> list[dict]:
    """Plain-language lifestyle assessment shown in the report."""
    f = []
    cat = targets["bmi_category"]
    if cat != "Normal":
        f.append({"level": "warn", "text": f"BMI {targets['bmi']} is in the {cat} range."})
    else:
        f.append({"level": "good", "text": f"BMI {targets['bmi']} is in the healthy range."})
    if p["sleep_hours"] < 7:
        f.append({"level": "warn", "text": f"Sleep of {p['sleep_hours']:g} h is below the recommended 7-9 h."})
    else:
        f.append({"level": "good", "text": "Your sleep duration is adequate."})
    if p["water_litres"] * 1000 < targets["water_ml"] * 0.8:
        f.append({"level": "warn", "text": f"You drink {p['water_litres']:g} L/day; target is about {targets['water_ml'] / 1000:g} L."})
    if p["activity_level"] <= 2:
        f.append({"level": "warn", "text": "Low physical activity - the timetable gradually builds exercise in."})
    if p["junk_food_per_week"] >= 4:
        f.append({"level": "warn", "text": f"{p['junk_food_per_week']} junk-food meals a week is high; try to keep it to 1-2."})
    return f
