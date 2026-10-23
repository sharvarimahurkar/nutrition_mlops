"""Food + disease knowledge base used by the timetable planner.

Item format: (name, slot, kcal_per_serving, diet_level, flags, prefs)
  diet_level : 0 = vegan, 1 = vegetarian, 2 = eggetarian, 3 = non-vegetarian
               (a user eats anything with level <= their own level)
  flags      : things that some diseases must avoid (sugar, high_gi, sodium, fat,
               spicy, purine, potassium, dairy, gluten, soy, protein_heavy)
  prefs      : things that some diseases / goals benefit from
               (fiber, iron, lowgi, protein, light, omega3)

NOTE: this is general nutrition guidance for a college project, not medical advice.
"""

DIET_LEVEL = {"vegan": 0, "vegetarian": 1, "eggetarian": 2, "non_vegetarian": 3}

FOODS = [
    # ---------------- BREAKFAST ----------------
    ("Vegetable poha with peanuts", "breakfast", 250, 0, ["high_gi"], ["iron", "light"]),
    ("Moong dal chilla with mint chutney", "breakfast", 220, 0, [], ["fiber", "protein", "lowgi", "light"]),
    ("Oats porridge (water / almond milk) with apple & nuts", "breakfast", 260, 0, [], ["fiber", "lowgi"]),
    ("Oats with milk and banana", "breakfast", 290, 1, ["dairy", "sugar"], ["fiber"]),
    ("Vegetable upma", "breakfast", 240, 0, ["gluten", "high_gi"], ["light"]),
    ("Ragi dosa with sambar", "breakfast", 230, 0, [], ["fiber", "iron", "lowgi"]),
    ("Idli (3) with sambar", "breakfast", 230, 0, ["high_gi"], ["light"]),
    ("Besan chilla with vegetables", "breakfast", 230, 0, [], ["protein", "lowgi", "fiber"]),
    ("Paneer bhurji with 1 multigrain roti", "breakfast", 330, 1, ["dairy", "gluten"], ["protein"]),
    ("Aloo paratha with butter and curd", "breakfast", 400, 1, ["fat", "high_gi", "dairy", "gluten"], []),
    ("Masala omelette (2 eggs) with multigrain toast", "breakfast", 290, 2, ["gluten"], ["protein"]),
    ("2 boiled eggs with sprouts salad", "breakfast", 240, 2, [], ["protein", "iron", "lowgi"]),
    ("Egg bhurji with 1 roti", "breakfast", 300, 2, ["gluten"], ["protein"]),
    ("Grilled chicken sandwich (whole wheat)", "breakfast", 330, 3, ["gluten", "purine"], ["protein"]),
    ("Apple-papaya bowl with chia seeds and almonds", "breakfast", 210, 0, [], ["fiber", "light", "omega3"]),
    ("Tofu scramble with vegetables", "breakfast", 250, 0, ["soy"], ["protein", "light"]),
    ("Vegetable dalia (broken wheat) porridge", "breakfast", 230, 0, ["gluten"], ["fiber", "lowgi", "iron"]),
    ("Plain dosa with coconut chutney", "breakfast", 250, 0, ["high_gi"], []),
    ("Greek yogurt with berries and flaxseeds", "breakfast", 220, 1, ["dairy"], ["protein", "omega3"]),
    ("Ragi porridge (savoury) with vegetables", "breakfast", 210, 0, [], ["iron", "fiber", "lowgi", "light"]),
    ("Sprouted moong salad with lemon and 1 boiled egg", "breakfast", 220, 2, [], ["protein", "fiber", "iron", "lowgi"]),

    # ---------------- SNACKS ----------------
    ("Roasted chana (30 g)", "snack", 120, 0, [], ["fiber", "protein", "iron", "lowgi"]),
    ("Almonds and walnuts (20 g)", "snack", 130, 0, [], ["omega3", "lowgi", "protein"]),
    ("Guava or apple slices with cinnamon", "snack", 80, 0, [], ["fiber", "light", "lowgi"]),
    ("Papaya bowl", "snack", 70, 0, [], ["light", "fiber"]),
    ("Buttermilk (chaas), 1 glass", "snack", 60, 1, ["dairy"], ["light"]),
    ("Sprouts chaat with lemon", "snack", 140, 0, [], ["fiber", "protein", "iron", "lowgi"]),
    ("Roasted makhana (1 cup)", "snack", 100, 0, [], ["light", "lowgi"]),
    ("Cucumber-carrot salad with lemon", "snack", 50, 0, [], ["light", "fiber"]),
    ("Coconut water (1 glass)", "snack", 45, 0, ["potassium"], ["light"]),
    ("Green tea with pumpkin & sunflower seeds", "snack", 110, 0, [], ["iron", "omega3"]),
    ("Banana (1 medium)", "snack", 90, 0, ["potassium", "sugar"], ["light"]),
    ("2 dates with 5 almonds", "snack", 120, 0, ["sugar"], ["iron"]),
    ("1 boiled egg with pepper", "snack", 80, 2, [], ["protein", "iron"]),
    ("Greek yogurt with chia seeds", "snack", 110, 1, ["dairy"], ["protein", "omega3"]),
    ("Grilled paneer cubes (50 g)", "snack", 120, 1, ["dairy"], ["protein"]),
    ("Clear chicken soup", "snack", 90, 3, [], ["protein", "light"]),
    ("Clear vegetable soup", "snack", 60, 0, [], ["light", "fiber"]),
    ("Pomegranate bowl", "snack", 90, 0, [], ["iron", "light"]),
    ("Sattu drink (roasted gram flour sharbat)", "snack", 140, 0, [], ["protein", "fiber", "lowgi", "iron"]),
    ("Puffed rice (murmura) bhel with vegetables", "snack", 110, 0, ["high_gi"], ["light"]),
    ("Beetroot-carrot juice (no sugar)", "snack", 70, 0, ["potassium", "sugar"], ["iron"]),
    ("Peanut butter on 1 multigrain toast", "snack", 160, 0, ["gluten", "fat"], ["protein"]),

    # ---------------- LUNCH ----------------
    ("Moong dal + 2 phulka + lauki sabzi + salad", "lunch", 420, 0, ["gluten"], ["fiber", "protein", "light"]),
    ("Rajma + brown rice + salad", "lunch", 480, 0, ["potassium"], ["fiber", "protein", "iron"]),
    ("Chole + 2 roti + salad", "lunch", 500, 0, ["gluten", "spicy"], ["fiber", "protein", "iron"]),
    ("Vegetable khichdi with curd", "lunch", 380, 1, ["dairy"], ["light"]),
    ("Palak paneer + 2 roti + salad", "lunch", 480, 1, ["dairy", "gluten", "potassium"], ["iron", "protein"]),
    ("Bhindi sabzi + dal + 1 cup brown rice", "lunch", 430, 0, [], ["fiber", "light"]),
    ("Quinoa vegetable pulao + cucumber raita", "lunch", 420, 1, ["dairy"], ["fiber", "protein", "lowgi"]),
    ("Curd rice with pomegranate", "lunch", 350, 1, ["dairy", "high_gi"], ["light"]),
    ("Soya chunk curry + 2 roti + salad", "lunch", 450, 0, ["soy", "gluten", "protein_heavy"], ["protein"]),
    ("Tofu stir-fried vegetables + brown rice", "lunch", 400, 0, ["soy"], ["protein", "fiber"]),
    ("Sambar rice + vegetable poriyal", "lunch", 420, 0, ["high_gi"], ["light"]),
    ("Light chicken curry + 2 roti + salad", "lunch", 520, 3, ["gluten", "spicy", "purine", "protein_heavy"], ["protein"]),
    ("Grilled fish + brown rice + sauteed vegetables", "lunch", 480, 3, ["purine", "protein_heavy"], ["omega3", "protein"]),
    ("Egg curry + 2 roti + salad", "lunch", 460, 2, ["gluten", "spicy"], ["protein"]),
    ("Chicken-vegetable stir-fry with quinoa", "lunch", 450, 3, ["purine", "protein_heavy"], ["protein", "lowgi"]),
    ("Light fish curry + 1 cup rice + salad", "lunch", 480, 3, ["spicy", "purine", "protein_heavy"], ["omega3", "protein"]),
    ("Ragi roti (2) + dal + seasonal sabzi", "lunch", 420, 0, [], ["fiber", "iron", "lowgi"]),
    ("Bajra khichdi with vegetables + curd", "lunch", 400, 1, ["dairy"], ["iron", "fiber", "lowgi"]),
    ("Jowar roti (2) + palak dal + salad", "lunch", 400, 0, ["potassium"], ["iron", "fiber", "lowgi"]),
    ("Mixed vegetable curry + 2 roti + dal", "lunch", 450, 0, ["gluten"], ["fiber"]),
    ("Masoor dal + 1 cup rice + beans poriyal", "lunch", 430, 0, [], ["iron", "protein", "light"]),

    # ---------------- DINNER (lighter) ----------------
    ("Clear vegetable soup + 2 moong dal cheela", "dinner", 300, 0, [], ["light", "protein", "fiber", "lowgi"]),
    ("Grilled paneer + sauteed vegetables", "dinner", 330, 1, ["dairy"], ["protein", "lowgi"]),
    ("Lauki sabzi + 2 roti + dal", "dinner", 320, 0, ["gluten"], ["light", "fiber"]),
    ("Moong dal khichdi with vegetables", "dinner", 340, 0, [], ["light", "protein"]),
    ("Vegetable dalia khichdi", "dinner", 300, 0, ["gluten"], ["fiber", "lowgi", "light"]),
    ("Palak soup + 1 multigrain toast", "dinner", 230, 0, ["gluten", "potassium"], ["iron", "light"]),
    ("Tofu & vegetable stir-fry (no rice)", "dinner", 280, 0, ["soy"], ["protein", "light", "lowgi"]),
    ("Grilled chicken + steamed vegetables", "dinner", 340, 3, ["purine", "protein_heavy"], ["protein", "light", "lowgi"]),
    ("Egg-white omelette + sauteed vegetables", "dinner", 220, 2, [], ["protein", "light", "lowgi"]),
    ("Baked fish tikka + green salad", "dinner", 320, 3, ["purine", "protein_heavy", "spicy"], ["omega3", "protein", "lowgi"]),
    ("Ragi roti + mixed vegetable sabzi + dal", "dinner", 330, 0, [], ["iron", "fiber", "lowgi"]),
    ("Chicken clear soup + 1 multigrain toast", "dinner", 280, 3, ["gluten"], ["light", "protein"]),
    ("Masoor dal + small portion rice + salad", "dinner", 360, 0, [], ["iron", "protein"]),
    ("Sprouts-quinoa salad bowl", "dinner", 290, 0, [], ["fiber", "protein", "lowgi", "light"]),
    ("Bottle-gourd (lauki) soup + 1 jowar roti", "dinner", 240, 0, [], ["light", "fiber", "lowgi"]),
    ("Paneer-vegetable wrap (whole wheat)", "dinner", 340, 1, ["dairy", "gluten"], ["protein"]),
    ("Egg curry (light) + 1 roti", "dinner", 330, 2, ["gluten", "spicy"], ["protein"]),
    ("Vegetable stew with 1 cup steamed rice", "dinner", 330, 0, [], ["light"]),
]

# ---------------------------------------------------------------------------
# Disease rules
# ---------------------------------------------------------------------------
DISEASE_RULES = {
    "diabetes": {
        "label": "Diabetes",
        "exclude": ["sugar", "high_gi"], "prefer": ["fiber", "lowgi"],
        "avoid": ["Sugar, sweets, mithai, jaggery", "Fruit juices and sweetened drinks", "White rice / maida in large portions", "Potato-heavy and fried snacks"],
        "include": ["High-fibre foods: oats, ragi, millets, dals, sprouts", "Non-starchy vegetables at every meal", "Protein with every meal to blunt sugar spikes"],
        "tips": ["Do not skip meals; keep gaps of 3-4 hours.", "A 10-15 minute walk after lunch and dinner helps control blood sugar.", "Check blood sugar regularly as advised by your doctor."],
    },
    "hypertension": {
        "label": "Hypertension (high BP)",
        "exclude": ["sodium", "fat"], "prefer": ["fiber", "light"],
        "avoid": ["Pickles, papad, chips, instant noodles", "Extra table salt; processed / canned foods", "Deep-fried and very oily food"],
        "include": ["Fruits & vegetables (potassium) - DASH style eating", "Garlic, flaxseeds, oats", "Low-fat dairy"],
        "tips": ["Keep salt under 5 g (about 1 tsp) a day.", "Avoid heavy exercise; prefer brisk walking, yoga and pranayama.", "Limit tea/coffee and manage stress."],
    },
    "high_cholesterol": {
        "label": "High cholesterol",
        "exclude": ["fat"], "prefer": ["fiber", "omega3"],
        "avoid": ["Fried food, bakery items, vanaspati / trans fats", "Red meat, organ meat, full-fat dairy", "Excess butter and ghee"],
        "include": ["Oats, barley, beans, soluble-fibre foods", "Nuts (almonds, walnuts), flaxseeds, fatty fish", "Olive / mustard / rice-bran oil in small amounts"],
        "tips": ["Aim for at least 150 minutes of moderate exercise per week.", "Repeat your lipid profile as advised by your doctor."],
    },
    "heart_disease": {
        "label": "Heart disease",
        "exclude": ["fat", "sodium", "sugar"], "prefer": ["omega3", "fiber", "light"],
        "avoid": ["Fried and processed food, trans fats", "High-salt foods, sugary drinks", "Large heavy meals late at night"],
        "include": ["Omega-3 (flaxseed, walnuts, fish)", "Whole grains, fruits, vegetables", "Small, frequent, light meals"],
        "tips": ["Only gentle activity (walking, light yoga) unless your cardiologist clears more.", "Stop exercise and seek medical help for chest pain or breathlessness."],
    },
    "thyroid": {
        "label": "Thyroid disorder",
        "exclude": ["soy"], "prefer": ["protein"],
        "avoid": ["Soy products close to medicine time", "Excess raw cruciferous veg (cabbage, cauliflower, broccoli) - cook them", "Highly processed food"],
        "include": ["Iodised salt in normal amounts", "Selenium / zinc: nuts, seeds, eggs, whole grains", "Plenty of fibre and water"],
        "tips": ["Thyroid medicine (if prescribed) is best taken on an empty stomach, 30-60 min before breakfast - follow your doctor's advice.", "Keep a gap of 4 hours between thyroid medicine and calcium/iron supplements."],
    },
    "pcos": {
        "label": "PCOS / PCOD",
        "exclude": ["sugar", "high_gi"], "prefer": ["fiber", "lowgi", "protein"],
        "avoid": ["Sugary drinks, sweets, refined flour (maida)", "Highly processed / packaged snacks", "Skipping meals"],
        "include": ["Low-GI foods: millets, oats, legumes", "Protein and healthy fats (nuts, seeds)", "Anti-inflammatory foods: turmeric, leafy greens"],
        "tips": ["Strength training 3 days a week improves insulin sensitivity.", "Regular sleep and stress control help hormonal balance."],
    },
    "anemia": {
        "label": "Anemia (iron deficiency)",
        "exclude": [], "prefer": ["iron"],
        "avoid": ["Tea / coffee within 1 hour of meals (blocks iron absorption)", "Calcium supplements together with iron-rich meals"],
        "include": ["Iron-rich foods: spinach, beetroot, pomegranate, dates, ragi, sprouts, eggs, fish", "Vitamin C (lemon, amla, guava) with meals to boost absorption", "Cook in an iron kadhai"],
        "tips": ["Get haemoglobin re-checked as advised by your doctor.", "Add a squeeze of lemon on dal, salad and sabzi."],
    },
    "obesity": {
        "label": "Obesity / weight management",
        "exclude": ["fat", "sugar"], "prefer": ["light", "fiber", "protein"],
        "avoid": ["Sugary drinks, sweets, bakery items", "Fried snacks and fast food", "Late-night eating"],
        "include": ["Protein + fibre at every meal for fullness", "Plenty of vegetables and salads", "Smaller portions, slower eating"],
        "tips": ["Aim for 0.25-0.5 kg weight loss per week - slow and steady.", "Low-impact activity first (walking, cycling, swimming) to protect your joints."],
    },
    "kidney_disease": {
        "label": "Kidney disease",
        "exclude": ["sodium", "potassium", "protein_heavy"], "prefer": ["light"],
        "avoid": ["High-potassium foods: banana, coconut water, potato, tomato, spinach (unless your nephrologist allows)", "Salt and processed foods", "High-protein supplements"],
        "include": ["Low-potassium vegetables (cabbage, cauliflower, bottle gourd)", "Controlled protein portions as per your nephrologist"],
        "tips": ["IMPORTANT: fluid, protein and potassium limits are individual - follow your nephrologist / renal dietitian strictly.", "The water target below is only a general figure; do not exceed your prescribed fluid limit."],
    },
    "gastritis_acidity": {
        "label": "Gastritis / acidity",
        "exclude": ["spicy", "fat"], "prefer": ["light"],
        "avoid": ["Spicy, fried and very oily food", "Excess tea, coffee, carbonated drinks", "Eating very late at night or skipping meals"],
        "include": ["Small frequent meals", "Bananas (if allowed), oats, rice, curd, coconut water", "Fennel (saunf) after meals"],
        "tips": ["Do not lie down for 2-3 hours after dinner.", "Avoid intense exercise on an empty stomach."],
    },
    "gout_uric_acid": {
        "label": "Gout / high uric acid",
        "exclude": ["purine"], "prefer": ["light"],
        "avoid": ["Red meat, organ meat, shellfish, some fish", "Alcohol (especially beer) and sugary drinks", "Excess lentils / mushrooms / cauliflower at once"],
        "include": ["Plenty of water (2.5-3 L unless restricted)", "Low-fat dairy, cherries, vitamin C foods", "Whole grains and vegetables"],
        "tips": ["Hydration helps flush uric acid.", "Avoid crash dieting; gradual weight loss only."],
    },
    "lactose_intolerance": {
        "label": "Lactose intolerance",
        "exclude": ["dairy"], "prefer": [],
        "avoid": ["Milk, paneer, cheese, ice-cream, regular curd (varies per person)"],
        "include": ["Calcium from ragi, sesame, almonds, leafy greens", "Lactose-free milk / plant milks fortified with calcium"],
        "tips": ["Check packaged-food labels for milk solids and whey."],
    },
    "gluten_intolerance": {
        "label": "Gluten intolerance / celiac",
        "exclude": ["gluten"], "prefer": [],
        "avoid": ["Wheat (roti, bread, semolina, dalia), barley, rye, maida", "Packaged foods with hidden gluten (sauces, soups)"],
        "include": ["Ragi, jowar, bajra, rice, quinoa, millets", "Naturally gluten-free dals, vegetables, fruits"],
        "tips": ["Buy certified gluten-free oats only."],
    },
}
