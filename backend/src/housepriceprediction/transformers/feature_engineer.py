import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

DEFAULT_COLS_TO_STR = ("MSSubClass", "MoSold")
DERIVED_COMPONENTS = (
    "TotalBsmtSF", "1stFlrSF", "2ndFlrSF",
    "FullBath", "HalfBath", "BsmtFullBath", "BsmtHalfBath",
    "WoodDeckSF", "OpenPorchSF", "EnclosedPorch", "3SsnPorch", "ScreenPorch"
)


class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Transformer that performs feature engineering steps:
    - Creates binary 'HasPool' from 'PoolArea' and drops 'PoolArea'.
    - Safely converts specified numerical columns to strings without float artifacts (.0).
    - Calculates aggregated architectural features if add_derived=True.
    """

    def __init__(self, cols_to_str=None, add_derived: bool = True):
        self.cols_to_str = cols_to_str
        self.add_derived = add_derived

    def _get_cols_to_str(self):
        return self.cols_to_str if self.cols_to_str is not None else DEFAULT_COLS_TO_STR

    @staticmethod
    def _convert_val(val):
        if pd.isna(val):
            return val
        try:
            f_val = float(val)
            if f_val.is_integer():
                return str(int(f_val))
            return str(val)
        except (ValueError, TypeError):
            return str(val)

    def fit(self, X: pd.DataFrame, y=None):
        # Unsupervised transformer: nothing to learn
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        cols_to_convert = self._get_cols_to_str()

        # Fail-fast validation
        required = ["PoolArea"] + list(cols_to_convert)
        if self.add_derived:
            required.extend(DERIVED_COMPONENTS)

        missing = [c for c in required if c not in X.columns]
        if missing:
            raise KeyError(f"Missing required columns in DataFrame: {missing}")

        X_out = X.copy()

        # 1. Pool feature engineering
        pool_area = pd.to_numeric(X_out["PoolArea"], errors="coerce").fillna(0)
        X_out["HasPool"] = (pool_area > 0).astype(int)
        X_out = X_out.drop(columns=["PoolArea"])

        # 2. Safe categorical string conversion
        for col in cols_to_convert:
            X_out[col] = X_out[col].apply(self._convert_val)

        # 3. Derived Features
        if self.add_derived:
            X_out["TotalSF"] = X_out["TotalBsmtSF"] + X_out["1stFlrSF"] + X_out["2ndFlrSF"]

            X_out["TotalBath"] = (
                X_out["FullBath"] + 0.5 * X_out["HalfBath"] +
                X_out["BsmtFullBath"] + 0.5 * X_out["BsmtHalfBath"]
            )

            X_out["TotalPorchSF"] = (
                X_out["WoodDeckSF"] + X_out["OpenPorchSF"] +
                X_out["EnclosedPorch"] + X_out["3SsnPorch"] + X_out["ScreenPorch"]
            )

        return X_out

