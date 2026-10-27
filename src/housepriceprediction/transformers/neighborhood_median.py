import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted


class NeighborhoodMedianImputer(BaseEstimator, TransformerMixin):
    """Imputes missing values in a target numerical column (e.g., LotFrontage)
    using the median value grouped by a categorical column (e.g., Neighborhood).
    Falls back to the global median for unseen categories or all-NaN groups.
    """

    def __init__(self, col_to_impute: str = "LotFrontage", groupby_col: str = "Neighborhood"):
        self.col_to_impute = col_to_impute
        self.groupby_col = groupby_col

    def fit(self, X: pd.DataFrame, y=None):
        self.medians_ = X.groupby(self.groupby_col)[self.col_to_impute].median().to_dict()
        self.global_median_ = X[self.col_to_impute].median()
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        # Ensure the transformer has been fitted
        check_is_fitted(self, attributes=["medians_", "global_median_"])

        X_out = X.copy()

        # Fail fast if required columns are missing
        missing_cols = [col for col in [self.col_to_impute, self.groupby_col] if col not in X_out.columns]
        if missing_cols:
            raise KeyError(f"Missing required columns in dataframe: {missing_cols}")

        # Identify missing values in the target column
        mask = X_out[self.col_to_impute].isna()
        if not mask.any():
            return X_out

        # Map neighborhood to learned medians
        mapped_medians = X_out[self.groupby_col].map(self.medians_)

        # Fallback to global median for unseen neighborhoods or neighborhoods with NaN medians
        mapped_medians = mapped_medians.fillna(self.global_median_)

        # Fill missing values only where the mask is True
        X_out.loc[mask, self.col_to_impute] = mapped_medians[mask]

        return X_out
