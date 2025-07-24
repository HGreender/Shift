import pytest
import requests
from unittest.mock import patch, MagicMock
from etl.extract import Extractor


@pytest.fixture
def extractor_instance():
    """Фикстура для создания экземпляра Extractor."""
    return Extractor(start_date="2023-01-01", end_date="2023-01-02")


def test_extractor_init(extractor_instance):
    """Тестирование инициализации Extractor."""
    assert extractor_instance.start_date == "2023-01-01"
    assert extractor_instance.end_date == "2023-01-02"
    assert extractor_instance.latitude == 55.0344
    assert extractor_instance.longitude == 82.9434


def test_extractor_start_date_setter_valid(extractor_instance):
    """Тестирование установки валидной начальной даты."""
    extractor_instance.start_date = "2024-01-01"
    assert extractor_instance.start_date == "2024-01-01"


def test_extractor_start_date_setter_invalid(extractor_instance):
    """Тестирование установки невалидной начальной даты."""
    with pytest.raises(ValueError):
        extractor_instance.start_date = "invalid-date"


def test_extractor_end_date_setter_valid(extractor_instance):
    """Тестирование установки валидной конечной даты."""
    extractor_instance.end_date = "2024-01-02"
    assert extractor_instance.end_date == "2024-01-02"


def test_extractor_end_date_setter_invalid(extractor_instance):
    """Тестирование установки невалидной конечной даты."""
    with pytest.raises(ValueError):
        extractor_instance.end_date = "invalid-date"


def test_extractor_latitude_setter_valid(extractor_instance):
    """Тестирование установки валидной широты."""
    extractor_instance.latitude = 45.0
    assert extractor_instance.latitude == 45.0


def test_extractor_latitude_setter_invalid(extractor_instance):
    """Тестирование установки невалидной широты."""
    with pytest.raises(ValueError, match='latitude must be from -90 to 90'):
        extractor_instance.latitude = 91.0
    with pytest.raises(ValueError, match='latitude must be from -90 to 90'):
        extractor_instance.latitude = -91.0


def test_extractor_longitude_setter_valid(extractor_instance):
    """Тестирование установки валидной долготы."""
    extractor_instance.longitude = 90.0
    assert extractor_instance.longitude == 90.0


def test_extractor_longitude_setter_invalid(extractor_instance):
    """Тестирование установки невалидной долготы."""
    with pytest.raises(ValueError, match='longitude must be from -180 to 180'):
        extractor_instance.longitude = 181.0
    with pytest.raises(ValueError, match='longitude must be from -180 to 180'):
        extractor_instance.longitude = -181.0


@patch('requests.get')
def test_run_api_extraction_success(mock_get, extractor_instance):
    """Тестирование успешного извлечения данных из API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"hourly": {}, "daily": {}}
    mock_get.return_value = mock_response

    result = extractor_instance.run_api_extraction()
    assert result == {"hourly": {}, "daily": {}}
    mock_get.assert_called_once()


@patch('requests.get')
def test_run_api_extraction_http_error(mock_get, extractor_instance):
    """Тестирование ошибки HTTP при извлечении из API."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        extractor_instance.run_api_extraction()


@patch('requests.get')
def test_run_api_extraction_json_decode_error(mock_get, extractor_instance):
    """Тестирование ошибки декодирования JSON при извлечении из API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Failed to decode")
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match='Failed to decode API response as JSON'):
        extractor_instance.run_api_extraction()


@patch('builtins.open', new_callable=MagicMock)
@patch('json.load', return_value={"hourly": {}, "daily": {}})
def test_run_json_extraction_success(mock_json_load, mock_open):
    """Тестирование успешного извлечения данных из JSON-файла."""
    result = Extractor.run_json_extraction("/app/dummy_path.json")
    assert result == {"hourly": {}, "daily": {}}
    mock_open.assert_called_once_with("/app/dummy_path.json", 'r', encoding='utf-8')
    mock_json_load.assert_called_once()


@patch('builtins.open', side_effect=FileNotFoundError)
def test_run_json_extraction_file_not_found(mock_open):
    """Тестирование ошибки 'файл не найден' при извлечении из JSON."""
    with pytest.raises(FileNotFoundError):
        Extractor.run_json_extraction("non_existent.json")


@patch('builtins.open', new_callable=MagicMock)
@patch('json.load', side_effect=ValueError) # Simulate JSONDecodeError
def test_run_json_extraction_json_decode_error(mock_json_load, mock_open):
    """Тестирование ошибки декодирования JSON при извлечении из JSON-файла."""
    with pytest.raises(ValueError):
        Extractor.run_json_extraction("malformed.json")
