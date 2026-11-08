from contextlib import asynccontextmanager
from typing import AsyncGenerator
import joblib
from fastapi import FastAPI, HTTPException

from housepriceprediction.config import MODELS_DIR
from housepriceprediction.api.schemas import HouseFeatures, PredictionResponse

MODEL_PATH = MODELS_DIR / "model.joblib"

ml_models: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Loads the trained machine learning pipeline once upon application startup."""
    print(f"Starting up application: {app.title}...")

    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Model file not found at {MODEL_PATH}. Run 'uv run train' first!"
        )

    print(f"Loading model from {MODEL_PATH}...")
    ml_models["pipeline"] = joblib.load(MODEL_PATH)
    yield
    ml_models.clear()


app = FastAPI(
    title="House Price Prediction API",
    description="API for predicting residential property prices based on a 16-field web form.",
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint to verify the API and model availability."""
    status = "ok" if "pipeline" in ml_models else "degraded"
    return {"status": status}


@app.post("/predict", response_model=PredictionResponse)
def predict_price(features: HouseFeatures) -> PredictionResponse:
    """Receives validated web form features, transforms them via Pydantic aliases,

    and returns the predicted house price in USD.
    """
    if "pipeline" not in ml_models or ml_models["pipeline"] is None:
        raise HTTPException(status_code=503, detail="Model is not loaded yet.")

    pipeline = ml_models["pipeline"]
    input_data = features.to_model_frame()

    prediction = pipeline.predict(input_data)
    predicted_price = float(prediction[0])

    return PredictionResponse(predicted_price=round(predicted_price, 2))