import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted

from housepriceprediction.features import FORM_FEATURES


class FormInputMasker(BaseEstimator, TransformerMixin):
    """Transformer that retains specified form features, adds and masks all missing

    non-form columns with learned default values (median for numeric, mode for categorical),
    ensures strict column ordering matching training, and dynamically recalculates GrLivArea.
    """
    defaults_: dict[str, object]
    non_form_features_: list[str]
    feature_names_in_: list[str]

    def __init__(self, form_features: tuple[str, ...] = FORM_FEATURES):
        self.form_features = form_features

    def fit(self, X: pd.DataFrame, y=None) -> "FormInputMasker":
        # Check that all form features exist in the input dataframe
        missing = [col for col in self.form_features if col not in X.columns]
        if missing:
            raise KeyError(f"Missing required form features in input data: {missing}")

        # Save all column names from training for strict ordering and reconstruction
        self.feature_names_in_ = list(X.columns)

        # Identify columns outside the form, excluding GrLivArea if present
        self.non_form_features_ = [
            col for col in X.columns if col not in self.form_features and col != "GrLivArea"
        ]

        # Learn defaults: median for numeric, mode for categorical/others
        self.defaults_ = {}
        for col in self.non_form_features_:
            if pd.api.types.is_numeric_dtype(X[col]):
                self.defaults_[col] = X[col].median()
            else:
                mode_series = X[col].mode()
                if mode_series.empty:
                    raise ValueError(f"Cannot compute mode for empty or all-NaN column: {col}")
                self.defaults_[col] = mode_series.iloc[0]

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        check_is_fitted(self)

        # Check that all form features exist in input
        missing = [col for col in self.form_features if col not in X.columns]
        if missing:
            raise KeyError(f"Missing required form features in input data: {missing}")

        # Create a copy to ensure immutability of the original input
        X_transformed = X.copy()

        # Add or replace non-form columns with learned default values
        for col, default_val in self.defaults_.items():
            X_transformed[col] = default_val

        # Dynamically recalculate GrLivArea from 1st and 2nd floor areas
        if "1stFlrSF" in X_transformed.columns and "2ndFlrSF" in X_transformed.columns:
            X_transformed["GrLivArea"] = (
                X_transformed["1stFlrSF"] + X_transformed["2ndFlrSF"]
            )

        # Ensure exact column order and presence of all columns as seen during fit
        return X_transformed[self.feature_names_in_]