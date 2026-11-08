from contextlib import asynccontextmanager
from typing import AsyncGenerator
import joblib
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, select, desc

from housepriceprediction.config import MODELS_DIR
from housepriceprediction.api.schemas import (
    HouseFeatures,
    PredictionResponse,
    PredictionRead,
)
from housepriceprediction.api.database import create_db_and_tables, get_session, PredictionRecord

MODEL_PATH = MODELS_DIR / "model.joblib"

ml_models: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Loads the ML pipeline and initializes the database upon startup."""
    print(f"Starting up application: {app.title}...")
    create_db_and_tables()
    print("Database and tables verified/created successfully.")

    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model file not found at {MODEL_PATH}. Run 'uv run train' first!")

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
def predict_price(
    features: HouseFeatures, session: Session = Depends(get_session)
) -> PredictionResponse:
    """Receives validated web form features, computes prediction, saves to DB,

    and returns the predicted house price in USD.
    """
    if "pipeline" not in ml_models or ml_models["pipeline"] is None:
        raise HTTPException(status_code=503, detail="Model is not loaded yet.")

    pipeline = ml_models["pipeline"]
    input_data = features.to_model_frame()

    prediction = pipeline.predict(input_data)
    predicted_price = round(float(prediction[0]), 2)

    db_record = PredictionRecord(
        features=features.model_dump(),
        predicted_price=predicted_price,
    )
    session.add(db_record)
    session.commit()
    session.refresh(db_record)

    return PredictionResponse(predicted_price=predicted_price)


@app.get("/predictions", response_model=list[PredictionRead])
def get_predictions(
    limit: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_session),
) -> list[PredictionRecord]:
    """Retrieves the most recent house price estimations from the database."""
    statement = select(PredictionRecord).order_by(desc(PredictionRecord.created_at), desc(PredictionRecord.id)).limit(limit)
    records = session.exec(statement).all()
    return list(records)
