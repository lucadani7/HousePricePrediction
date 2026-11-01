from pathlib import Path
import pytest
from housepriceprediction.config import TXT_FILE
from housepriceprediction.data_description import DataDescription


@pytest.fixture
def mock_data_description_file(tmp_path: Path) -> Path:
    """Creates a temporary data description file mimicking the real file format
    (using tabs, spacing, and blank lines).
    """
    content = """
MSSubClass: 20, 30, 40, 50

LotFrontage: 

PoolQC:
\tEx\tExcellent
\tGd\tGood
\tNA\tNo Pool

Fence:
\tGdPrv\tGood Privacy
\tMnPrv\tMinimum Privacy
\tNA\tNo Fence
"""
    file_path = tmp_path / "data_description_test.txt"
    file_path.write_text(content.strip(), encoding="utf-8")
    return file_path


@pytest.mark.skipif(not TXT_FILE.exists(), reason="data_description.txt not downloaded")
def test_real_data_description_file() -> None:
    """Verifies parsing against the real data_description.txt file.
    Ensures that the exact expected 14 columns are identified where NA means absence.
    """
    desc = DataDescription(TXT_FILE)
    expected_columns = (
        "Alley",
        "BsmtCond",
        "BsmtExposure",
        "BsmtFinType1",
        "BsmtFinType2",
        "BsmtQual",
        "Fence",
        "FireplaceQu",
        "GarageCond",
        "GarageFinish",
        "GarageQual",
        "GarageType",
        "MiscFeature",
        "PoolQC",
    )
    assert desc.columns_where_na_means_absent == expected_columns


@pytest.mark.skipif(not TXT_FILE.exists(), reason="data_description.txt not downloaded")
def test_name_mismatch_trap() -> None:
    """Documents the name mismatch trap between CSV columns and description file headers.
    - 'Bedroom' exists in the description text but has no codes -> raises ValueError.
    - 'BedroomAbvGr' is the actual CSV column name and is absent from the text -> raises KeyError.
    """
    desc = DataDescription(TXT_FILE)

    with pytest.raises(ValueError):
        desc.codes("Bedroom")

    with pytest.raises(KeyError):
        desc.codes("BedroomAbvGr")


def test_columns_where_na_means_absent(mock_data_description_file: Path) -> None:
    """Verifies that columns where NA means absence are correctly identified
    and that the result is a sorted tuple.
    """
    desc = DataDescription(mock_data_description_file)
    result = desc.columns_where_na_means_absent

    assert isinstance(result, tuple)
    assert result == ("Fence", "PoolQC")


def test_has_codes(mock_data_description_file: Path) -> None:
    """Verifies the functionality of the has_codes method across various scenarios."""
    desc = DataDescription(mock_data_description_file)

    assert desc.has_codes("PoolQC") is True
    assert desc.has_codes("LotFrontage") is False
    assert desc.has_codes("NonExistentColumn") is False


def test_codes_success(mock_data_description_file: Path) -> None:
    """Verifies successful extraction of codes as a dictionary for a valid column."""
    desc = DataDescription(mock_data_description_file)
    codes = desc.codes("PoolQC")

    assert isinstance(codes, dict)
    assert "NA" in codes
    assert codes["NA"] == "No Pool"
    assert codes["Ex"] == "Excellent"


def test_codes_raises_key_error(mock_data_description_file: Path) -> None:
    """Verifies that a KeyError is raised for a non-existent column."""
    desc = DataDescription(mock_data_description_file)

    with pytest.raises(KeyError) as exc_info:
        desc.codes("FakeColumn")

    assert "FakeColumn" in str(exc_info.value)


def test_codes_raises_value_error(mock_data_description_file: Path) -> None:
    """Verifies that a ValueError is raised for a column without defined codes."""
    desc = DataDescription(mock_data_description_file)

    with pytest.raises(ValueError) as exc_info:
        desc.codes("LotFrontage")

    assert "LotFrontage" in str(exc_info.value)


# ==========================================
# EDGE CASES
# ==========================================

def test_empty_description_file(tmp_path: Path) -> None:
    """Verifies the class behavior when the description text file is completely empty."""
    file_path = tmp_path / "empty.txt"
    file_path.write_text("", encoding="utf-8")

    desc = DataDescription(file_path)

    assert desc.columns_where_na_means_absent == ()
    assert desc.has_codes("AnyColumn") is False
    with pytest.raises(KeyError):
        desc.codes("AnyColumn")


def test_malformed_blocks(tmp_path: Path) -> None:
    """Verifies how the parser handles lines or headers that do not follow the standard format."""
    content = """
ThisIsHeaderWithoutColon
\tSome subline without context

ValidFeature: 
\tSomeCode

AnotherFeature : 
\tNA\tsomething
"""
    file_path = tmp_path / "malformed.txt"
    file_path.write_text(content.strip(), encoding="utf-8")

    desc = DataDescription(file_path)

    assert desc.has_codes("ThisIsHeaderWithoutColon") is False
    assert desc.has_codes("ValidFeature") is True
    assert "AnotherFeature" in desc.columns_where_na_means_absent


def test_strict_na_starting_check(tmp_path: Path) -> None:
    """Verifies that structural NA detection is strict (looks for exact 'NA' as a code key)."""
    content = """
BadNaFeature:
\tN/A\tNot applicable
\tna\tlowercase na

GoodNaFeature:
\tNA\tStrict match
"""
    file_path = tmp_path / "strict_na.txt"
    file_path.write_text(content.strip(), encoding="utf-8")

    desc = DataDescription(file_path)

    assert desc.columns_where_na_means_absent == ("GoodNaFeature",)
