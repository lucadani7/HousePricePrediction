# House Price Prediction - backend

Python package `housepriceprediction`: preprocessing, models, training script and FastAPI service.
See the [main README](../README.md) for the project overview and results.

```bash
uv sync                      # install dependencies (Python 3.13 is installed by uv)
uv run train                 # train and save models/model.joblib + models/model.json
uv run uvicorn housepriceprediction.api.main:app --reload    # API on http://localhost:8000
uv run pytest                # tests
```

The training data (`train.csv`, `test.csv`) must be downloaded from Kaggle into `data/raw/`.
