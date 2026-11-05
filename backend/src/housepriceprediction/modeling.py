from typing import Final

import numpy as np
from sklearn.base import RegressorMixin
from sklearn.compose import TransformedTargetRegressor
from sklearn.linear_model import Lasso
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from housepriceprediction.preprocessing import build_preprocessor
from housepriceprediction.transformers import FormInputMasker

FINAL_LASSO_ALPHA: Final = 0.003


def build_lasso_pipeline(alpha: float = FINAL_LASSO_ALPHA) -> Pipeline:
    """The chosen final model: Lasso on scaled features."""
    return model_pipeline(Lasso(alpha=alpha, max_iter=50000), scale=True)


def model_pipeline(regressor: RegressorMixin, *, scale: bool) -> Pipeline:
    """Preprocessing + (optional) scaling + regressor.

    `scale` has no default on purpose: linear models need it (scale=True),
    tree models and the baseline do not (scale=False), and forgetting it must be impossible.
    """
    preprocessor = ("preprocessor", build_preprocessor(add_derived=True))
    model = ("regressor", regressor)
    if scale:
        return Pipeline([preprocessor, ("scaler", StandardScaler()), model])
    return Pipeline([preprocessor, model])


def build_final_pipeline() -> TransformedTargetRegressor:
    """Returns the final end-to-end regression pipeline wrapped with TransformedTargetRegressor.

    The pipeline handles form input masking, feature engineering, scaling, and Lasso regression.
    The target variable must be provided in original dollar scale (not log-transformed),
    as TransformedTargetRegressor handles log1p and expm1 transformations internally.
    """
    inner_pipeline = Pipeline([
        ("form", FormInputMasker()),
        ("model", build_lasso_pipeline()),
    ])

    return TransformedTargetRegressor(
        regressor=inner_pipeline,
        func=np.log1p,
        inverse_func=np.expm1,
    )
