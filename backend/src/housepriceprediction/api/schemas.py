from typing import Literal
import pandas as pd
from pydantic import BaseModel, Field, model_validator

Neighborhood = Literal[
    "Blmngtn", "Blueste", "BrDale", "BrkSide", "ClearCr",
    "CollgCr", "Crawfor", "Edwards", "Gilbert", "IDOTRR",
    "MeadowV", "Mitchel", "NAmes", "NoRidge", "NPkVill",
    "NridgHt", "NWAmes", "OldTown", "SWISU", "Sawyer",
    "SawyerW", "Somerst", "StoneBr", "Timber", "Veenker"
]

KitchenQuality = Literal["Ex", "Gd", "TA", "Fa", "Po"]
ZoningClassification = Literal["C (all)", "FV", "RH", "RL", "RM"]


class HouseFeatures(BaseModel):
    """Pydantic model representing the 16 web form features with validation

    and automatic serialization mapping to scikit-learn feature names.
    """
    first_floor_sf: int = Field(gt=0, serialization_alias="1stFlrSF")
    second_floor_sf: int = Field(ge=0, serialization_alias="2ndFlrSF")
    total_bsmt_sf: int = Field(ge=0, serialization_alias="TotalBsmtSF")
    bsmt_fin_sf1: int = Field(ge=0, serialization_alias="BsmtFinSF1")
    overall_quality: int = Field(ge=1, le=10, serialization_alias="OverallQual")
    overall_condition: int = Field(ge=1, le=10, serialization_alias="OverallCond")
    kitchen_quality: KitchenQuality = Field(serialization_alias="KitchenQual")
    year_built: int = Field(ge=1800, le=2026, serialization_alias="YearBuilt")
    year_remod_add: int = Field(ge=1800, le=2026, serialization_alias="YearRemodAdd")
    neighborhood: Neighborhood = Field(serialization_alias="Neighborhood")
    ms_zoning: ZoningClassification = Field(serialization_alias="MSZoning")
    lot_area: int = Field(gt=0, serialization_alias="LotArea")
    garage_cars: int = Field(ge=0, le=5, serialization_alias="GarageCars")
    full_bath: int = Field(ge=0, le=5, serialization_alias="FullBath")
    half_bath: int = Field(ge=0, le=4, serialization_alias="HalfBath")
    fireplaces: int = Field(ge=0, le=5, serialization_alias="Fireplaces")

    @model_validator(mode="after")
    def validate_house_rules(self) -> "HouseFeatures":
        """Enforces cross-field consistency and training data constraints."""
        if self.year_remod_add < self.year_built:
            raise ValueError("Year remod add cannot be earlier than year built.")
        if self.bsmt_fin_sf1 > self.total_bsmt_sf:
            raise ValueError("Finished basement area cannot exceed total basement area.")
        if (self.first_floor_sf + self.second_floor_sf) > 4000:
            raise ValueError("Total above ground square footage cannot exceed 4000 sq ft.")
        return self

    def to_model_frame(self) -> pd.DataFrame:
        """Converts validated features into a pandas DataFrame using model-expected names."""
        return pd.DataFrame([self.model_dump(by_alias=True)])


class PredictionResponse(BaseModel):
    """Response schema returning the predicted house price in dollars."""
    predicted_price: float