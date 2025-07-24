import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
import os
import sys
import argparse

# Импортируем run_pipeline напрямую, так как мы будем имитировать аргументы
from main import run_pipeline, main # Импортируем main для тестирования парсера аргументов


# Фикстура для имитации sys.exit, чтобы тесты не завершались
@pytest.fixture(autouse=True)
def mock_sys_exit(mocker):
    """
    Имитирует sys.exit(), чтобы предотвратить завершение программы во время тестов,
    которые вызывают sys.exit(1) при ошибке.
    """
    mocker.patch('sys.exit')


# Фикстура для имитации os.getenv("DATABASE_FILE")
@pytest.fixture
def mock_db_path(mocker):
    """Имитирует переменную окружения DATABASE_FILE."""
    mocker.patch.dict(os.environ, {"DATABASE_FILE": "/app/data/test_weather.db"})


# Фикстура для создания фиктивных данных, которые будут возвращаться экстрактором
@pytest.fixture
def mock_raw_data():
    """Возвращает фиктивные необработанные данные для экстрактора."""
    return {
        "hourly": {
            "time": [0, 3600],
            "temperature_2m": [50.0, 52.0],
            "relative_humidity_2m": [80, 78],
            "dew_point_2m": [45.0, 46.0],
            "apparent_temperature": [48.0, 50.0],
            "temperature_80m": [49.0, 51.0],
            "temperature_120m": [48.0, 50.0],
            "wind_speed_10m": [10.0, 12.0],
            "wind_speed_80m": [15.0, 18.0],
            "wind_direction_10m": [270, 280],
            "wind_direction_80m": [260, 270],
            "visibility": [10000, 9000],
            "evapotranspiration": [0.1, 0.2],
            "weather_code": [0, 0],
            "soil_temperature_0cm": [50.0, 51.0],
            "soil_temperature_6cm": [48.0, 49.0],
            "rain": [0.0, 0.0],
            "showers": [0.0, 0.0],
            "snowfall": [0.0, 0.0]
        },
        "daily": {
            "time": [0],
            "sunrise": [0],
            "sunset": [0 + 17*3600],
            "daylight_duration": [10 * 3600]
        }
    }


# Фикстура для создания фиктивного преобразованного DataFrame
@pytest.fixture
def mock_transformed_df():
    """Возвращает фиктивный преобразованный DataFrame."""
    return pd.DataFrame({
        'time': pd.to_datetime(['1970-01-01 00:00:00+00:00', '1970-01-01 01:00:00+00:00']),
        'avg_temperature_2m_24h': [10.0, 12.0],
        'daylight_hours': [10.0, 10.0],
        'sunset_iso': ['1970-01-01T17:00:00Z', '1970-01-01T17:00:00Z'],
        'sunrise_iso': ['1970-01-01T00:00:00Z', '1970-01-01T00:00:00Z']
    })


# --- Тесты полного конвейера ---

@patch('etl.extract.Extractor.run_api_extraction')
@patch('etl.transform.Transformer.run')
@patch('etl.load.Loader.load_to_csv')
@patch('etl.load.Loader.__init__', return_value=None) # Имитируем __init__ Loader
@patch('etl.transform.Transformer.__init__', return_value=None) # Имитируем __init__ Transformer
@patch('etl.extract.Extractor.__init__', return_value=None) # Имитируем __init__ Extractor
def test_pipeline_api_to_csv_success(
    mock_extractor_init, mock_transformer_init, mock_loader_init,
    mock_load_to_csv, mock_transform_run, mock_extract_api_run,
    mock_raw_data, mock_transformed_df
):
    """
    Тестирует успешный сквозной конвейер: API -> CSV.
    """
    # Настраиваем возвращаемые значения моков
    mock_extract_api_run.return_value = mock_raw_data
    mock_transform_run.return_value = mock_transformed_df

    # Имитируем аргументы командной строки
    args = MagicMock(
        source='api',
        target='csv',
        start_date='2023-01-01',
        end_date='2023-01-02',
        file_path=None,
        output_file='test_output.csv'
    )

    run_pipeline(args)

    # Проверяем, что методы были вызваны в правильном порядке и с правильными аргументами
    mock_extractor_init.assert_called_once_with(start_date='2023-01-01', end_date='2023-01-02')
    mock_extract_api_run.assert_called_once()
    mock_transformer_init.assert_called_once_with(mock_raw_data)
    mock_transform_run.assert_called_once()
    mock_loader_init.assert_called_once_with(mock_transformed_df)
    mock_load_to_csv.assert_called_once_with('test_output.csv')
    sys.exit.assert_not_called() # Убеждаемся, что sys.exit не был вызван


@patch('etl.extract.Extractor.run_api_extraction')
@patch('etl.transform.Transformer.run')
@patch('etl.load.Loader.load_to_db')
@patch('etl.load.Loader.__init__', return_value=None)
@patch('etl.transform.Transformer.__init__', return_value=None)
@patch('etl.extract.Extractor.__init__', return_value=None)
def test_pipeline_api_to_db_success(
    mock_extractor_init, mock_transformer_init, mock_loader_init,
    mock_load_to_db, mock_transform_run, mock_extract_api_run,
    mock_raw_data, mock_transformed_df, mock_db_path # Используем фикстуру mock_db_path
):
    """
    Тестирует успешный сквозной конвейер: API -> DB.
    """
    mock_extract_api_run.return_value = mock_raw_data
    mock_transform_run.return_value = mock_transformed_df

    args = MagicMock(
        source='api',
        target='db',
        start_date='2023-01-01',
        end_date='2023-01-02',
        file_path=None,
        output_file=None
    )

    run_pipeline(args)

    mock_extractor_init.assert_called_once_with(start_date='2023-01-01', end_date='2023-01-02')
    mock_extract_api_run.assert_called_once()
    mock_transformer_init.assert_called_once_with(mock_raw_data)
    mock_transform_run.assert_called_once()
    mock_loader_init.assert_called_once_with(mock_transformed_df)
    # Проверяем, что load_to_db вызван с путем из переменной окружения
    mock_load_to_db.assert_called_once_with(os.getenv("DATABASE_FILE"))
    sys.exit.assert_not_called()


@patch('etl.extract.Extractor.run_json_extraction')
@patch('etl.transform.Transformer.run')
@patch('etl.load.Loader.load_to_csv')
@patch('etl.load.Loader.__init__', return_value=None)
@patch('etl.transform.Transformer.__init__', return_value=None)
@patch('etl.extract.Extractor.__init__', return_value=None)
def test_pipeline_json_to_csv_success(
    mock_extractor_init, mock_transformer_init, mock_loader_init,
    mock_load_to_csv, mock_transform_run, mock_extract_json_run,
    mock_raw_data, mock_transformed_df
):
    """
    Тестирует успешный сквозной конвейер: JSON -> CSV.
    """
    mock_extract_json_run.return_value = mock_raw_data
    mock_transform_run.return_value = mock_transformed_df

    args = MagicMock(
        source='json',
        target='csv',
        start_date=None,
        end_date=None,
        file_path='data/input.json',
        output_file='test_output.csv'
    )

    run_pipeline(args)

    # Для JSON-экстрактора Extractor.__init__ не вызывается, так как run_json_extraction статический метод
    mock_extractor_init.assert_not_called()
    mock_extract_json_run.assert_called_once_with('data/input.json')
    mock_transformer_init.assert_called_once_with(mock_raw_data)
    mock_transform_run.assert_called_once()
    mock_loader_init.assert_called_once_with(mock_transformed_df)
    mock_load_to_csv.assert_called_once_with('test_output.csv')
    sys.exit.assert_not_called()


@patch('etl.extract.Extractor.run_json_extraction')
@patch('etl.transform.Transformer.run')
@patch('etl.load.Loader.load_to_db')
@patch('etl.load.Loader.__init__', return_value=None)
@patch('etl.transform.Transformer.__init__', return_value=None)
@patch('etl.extract.Extractor.__init__', return_value=None)
def test_pipeline_json_to_db_success(
    mock_extractor_init, mock_transformer_init, mock_loader_init,
    mock_load_to_db, mock_transform_run, mock_extract_json_run,
    mock_raw_data, mock_transformed_df, mock_db_path
):
    """
    Тестирует успешный сквозной конвейер: JSON -> DB.
    """
    mock_extract_json_run.return_value = mock_raw_data
    mock_transform_run.return_value = mock_transformed_df

    args = MagicMock(
        source='json',
        target='db',
        start_date=None,
        end_date=None,
        file_path='data/input.json',
        output_file=None
    )

    run_pipeline(args)

    mock_extractor_init.assert_not_called()
    mock_extract_json_run.assert_called_once_with('data/input.json')
    mock_transformer_init.assert_called_once_with(mock_raw_data)
    mock_transform_run.assert_called_once()
    mock_loader_init.assert_called_once_with(mock_transformed_df)
    mock_load_to_db.assert_called_once_with(os.getenv("DATABASE_FILE"))
    sys.exit.assert_not_called()


# --- Тесты обработки ошибок ---

@patch('etl.extract.Extractor.run_api_extraction', side_effect=Exception("Extraction error"))
@patch('etl.transform.Transformer.run')
@patch('etl.load.Loader.load_to_csv')
@patch('etl.load.Loader.__init__', return_value=None)
@patch('etl.transform.Transformer.__init__', return_value=None)
@patch('etl.extract.Extractor.__init__', return_value=None)
def test_pipeline_extraction_failure(
    mock_extractor_init, mock_transformer_init, mock_loader_init,
    mock_load_to_csv, mock_transform_run, mock_extract_api_run
):
    """
    Тестирует обработку ошибок при извлечении данных.
    """
    args = MagicMock(
        source='api',
        target='csv',
        start_date='2023-01-01',
        end_date='2023-01-02',
        file_path=None,
        output_file='test_output.csv'
    )

    run_pipeline(args)

    mock_extract_api_run.assert_called_once()
    mock_transform_run.assert_not_called() # Трансформация не должна вызываться
    mock_load_to_csv.assert_not_called() # Загрузка не должна вызываться
    sys.exit.assert_called_once_with(1) # Убеждаемся, что sys.exit(1) был вызван


@patch('etl.extract.Extractor.run_api_extraction')
@patch('etl.transform.Transformer.run', side_effect=Exception("Transformation error"))
@patch('etl.load.Loader.load_to_csv')
@patch('etl.load.Loader.__init__', return_value=None)
@patch('etl.transform.Transformer.__init__', return_value=None)
@patch('etl.extract.Extractor.__init__', return_value=None)
def test_pipeline_transformation_failure(
    mock_extractor_init, mock_transformer_init, mock_loader_init,
    mock_load_to_csv, mock_transform_run, mock_extract_api_run,
    mock_raw_data
):
    """
    Тестирует обработку ошибок при преобразовании данных.
    """
    mock_extract_api_run.return_value = mock_raw_data

    args = MagicMock(
        source='api',
        target='csv',
        start_date='2023-01-01',
        end_date='2023-01-02',
        file_path=None,
        output_file='test_output.csv'
    )

    run_pipeline(args)

    mock_extract_api_run.assert_called_once()
    mock_transform_run.assert_called_once()
    mock_load_to_csv.assert_not_called() # Загрузка не должна вызываться
    sys.exit.assert_called_once_with(1)


@patch('etl.extract.Extractor.run_api_extraction')
@patch('etl.transform.Transformer.run')
@patch('etl.load.Loader.load_to_csv', side_effect=Exception("Loading error"))
@patch('etl.load.Loader.__init__', return_value=None)
@patch('etl.transform.Transformer.__init__', return_value=None)
@patch('etl.extract.Extractor.__init__', return_value=None)
def test_pipeline_loading_failure(
    mock_extractor_init, mock_transformer_init, mock_loader_init,
    mock_load_to_csv, mock_transform_run, mock_extract_api_run,
    mock_raw_data, mock_transformed_df
):
    """
    Тестирует обработку ошибок при загрузке данных.
    """
    mock_extract_api_run.return_value = mock_raw_data
    mock_transform_run.return_value = mock_transformed_df

    args = MagicMock(
        source='api',
        target='csv',
        start_date='2023-01-01',
        end_date='2023-01-02',
        file_path=None,
        output_file='test_output.csv'
    )

    run_pipeline(args)

    mock_extract_api_run.assert_called_once()
    mock_transform_run.assert_called_once()
    mock_load_to_csv.assert_called_once()
    sys.exit.assert_called_once_with(1)


# --- Тесты парсера аргументов main() ---

@patch('argparse.ArgumentParser.error', side_effect=SystemExit) # Изменено: теперь вызывает SystemExit
@patch('main.run_pipeline')
def test_main_api_missing_dates(mock_run_pipeline, mock_parser_error):
    """
    Тестирует, что main() вызывает ошибку для API без дат.
    """
    with patch.object(sys, 'argv', ['main.py', '-s', 'api', '--target', 'csv', '-o', 'output.csv']):
        with pytest.raises(SystemExit): # Ожидаем SystemExit
            main()
        mock_parser_error.assert_called_once_with("--start-date and --end-date are required for the --source api")
        mock_run_pipeline.assert_not_called() # run_pipeline не должен вызываться


@patch('argparse.ArgumentParser.error', side_effect=SystemExit) # Изменено: теперь вызывает SystemExit
@patch('main.run_pipeline')
def test_main_json_missing_file_path(mock_run_pipeline, mock_parser_error):
    """
    Тестирует, что main() вызывает ошибку для JSON без пути к файлу.
    """
    with patch.object(sys, 'argv', ['main.py', '-s', 'json', '--target', 'db']):
        with pytest.raises(SystemExit): # Ожидаем SystemExit
            main()
        mock_parser_error.assert_called_once_with("--file-path is required for --source json")
        mock_run_pipeline.assert_not_called() # run_pipeline не должен вызываться


@patch('argparse.ArgumentParser.error', side_effect=SystemExit) # Изменено: теперь вызывает SystemExit
@patch('main.run_pipeline')
def test_main_csv_missing_output_file(mock_run_pipeline, mock_parser_error):
    """
    Тестирует, что main() вызывает ошибку для CSV без выходного файла.
    """
    with patch.object(sys, 'argv', ['main.py', '-s', 'api', '-start', '2023-01-01', '-end', '2023-01-02', '--target', 'csv']):
        with pytest.raises(SystemExit): # Ожидаем SystemExit
            main()
        mock_parser_error.assert_called_once_with("--output-file is required for --target csv")
        mock_run_pipeline.assert_not_called() # run_pipeline не должен вызываться


@patch('main.run_pipeline')
def test_main_valid_args_api_csv(mock_run_pipeline):
    """
    Тестирует успешный вызов run_pipeline с валидными аргументами API -> CSV.
    """
    with patch.object(sys, 'argv', ['main.py', '-s', 'api', '-start', '2023-01-01', '-end', '2023-01-02', '--target', 'csv', '-o', 'output.csv']):
        main()
        mock_run_pipeline.assert_called_once()
        # Проверяем, что run_pipeline был вызван с правильными аргументами
        call_args = mock_run_pipeline.call_args[0][0]
        assert call_args.source == 'api'
        assert call_args.start_date == '2023-01-01'
        assert call_args.end_date == '2023-01-02'
        assert call_args.target == 'csv'
        assert call_args.output_file == 'output.csv'


@patch('main.run_pipeline')
def test_main_valid_args_json_db(mock_run_pipeline):
    """
    Тестирует успешный вызов run_pipeline с валидными аргументами JSON -> DB.
    """
    with patch.object(sys, 'argv', ['main.py', '-s', 'json', '--file-path', 'input.json', '--target', 'db']):
        main()
        mock_run_pipeline.assert_called_once()
        call_args = mock_run_pipeline.call_args[0][0]
        assert call_args.source == 'json'
        assert call_args.file_path == 'input.json'
        assert call_args.target == 'db'
