import pytest
from etl.utils import validators


def test_validate_date_valid():
    assert validators.validate_date("2023-01-01") == "2023-01-01"

def test_validate_date_invalid_format():
    with pytest.raises(ValueError, match="Expected: YYYY-MM-DD"):
        validators.validate_date("01-01-2023")
    with pytest.raises(ValueError, match="Expected: YYYY-MM-DD"):
        validators.validate_date("2023/01/01")

def test_validate_date_invalid_date():
    with pytest.raises(ValueError, match="Expected: YYYY-MM-DD"):
        validators.validate_date("2023-02-30") # В феврале нет 30 дней
