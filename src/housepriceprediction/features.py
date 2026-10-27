QUALITY_SCALE = ("None", "Po", "Fa", "TA", "Gd", "Ex")
BSMT_FIN_SCALE = ("None", "Unf", "LwQ", "Rec", "BLQ", "ALQ", "GLQ")

ORDINAL_CATEGORIES = {
    # Standard quality scale (9 columns)
    "ExterQual": QUALITY_SCALE,
    "ExterCond": QUALITY_SCALE,
    "BsmtQual": QUALITY_SCALE,
    "BsmtCond": QUALITY_SCALE,
    "HeatingQC": QUALITY_SCALE,
    "KitchenQual": QUALITY_SCALE,
    "FireplaceQu": QUALITY_SCALE,
    "GarageQual": QUALITY_SCALE,
    "GarageCond": QUALITY_SCALE,

    # Custom scales (5 columns)
    "BsmtExposure": ("None", "No", "Mn", "Av", "Gd"),
    "BsmtFinType1": BSMT_FIN_SCALE,
    "BsmtFinType2": BSMT_FIN_SCALE,
    "GarageFinish": ("None", "Unf", "RFn", "Fin"),
    "Functional": ("Sal", "Sev", "Maj2", "Maj1", "Mod", "Min2", "Min1", "Typ"),
}

# Nominal categorical columns (one-hot encoded)
NOMINAL_COLUMNS = (
    "MSZoning", "LandContour", "LotConfig", "Neighborhood", "Condition1",
    "BldgType", "HouseStyle", "RoofStyle", "Exterior1st", "Exterior2nd",
    "MasVnrType", "Foundation", "CentralAir", "Electrical",
    "GarageType", "PavedDrive", "SaleType", "SaleCondition",
    "MSSubClass", "MoSold", "Alley", "Fence", "MiscFeature",
    "LandSlope", "LotShape"
)

# Numeric features
NUMERIC_COLUMNS = (
    "LotFrontage", "LotArea", "OverallQual", "OverallCond", "YearBuilt",
    "YearRemodAdd", "MasVnrArea", "BsmtFinSF1", "BsmtFinSF2", "BsmtUnfSF",
    "TotalBsmtSF", "1stFlrSF", "2ndFlrSF", "LowQualFinSF", "GrLivArea",
    "BsmtFullBath", "BsmtHalfBath", "FullBath", "HalfBath", "BedroomAbvGr",
    "KitchenAbvGr", "TotRmsAbvGrd", "Fireplaces", "GarageCars", "GarageArea",
    "WoodDeckSF", "OpenPorchSF", "EnclosedPorch", "3SsnPorch", "ScreenPorch",
    "MiscVal", "YrSold", "HasPool"
)
