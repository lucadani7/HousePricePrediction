from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted

DEFAULT_PURE_NONE_COLS = ("Alley", "Fence", "MiscFeature")

@dataclass(frozen=True)
class ConditionalGroup:
    parent_col: str
    is_numeric_parent: bool
    numeric_cols: tuple[str, ...] = ()
    categorical_cols: tuple[str, ...] = ()
    absent_num_val: float = 0
    absent_cat_val: str = "None"

DEFAULT_CONDITIONAL_GROUPS = (
    ConditionalGroup(
        parent_col="TotalBsmtSF",
        is_numeric_parent=True,
        numeric_cols=("BsmtFinSF1", "BsmtFinSF2", "BsmtUnfSF", "TotalBsmtSF", "BsmtFullBath", "BsmtHalfBath"),
        categorical_cols=("BsmtQual", "BsmtCond", "BsmtExposure", "BsmtFinType1", "BsmtFinType2"),
    ),
    ConditionalGroup(
        parent_col="GarageType",
        is_numeric_parent=False,
        numeric_cols=("GarageCars", "GarageArea"),
        categorical_cols=("GarageFinish", "GarageQual", "GarageCond"),
    ),
    ConditionalGroup(
        parent_col="MasVnrArea",
        is_numeric_parent=True,
        numeric_cols=("MasVnrArea",),
        categorical_cols=("MasVnrType",),
    ),
    ConditionalGroup(
        parent_col="Fireplaces",
        is_numeric_parent=True,
        categorical_cols=("FireplaceQu",),
    ),
)


def _is_element_present(series: pd.Series, is_numeric: bool) -> pd.Series:
    match is_numeric:
        case True:
            arr = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
            mask = (~np.isnan(arr)) & (arr > 0)
        case False:
            arr = series.to_numpy()
            mask = (arr != "None") & (arr != "") & (~pd.isna(arr))
    return pd.Series(mask, index=series.index)


def _ensure_object(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series.dtype):
        return series.astype("object")
    return series


class ConditionalImputer(BaseEstimator, TransformerMixin):
    """Imputes missing values using structural conditional rules:

    - Pure 'None' structural NAs.
    - Conditional groups where a parent indicator determines absence vs unknown detail.
    """

    def __init__(self, pure_none_cols=None, conditional_groups=None):
        self.pure_none_cols = pure_none_cols
        self.conditional_groups = conditional_groups

    def _get_pure_none_cols(self):
        return self.pure_none_cols if self.pure_none_cols is not None else DEFAULT_PURE_NONE_COLS

    def _get_conditional_groups(self):
        return self.conditional_groups if self.conditional_groups is not None else DEFAULT_CONDITIONAL_GROUPS

    def _validate_columns(self, X: pd.DataFrame):
        pure_cols = self._get_pure_none_cols()
        groups = self._get_conditional_groups()

        all_needed = list(pure_cols)
        for g in groups:
            all_needed.append(g.parent_col)
            all_needed.extend(g.numeric_cols)
            all_needed.extend(g.categorical_cols)

        missing = [c for c in all_needed if c not in X.columns]
        if missing:
            raise KeyError(f"Missing required columns in DataFrame: {missing}")

    def fit(self, X: pd.DataFrame, y=None):
        self._validate_columns(X)
        self.imputation_stats_ = {}

        groups = self._get_conditional_groups()
        for group in groups:
            parent = group.parent_col
            present_mask = _is_element_present(X[parent], group.is_numeric_parent)
            subset = X.loc[present_mask]

            stats = {}
            for col in group.numeric_cols:
                stats[col] = 0.0 if subset.empty else subset[col].median()

            for col in group.categorical_cols:
                condition = not subset.empty and not subset[col].mode().empty
                stats[col] = subset[col].mode().iloc[0] if condition else group.absent_cat_val

            self.imputation_stats_[parent] = stats

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        check_is_fitted(self, attributes=["imputation_stats_"])
        self._validate_columns(X)

        X_out = X.copy()
        pure_cols = self._get_pure_none_cols()
        groups = self._get_conditional_groups()

        # 1. Handle pure 'None' columns
        for col in pure_cols:
            X_out[col] = _ensure_object(X_out[col]).fillna("None")

        # 2. Handle conditional groups
        for group in groups:
            parent = group.parent_col
            is_num = group.is_numeric_parent
            present_mask = _is_element_present(X_out[parent], is_num)
            absent_mask = ~present_mask

            absent_num = group.absent_num_val
            absent_cat = group.absent_cat_val
            stats = self.imputation_stats_.get(parent, {})

            # Handle parent column itself when absent/missing
            if is_num:
                mask_parent_absent = absent_mask & X_out[parent].isna()
                X_out.loc[mask_parent_absent, parent] = absent_num
            else:
                X_out[parent] = _ensure_object(X_out[parent])
                mask_parent_absent = absent_mask & X_out[parent].isna()
                X_out.loc[mask_parent_absent, parent] = absent_cat

            # Process numeric dependents
            for col in group.numeric_cols:
                mask_absent_col = absent_mask & X_out[col].isna()
                X_out.loc[mask_absent_col, col] = absent_num

                fallback_val = stats.get(col, 0)
                mask_present_col = present_mask & X_out[col].isna()
                X_out.loc[mask_present_col, col] = fallback_val

            # Process categorical dependents
            for col in group.categorical_cols:
                X_out[col] = _ensure_object(X_out[col])
                mask_absent_col = absent_mask & X_out[col].isna()
                X_out.loc[mask_absent_col, col] = absent_cat
                fallback_val = stats.get(col, absent_cat)
                mask_present_col = present_mask & X_out[col].isna()
                X_out.loc[mask_present_col, col] = fallback_val

        return X_out
