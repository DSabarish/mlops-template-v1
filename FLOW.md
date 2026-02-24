# MLOps Single-Repo Flow: Terraform Infra + ML Pipeline (CI/CD)

One repo, two concerns (as in [gpt.md](gpt.md)):

- **Terraform** = *provision infrastructure* (unchanged)
- **CI/CD** = run ML pipeline, tests, deploy app to Cloud Run

Two GitHub Actions workflows:

1. **terraform-infra** – provisions GCP (buckets, BigQuery, Artifact Registry, service accounts).
2. **ml-cicd** – pipeline (generate → BQ → GCS → clean → transform → train), pytest, deploy to Cloud Run.

---

## Pipeline (CI)

1. **generate_data.py** – 100 records, 5 cols (f1..f5), 1 target (T).
2. **bq_ingestion.py** – save data to BigQuery (Terraform-created table).
3. **gcs_ingestion.py** – query BQ, save to GCS data bucket (versioned: `data/<version>/data.csv`).
4. **clean.py** – drop nulls, drop duplicates, validate schema.
5. **transformation.py** – produce X (f1..f5), y (T) for training.
6. **train.py** – LinearRegression; save to GCS artifacts bucket: `models/latest/` + `models/v_<timestamp>/`.
7. **inference.py** – FastAPI: load model from path (env `MODEL_PATH` or GCS latest), `POST /predict` returns prediction.
8. **frontend/index.html** – form with f1..f5; on submit calls FastAPI `/predict`, shows result.

**Heavy lifting:** Training can be moved to **Vertex AI custom job** via `vertex_train.py` (entrypoint for a custom container/job).

---

## CI/CD (GitHub Actions)

- **tf-outputs** – read Terraform outputs (from GCS state or secrets).
- **pipeline** – run `run_pipeline.py` (generate → BQ → GCS → clean → transform → train).
- **test** – `pytest tests/` (2 test cases: clean drops nulls, predict returns float).
- **deploy** – build Docker image (FastAPI + frontend), push to Artifact Registry, `gcloud run deploy app`.

Cloud Run is **not** in Terraform; the first deploy creates the service. Env passed to Cloud Run: `GCP_PROJECT`, `ARTIFACTS_BUCKET` (model is loaded from GCS latest).

---

## Repo Layout

```
├── .github/workflows/
│   ├── terraform-infra.yml
│   └── ml-cicd.yml
├── terraform/              # unchanged
├── ML-code/
│   ├── config.py
│   ├── generate_data.py
│   ├── bq_ingestion.py
│   ├── gcs_ingestion.py
│   ├── clean.py
│   ├── transformation.py
│   ├── train.py
│   ├── inference.py       # FastAPI
│   ├── vertex_train.py   # Vertex AI custom job entrypoint
│   ├── run_pipeline.py
│   ├── data/
│   └── requirements.txt
├── frontend/
│   └── index.html
├── tests/
│   ├── conftest.py
│   ├── test_clean.py
│   └── test_inference.py
├── Dockerfile
└── FLOW.md
```

---

## Local Run

1. **Pipeline:** Set `GOOGLE_APPLICATION_CREDENTIALS`, then  
   `python ML-code/run_pipeline.py`
2. **Tests:** `PYTHONPATH=ML-code python -m pytest tests/ -v`
3. **API:** `cd ML-code && uvicorn inference:app --reload` then open `frontend/index.html` (set API base to `http://localhost:8000` if needed).

---

## GitHub Secrets

- `GCP_SA_KEY` – JSON key for GCP (pipeline, deploy, tf-outputs).
- `TF_STATE_BUCKET` – (optional) GCS bucket for Terraform state.
- If no state: `GCP_PROJECT`, `DATA_BUCKET`, `ARTIFACTS_BUCKET`, `DATASET_ID`, `TABLE_ID`, `ARTIFACT_REPO_URL`.
