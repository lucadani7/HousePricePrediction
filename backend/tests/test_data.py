import pytest

from housepriceprediction.data import TRAIN_CSV, load_training_data

DATA_PATH = TRAIN_CSV


@pytest.mark.skipif(not DATA_PATH.exists(), reason="train.csv data file not found")
def test_load_training_data_properties():
    """Verifies that load_training_data correctly loads features and target

    adhering to row counts, column exclusions ('Id', 'SalePrice'), and dollar scale.
    """
    X, y = load_training_data()

    # 1. Verify target y is in dollars (not log-transformed, e.g., mean price is around 180k, not ~12)
    assert y.mean() > 50000.0
    assert y.name == "SalePrice"

    # 2. Verify 'Id' and 'SalePrice' are not present in feature set X
    assert "Id" not in X.columns
    assert "SalePrice" not in X.columns

    # 3. Verify row count matches the dataset size minus the 4 filtered outliers (1460 - 4 = 1456)
    assert len(X) == 1456
    assert len(y) == 1456