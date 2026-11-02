from typing import Final

from sklearn.base import RegressorMixin
from sklearn.linear_model import Lasso
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from housepriceprediction.preprocessing import build_preprocessor

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