from pathlib import Path
from typing import Final

PROJECT_ROOT: Final = Path(__file__).resolve().parents[2]
DATA_RAW: Final = PROJECT_ROOT / "data" / "raw"
TXT_FILE: Final = PROJECT_ROOT / "data" / "raw" / "data_description.txt"

TARGET: Final = "SalePrice"
RANDOM_STATE: Final = 42