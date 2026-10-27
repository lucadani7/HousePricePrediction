# Preprocessing Specification

This document serves as the single source of truth for the data preprocessing pipeline in the House Price Prediction project. All steps defined here will be implemented in Phase 2 (Preprocessing Pipeline).

---

## 1. Execution Order & Rule
* **Sequential Flow:** The preprocessing steps below **must be executed strictly in the numerical order listed**. Operations like missing value imputation happen *before* categorical encoding.

## 2. Data Reading & Ingestion
* **Pandas CSV Reading Options:** `keep_default_na=False`, `na_values=["NA"]`. This ensures explicit control over missing values without pandas misinterpreting words like `"None"` or `"NA"`.

## 3. Target Variable (`SalePrice`)
* **Separation:** `SalePrice` is isolated from the feature matrix immediately.
* **Transformation:** Logarithmic transformation `np.log1p(SalePrice)` is applied for training models to stabilize variance and optimize relative/percentage errors.
* **Inverse Transformation:** Final predictions are converted back using `np.expm1()`.

## 4. Row Filtering (Training Set Only)
* **Outliers:** Drop houses where `GrLivArea > 4000` **strictly from the training dataset** to prevent leverage points from skewing regression coefficients. 
* *Note on Production:* The web application/inference pipeline must enforce a hard limit or display a warning for user inputs exceeding 4,000 sq ft, as the model is not trained on mansions of this size.

## 5. Column Dropping

To reduce noise, eliminate redundant metadata, and handle near-constant features, specific columns are dropped at distinct stages of the data workflow:

### 5.1. Metadata and Target Separation (Pre-Pipeline)
* **`Id`**: Treated as a primary identifier for tracking and submission generation. It contains no predictive signal for housing valuation and is separated from the feature matrix at the data loading stage before entering the scikit-learn Pipeline. This ensures compatibility with web form inference where an ID is not present.
* **`SalePrice`**: The target variable. It is extracted as the target vector ($y$) during training and is entirely absent in the test set and production requests.

### 5.2. Pipeline-Level Dropping (`ColumnDropper`)
The following features are dropped automatically inside the scikit-learn Pipeline using the `ColumnDropper` transformer due to extreme class imbalance, near-zero variance, or redundancy:
* **`GarageYrBlt`**: Highly redundant with `YearBuilt` and prone to missing values.
* **`Street`**: Extremely skewed categorical feature (almost all properties share the same road type).
* **`Utilities`**: Practically constant across the entire dataset (almost all entries are "AllPub").
* **`Condition2`**: Redundant with `Condition1` and highly skewed.
* **`RoofMatl`**: Extremely dominant category ("CompShg"), offering virtually no split variance for models.
* **`Heating`**: Extremely dominant category ("GasA").
* **`PoolQC`**: Highly sparse feature where the presence of a pool is already fully captured by `PoolArea`.


## 6. Structural Missing Values Handling (ConditionalImputer)

Instead of blind global imputation, the Ames dataset contains clear structural dependencies where the physical absence of an element dictates the imputation value:
- **Pure "None" columns (`Alley`, `Fence`, `MiscFeature`)**: Absence represents a simple negation of the feature and is filled directly with `"None"`.
- **Parent-Dependent Structural Groups**:
  - **Basement (`TotalBsmtSF` as parent)**: If the basement area is 0 or missing, the related numeric columns receive `0` and categorical columns (`BsmtQual`, `BsmtCond`, etc.) receive `"None"`. If the basement exists, missing values are imputed with the median (numeric) or mode (categorical) calculated **strictly on houses that have a basement**.
  - **Garage (`GarageType` as parent)**: If the garage type is missing/absent, details receive `0` / `"None"`. If the garage exists, statistics learned from the subset of houses with a garage are imputed.
  - **Exterior Veneer (`MasVnrArea` as parent)**: An area of 0 or missing implies the absence of veneer (`"None"`), while a non-zero area enforces imputing the type with the mode calculated on houses with veneer.
  - **Fireplace (`Fireplaces` as parent)**: A fireplace count equal to 0 causes `FireplaceQu` to be `"None"`.
  - 
### Other Missing Values
* **LotFrontage:** Imputed using the **median value of the respective Neighborhood** (computed strictly on training data), via `NeighborhoodMedianImputer`.
* **Electrical:** Imputed with the most frequent value (**mode** of the training set, fallback to `'SBrkr'`).
* **Functional:** Imputed with its standard default value (`'Typ'`), as stated in `data_description.txt`.
* **General Pipeline Defaults:** Remaining unhandled numerical columns receive the **median** (computed on train), and remaining categorical columns receive the **mode** (computed on train).

## 7. Feature Engineering & Transformations
* **PoolArea:** Transformed into a binary indicator feature: `HasPool` (`1` if `PoolArea > 0`, else `0`), replacing the continuous area since 99.5% of houses have no pool.
* **MoSold (Month Sold):** Treated as a **categorical variable** (nominal) rather than a continuous quantity, as months represent a cyclic calendar timeline.

## 8. Categorical Encoding Strategy

### A. Standard Ordinal Features (9 columns)
Because missing values are already imputed to `"None"` in Step 6, the mapping applies directly to `"None"` and the standard quality scales:
* `"None"` $\to$ `0`
* `Po` $\to$ `1`
* `Fa` $\to$ `2`
* `TA` $\to$ `3`
* `Gd` $\to$ `4`
* `Ex` $\to$ `5`

*(Note: `PoolQC` is excluded from this list as it is dropped due to near-constancy).*

### B. Custom Ordinal Features (5 columns)
Features with custom hierarchical scales are mapped explicitly using domain definitions from `data_description.txt`:
1. **`BsmtExposure`**: `"None"` $\to$ `0`, `No` $\to$ `1`, `Mn` $\to$ `2`, `Av` $\to$ `3`, `Gd` $\to$ `4`
2. **`BsmtFinType1` & `BsmtFinType2`**: `"None"` $\to$ `0`, `Unf` $\to$ `1`, `LwQ` $\to$ `2`, `Rec` $\to$ `3`, `BLQ` $\to$ `4`, `ALQ` $\to$ `5`, `GLQ` $\to$ `6`
3. **`GarageFinish`**: `"None"` $\to$ `0`, `Unf` $\to$ `1`, `RFn` $\to$ `2`, `Fin` $\to$ `3`
4. **`Functional`**: `Sal` $\to$ `1`, `Sev` $\to$ `2`, `Maj2` $\to$ `3`, `Maj1` $\to$ `4`, `Mod` $\to$ `5`, `Min2` $\to$ `6`, `Min1` $\to$ `7`, `Typ` $\to$ `8`

### C. Nominal Features (including `MSSubClass`)
* **Rare Category Grouping:** Categories with fewer than 10 occurrences in the training set are automatically grouped into an `"Other"` category.
* **One-Hot Encoding:** Applied to all nominal categories after rare grouping.

## 9. Core Preprocessing Rules

* **Rule A (No Data Leakage):** All statistical parameters required for preprocessing (medians, modes, frequency thresholds for rare categories) **must be learned exclusively from the training split** and applied to the validation/test splits.
* **Rule B (Handling Unseen Data):** 
  * Unseen categorical values encountered during validation, testing, or web inference are automatically bucketed into `"Other"`.
  * Unexpected missing values in production fallback to the default imputation values learned during training (or conditional `0` for structural absences).

## 10. Multicollinearity & Feature Selection Note
* Highly correlated structural pairs (e.g., `GarageCars` & `GarageArea`, `TotalBsmtSF` & `1stFlrSF`) will be addressed during modeling (e.g., via L2 regularization / Ridge regression or selective dropping).
