# NutriPlan – ML-Based Lifestyle & Nutritional Assessment Framework (MLOps project)

A user fills a web form (age, height, weight, diet type, diseases, lifestyle).
The app returns a **health-risk assessment (ML model)** and a **weekly timetable**
(wake-up, exercise, breakfast, snacks, lunch, dinner, water, medicine reminders, sleep)
matched to the user's **diet** (vegan / vegetarian / eggetarian / non-veg) and **diseases**
(diabetes, BP, cholesterol, heart, thyroid, PCOS, anemia, obesity, kidney, acidity, gout,
lactose / gluten intolerance). It can be printed / saved as PDF.

## Run in VS Code (3 steps)
1. Unzip, then **File → Open Folder…** → `nutrition_mlops`
2. Open the terminal (**Ctrl + `**) and run:
   ```
   python -m venv .venv
   .venv\Scripts\activate          # Windows   (Mac/Linux: source .venv/bin/activate)
   pip install -r requirements.txt
   python run.py
   ```
3. Browser opens at **http://127.0.0.1:8000** – fill the form → *Generate my timetable*.

(First run trains the model automatically. You can also press **F5** → "Run NutriPlan".)

## Mapping to your PPT (MLOps lifecycle)
| Slide topic | Where in this project |
|---|---|
| Data ingestion / validation / cleaning | `src/data_gen.py`, `src/train.py → load_data()` |
| Feature + preprocessing (shared train/serve) | `src/features.py` |
| Model development & comparison | `src/train.py` (LogReg, RandomForest, GradientBoosting) |
| Evaluation table (slide 6) | `models/metrics.json` or `GET /model-info` |
| Experiment tracking | MLflow auto-logging if installed (`pip install mlflow`, `mlflow ui`) |
| Automated testing | `tests/` → `pytest -q` |
| CI/CD | `.github/workflows/ci.yml` |
| Docker | `Dockerfile`, `docker-compose.yml` |
| REST API / serving | `api/main.py` (`POST /api/plan`, `/health`, `/model-info`, `/docs`) |
| Monitoring | `GET /metrics` (Prometheus format), `monitoring/prometheus.yml`, `logs/app.log` |
| Drift detection | `src/drift.py`, `GET /drift` (PSI > 0.2 ⇒ retrain) |
| Retraining / Airflow | `python -m src.train`, `airflow/retrain_dag.py` (planned) |

## Important notes (be honest in your viva / report)
* **Dataset:** no Kaggle data was available offline, so `src/data_gen.py` creates a
  *synthetic* dataset (5000 rows). To use your real Kaggle dataset, save it as
  `data/nutrition.csv` with the same columns (see `src/features.py`) and run
  `python -m src.train`. Fill the PPT placeholders from `models/metrics.json`.
* The timetable is **rule-based** (food database in `src/foods.py`); the ML model predicts the risk level.
* Airflow DAG, Grafana dashboards and cloud deployment are *planned* – mark them PLANNED in the PPT.
* Not medical advice.

## Other commands
```
pytest -q                      # run tests
python -m src.train            # retrain
docker compose up --build      # API :8000, Prometheus :9090, Grafana :3000
```
