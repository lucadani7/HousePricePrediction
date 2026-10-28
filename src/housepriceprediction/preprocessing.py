from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

from housepriceprediction.features import (
    DERIVED_COLUMNS,
    NOMINAL_COLUMNS,
    NUMERIC_COLUMNS,
    ORDINAL_CATEGORIES,
    ORDINAL_COLUMNS,
)
from housepriceprediction.transformers import (
    ColumnDropper,
    ConditionalImputer,
    FeatureEngineer,
    NeighborhoodMedianImputer,
)


def make_functional_pipeline() -> Pipeline:
    """Fill missing Functional values with 'Typ', then encode the ordered scale as integers."""
    return Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="Typ")),
        ("encode", OrdinalEncoder(categories=[list(ORDINAL_CATEGORIES["Functional"])])),
    ])


def make_ordinal_pipeline() -> Pipeline:
    """Fill missing values with most frequent, then encode standard ordinal categories."""
    return Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OrdinalEncoder(categories=[list(ORDINAL_CATEGORIES[c]) for c in ORDINAL_COLUMNS])),
    ])


def make_nominal_pipeline() -> Pipeline:
    """Fill missing nominal values with most frequent, then one-hot encode handling infrequent categories."""
    return Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        (
            "encode",
            OneHotEncoder(
                handle_unknown="infrequent_if_exist",
                min_frequency=10,
                sparse_output=False,
            ),
        ),
    ])


def make_numeric_pipeline() -> Pipeline:
    """Fill missing numeric values with median."""
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
    ])


def build_preprocessor(add_derived: bool = True) -> Pipeline:
    """Full preprocessing pipeline: raw Ames features in, numeric matrix out."""
    numeric_features = list(NUMERIC_COLUMNS)
    if add_derived:
        numeric_features.extend(DERIVED_COLUMNS)

    encoder = ColumnTransformer(
        [
            ("functional", make_functional_pipeline(), ["Functional"]),
            ("ordinal", make_ordinal_pipeline(), list(ORDINAL_COLUMNS)),
            ("nominal", make_nominal_pipeline(), list(NOMINAL_COLUMNS)),
            ("numeric", make_numeric_pipeline(), numeric_features),
        ],
        verbose_feature_names_out=False,
    ).set_output(transform="pandas")

    return Pipeline([
        ("drop", ColumnDropper()),
        ("conditional", ConditionalImputer()),
        ("lot_frontage", NeighborhoodMedianImputer()),
        ("features", FeatureEngineer(add_derived=add_derived)),
        ("encode", encoder),
    ])
