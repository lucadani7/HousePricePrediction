import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

DEFAULT_DROP_COLS = (
    "GarageYrBlt",
    "Street",
    "Utilities",
    "Condition2",
    "RoofMatl",
    "Heating",
    "PoolQC",
)


class ColumnDropper(BaseEstimator, TransformerMixin):
    """Transformer that drops specified columns from a pandas DataFrame."""

    def __init__(self, columns=None):
        self.columns = columns

    def _get_columns(self):
        return self.columns if self.columns is not None else DEFAULT_DROP_COLS

    def fit(self, X: pd.DataFrame, y=None):
        # Unsupervised transformer: nothing to learn
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        cols_to_drop = self._get_columns()
        missing = [c for c in cols_to_drop if c not in X.columns]
        if missing:
            raise KeyError(f"Columns to drop not found in DataFrame: {missing}")

        return X.drop(columns=list(cols_to_drop))
