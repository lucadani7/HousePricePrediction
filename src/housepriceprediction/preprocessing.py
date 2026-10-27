from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from housepriceprediction.features import ORDINAL_CATEGORIES


def make_functional_pipeline() -> Pipeline:
    """Fill missing Functional values with 'Typ', then encode the ordered scale as integers."""
    return Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="Typ")),
        ("encode", OrdinalEncoder(categories=[list(ORDINAL_CATEGORIES["Functional"])])),
    ])
