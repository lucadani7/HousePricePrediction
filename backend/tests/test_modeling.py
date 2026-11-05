import pytest

from housepriceprediction.data import TRAIN_CSV, load_training_data
from housepriceprediction.features import FORM_FEATURES
from housepriceprediction.modeling import build_final_pipeline

DATA_PATH = TRAIN_CSV


@pytest.mark.skipif(not DATA_PATH.exists(), reason="train.csv data file not found")
def test_final_pipeline_end_to_end():
    """Tests training the final pipeline with dollar targets loaded centrally

    and predicting on a restricted DataFrame containing only the 16 web form features.
    """
    # Load standardized training data using the centralized data module
    X, y = load_training_data()

    # Instantiate and fit the final pipeline
    pipeline = build_final_pipeline()
    pipeline.fit(X, y)

    # Simulate web form input: select only the 16 required form features for a few houses
    form_subset = X[list(FORM_FEATURES)].head(5)

    # Make predictions
    predictions = pipeline.predict(form_subset)

    # Verify predictions output format and reasonable price bounds ($30k to $800k)
    assert len(predictions) == 5
    for pred in predictions:
        assert isinstance(pred, (float, int))
        assert 30000.0 <= pred <= 800000.0, f"Prediction out of bounds: {pred}"