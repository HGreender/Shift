import os
import pytest
import pandas as pd
import sqlite3
from etl.load import Loader


@pytest.fixture
def sample_dataframe():
    """Фикстура для предоставления примера DataFrame."""
    data = {
        'time': pd.to_datetime(['2023-01-01 00:00:00', '2023-01-01 01:00:00']),
        'temperature_2m_celsius': [0.0, 1.0],
        'rain_mm': [0.0, 2.5]
    }
    return pd.DataFrame(data)


@pytest.fixture
def loader_instance(sample_dataframe):
    """Фикстура для создания экземпляра Loader."""
    return Loader(sample_dataframe)


def test_loader_init_valid(sample_dataframe):
    """Тестирование валидной инициализации Loader."""
    loader = Loader(sample_dataframe)
    pd.testing.assert_frame_equal(loader.df, sample_dataframe)


def test_loader_init_empty_df():
    """Тестирование инициализации Loader с пустым DataFrame."""
    with pytest.raises(ValueError, match="Empty DataFrame"):
        Loader(pd.DataFrame())


def test_loader_df_setter_valid(loader_instance):
    """Тестирование установки валидного DataFrame в Loader."""
    new_df = pd.DataFrame({'col1': [1, 2]})
    loader_instance.df = new_df
    pd.testing.assert_frame_equal(loader_instance.df, new_df)


def test_loader_df_setter_empty_df(loader_instance):
    """Тестирование установки пустого DataFrame в Loader."""
    with pytest.raises(ValueError, match="Empty DataFrame"):
        loader_instance.df = pd.DataFrame()


@pytest.fixture(scope="module")
def csv_test_path():
    """Фикстура для пути к тестовому CSV-файлу."""
    # Изменяем, чтобы передавать путь, который ожидается main.py
    # load.py добавит 'data/' к этому пути
    path_relative_to_data_dir = "output/test_output.csv"
    full_path_in_container = os.path.join('data', path_relative_to_data_dir)
    yield path_relative_to_data_dir # Yield the path as main.py would pass it
    if os.path.exists(full_path_in_container): # Check the full path
        os.remove(full_path_in_container)
    # Добавляем дополнительную проверку для удаления каталога 'output'
    output_dir = os.path.dirname(full_path_in_container)
    if os.path.exists(output_dir) and not os.listdir(output_dir):
        os.rmdir(output_dir)
    # Также проверяем и удаляем, если data/ стало пустым
    data_dir = os.path.join('data')
    if os.path.exists(data_dir) and not os.listdir(data_dir):
        os.rmdir(data_dir)


def test_load_to_csv_success(loader_instance, csv_test_path):
    """Тестирование успешной загрузки в CSV-файл."""
    loader_instance.load_to_csv(csv_test_path)
    # Теперь проверяем полный путь, который load.py фактически использовал
    expected_full_path = os.path.join('data', csv_test_path)
    assert os.path.exists(expected_full_path)
    loaded_df = pd.read_csv(expected_full_path, parse_dates=['time'])
    pd.testing.assert_frame_equal(loaded_df, loader_instance.df)


@pytest.fixture(scope="module")
def db_test_path():
    """Фикстура для пути к тестовой базе данных SQLite."""
    path = "data/test_weather.db"
    yield path
    if os.path.exists(path):
        os.remove(path)
    if os.path.exists(os.path.dirname(path)):
        # Проверяем, что каталог пуст, прежде чем удалять его
        if not os.listdir(os.path.dirname(path)):
            os.rmdir(os.path.dirname(path))


def test_load_to_db_success_new_table(loader_instance, db_test_path):
    """Тестирование успешной загрузки в новую таблицу базы данных."""
    table_name = "weather_forecasts_test_new"
    loader_instance.load_to_db(db_test_path, table_name)

    with sqlite3.connect(db_test_path) as conn:
        loaded_df = pd.read_sql(f"SELECT * FROM {table_name}", conn, parse_dates=['time'])

    # DB может немного изменить типы данных, поэтому check_dtype=False
    pd.testing.assert_frame_equal(loaded_df, loader_instance.df, check_dtype=False)


def test_load_to_db_append_existing_data(loader_instance, db_test_path):
    """Тестирование добавления существующих данных в базу данных."""
    table_name = "weather_forecasts_test_append"

    # Первая загрузка
    loader_instance.load_to_db(db_test_path, table_name)

    # Подготовка новых данных с одной совпадающей строкой и одной новой строкой
    new_data = {
        'time': pd.to_datetime(['2023-01-01 01:00:00', '2023-01-01 02:00:00']),
        'temperature_2m_celsius': [1.0, 5.0],
        'rain_mm': [2.5, 3.0]
    }
    new_df = pd.DataFrame(new_data)
    new_loader = Loader(new_df)

    new_loader.load_to_db(db_test_path, table_name)

    with sqlite3.connect(db_test_path) as conn:
        loaded_df = pd.read_sql(f"SELECT * FROM {table_name}", conn, parse_dates=['time'])

    expected_df = pd.DataFrame({
        'time': pd.to_datetime(['2023-01-01 00:00:00', '2023-01-01 01:00:00', '2023-01-01 02:00:00']),
        'temperature_2m_celsius': [0.0, 1.0, 5.0],
        'rain_mm': [0.0, 2.5, 3.0]
    })
    # Сортируем DataFrame перед сравнением, так как порядок может измениться
    pd.testing.assert_frame_equal(loaded_df.sort_values(by='time').reset_index(drop=True),
                                  expected_df.sort_values(by='time').reset_index(drop=True),
                                  check_dtype=False)


def test_load_to_db_operational_error(loader_instance, mocker):
    """Тестирование операционной ошибки SQLite при загрузке в БД."""
    mocker.patch('sqlite3.connect', side_effect=sqlite3.OperationalError("Disk full"))
    with pytest.raises(sqlite3.OperationalError, match="Disk full"):
        loader_instance.load_to_db("data/error.db")


def test_load_to_db_unknown_error(loader_instance, mocker):
    """Тестирование неизвестной ошибки при загрузке в БД."""
    mocker.patch('sqlite3.connect', side_effect=Exception("Something bad happened"))
    with pytest.raises(Exception, match="Something bad happened"):
        loader_instance.load_to_db("data/error.db")
