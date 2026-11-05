from pathlib import Path
from typing import Final

import pandas as pd

from housepriceprediction.config import DATA_RAW, TARGET

# Outlier removal threshold recommended by the dataset author (GrLivArea > 4000 sq ft)
OUTLIER_LIVING_AREA: Final[int] = 4000
TRAIN_CSV: Final[Path] = DATA_RAW / "train.csv"


def load_training_data(filepath: Path = TRAIN_CSV) -> tuple[pd.DataFrame, pd.Series]:
    """Load the Ames training dataset with the project's rules.

    - Applies consistent NA rules (only "NA" is missing; the string "None" stays a category).
    - Removes the outliers with GrLivArea above OUTLIER_LIVING_AREA.
    - Drops the 'Id' column.
    - Returns X (raw features) and y (SalePrice in dollars, NOT log-transformed).
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Training data file not found at: {filepath}")

    df = pd.read_csv(filepath, keep_default_na=False, na_values=["NA"])
    df = df[df["GrLivArea"] <= OUTLIER_LIVING_AREA].reset_index(drop=True)

    y = df[TARGET].copy()
    X = df.drop(columns=["Id", TARGET])
    return X, y
