from src.foods import FOODS, DISEASE_RULES
from src.planner import build_plan, nutrition_targets

BASE = dict(name="T", age=30, gender="female", height_cm=160, weight_kg=60, activity_level=2,
            diet="vegetarian", goal="maintain", diseases=[], wake_time="06:30",
            sleep_hours=7, water_litres=2, junk_food_per_week=2, dislikes="")
LOOKUP = {f[0]: f for f in FOODS}


def meals(plan):
    for d in plan["days"]:
        for e in d["events"]:
            if e["kind"] == "meal" and ": " in e["title"]:
                yield LOOKUP[e["title"].split(": ", 1)[1]]


def test_seven_days_with_all_meals():
    plan = build_plan(BASE)
    assert len(plan["days"]) == 7
    for d in plan["days"]:
        assert sum(e["kind"] == "meal" for e in d["events"]) == 5


def test_vegetarian_has_no_egg_or_meat():
    for f in meals(build_plan(BASE)):
        assert f[3] <= 1


def test_vegan_has_no_dairy():
    for f in meals(build_plan({**BASE, "diet": "vegan"})):
        assert f[3] == 0 and "dairy" not in f[4]


def test_every_disease_respects_its_excluded_flags():
    for dis, rule in DISEASE_RULES.items():
        for diet in ("vegetarian", "non_vegetarian"):
            plan = build_plan({**BASE, "diet": diet, "diseases": [dis]})
            for f in meals(plan):
                assert not set(f[4]) & set(rule["exclude"]), (dis, f[0])


def test_diabetes_has_post_meal_walks():
    plan = build_plan({**BASE, "diseases": ["diabetes"]})
    assert any(e["kind"] == "walk" for e in plan["days"][0]["events"])


def test_calorie_floor_and_underweight_goal_fix():
    t = nutrition_targets({**BASE, "weight_kg": 40, "goal": "lose_weight"})
    assert t["calories"] >= 1200 and t["goal_used"] == "maintain"


def test_timeline_is_in_order():
    ev = build_plan(BASE)["days"][0]["events"]
    assert ev[0]["kind"] == "wake" and ev[-1]["kind"] == "sleep"


def test_two_snacks_differ():
    for d in build_plan(BASE)["days"]:
        sn = [e["title"].split(": ", 1)[1] for e in d["events"] if "snack" in e["title"].lower()]
        assert len(sn) == 2 and sn[0] != sn[1]
