import joblib
import pandas as pd
import pytest

from housepriceprediction.config import MODELS_DIR

MODEL_PATH = MODELS_DIR / "model.joblib"


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="Saved model.joblib not found. Run 'uv run train' first.")
def test_saved_model_prediction():
    """Loads the serialized model joblib artifact and verifies it can predict

    a reasonable price for a handcrafted sample house containing the 16 form fields.
    """
    model = joblib.load(MODEL_PATH)

    # Handcrafted sample house representing realistic values for the 16 form features
    sample_form_data = pd.DataFrame([{
        "1stFlrSF": 1200,
        "2ndFlrSF": 800,
        "TotalBsmtSF": 1000,
        "BsmtFinSF1": 600,
        "OverallQual": 7,
        "OverallCond": 5,
        "KitchenQual": "Gd",
        "YearBuilt": 2005,
        "YearRemodAdd": 2005,
        "Neighborhood": "CollgCr",
        "MSZoning": "RL",
        "LotArea": 9500,
        "GarageCars": 2,
        "FullBath": 2,
        "HalfBath": 1,
        "Fireplaces": 1,
    }])

    predictions = model.predict(sample_form_data)

    assert len(predictions) == 1
    predicted_price = predictions[0]

    # Verify prediction output is a valid numeric scalar within a realistic range ($30k - $800k)
    assert isinstance(predicted_price, (float, int))
    assert 30000.0 <= predicted_price <= 800000.0, f"Predicted price out of bounds: {predicted_price}"