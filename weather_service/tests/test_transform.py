import pandas as pd
import pytest
from etl.transform import (Transformer,
                           _hourly_date_transform,
                           _daily_date_transform,
                           _convert_units,
                           _aggregate_data,
                           _structure_final_df)


@pytest.fixture
def sample_raw_data():
    """Фикстура для предоставления примера необработанных данных."""
    return {
        "hourly": {
            "time": [0, 3600, 7200, 86400, 90000, 93600],
            "temperature_2m": [50.0, 52.0, 55.0, 60.0, 61.0, 62.0],
            "relative_humidity_2m": [80, 78, 75, 70, 69, 68],
            "dew_point_2m": [45.0, 46.0, 48.0, 50.0, 51.0, 52.0],
            "apparent_temperature": [48.0, 50.0, 53.0, 58.0, 59.0, 60.0],
            "temperature_80m": [49.0, 51.0, 54.0, 59.0, 60.0, 61.0],
            "temperature_120m": [48.0, 50.0, 53.0, 58.0, 59.0, 60.0],
            "wind_speed_10m": [10.0, 12.0, 15.0, 8.0, 9.0, 10.0], # узлы
            "wind_speed_80m": [15.0, 18.0, 20.0, 12.0, 14.0, 15.0], # узлы
            "wind_direction_10m": [270, 280, 290, 180, 190, 200],
            "wind_direction_80m": [260, 270, 280, 170, 180, 190],
            "visibility": [10000, 9000, 8000, 12000, 11000, 10500], # футы
            "evapotranspiration": [0.1, 0.2, 0.1, 0.05, 0.08, 0.1], # дюймы
            "weather_code": [0, 0, 1, 0, 0, 1],
            "soil_temperature_0cm": [50.0, 51.0, 52.0, 55.0, 56.0, 57.0],
            "soil_temperature_6cm": [48.0, 49.0, 50.0, 53.0, 54.0, 55.0],
            "rain": [0.0, 0.0, 0.1, 0.0, 0.0, 0.0], # дюймы
            "showers": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], # дюймы
            "snowfall": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] # дюймы
        },
        "daily": {
            "time": [0, 86400],
            "sunrise": [0, 86400 + 7*3600], # Пример: 1 января 1970 00:00:00 UTC и 2 января 1970 07:00:00 UTC
            "sunset": [0 + 17*3600, 86400 + 17*3600], # Пример: 1 января 1970 17:00:00 UTC и 2 января 1970 17:00:00 UTC
            "daylight_duration": [10 * 3600, 10.5 * 3600]
        }
    }


@pytest.fixture
def transformer_instance(sample_raw_data):
    """Фикстура для создания экземпляра Transformer."""
    return Transformer(sample_raw_data)


def test_transformer_init_valid(sample_raw_data):
    """Тестирование валидной инициализации Transformer."""
    transformer = Transformer(sample_raw_data)
    assert transformer.data == sample_raw_data


def test_transformer_init_invalid_data():
    """Тестирование инициализации Transformer с невалидными данными."""
    with pytest.raises(ValueError, match="Dataframe initialization error in Transformer"):
        Transformer({"hourly": {}})
    with pytest.raises(ValueError, match="Dataframe initialization error in Transformer"):
        Transformer({"daily": {}})
    with pytest.raises(ValueError, match="Dataframe initialization error in Transformer"):
        Transformer(None)


def test_transformer_data_setter_valid(transformer_instance, sample_raw_data):
    """Тестирование установки валидных данных в Transformer."""
    new_data = {"hourly": {"time": [1]}, "daily": {"time": [1]}}
    transformer_instance.data = new_data
    assert transformer_instance.data == new_data


def test_transformer_data_setter_invalid(transformer_instance):
    """Тестирование установки невалидных данных в Transformer."""
    with pytest.raises(ValueError, match="Dataframe set error in Transformer"):
        transformer_instance.data = {"hourly": {}}
    with pytest.raises(ValueError, match="Dataframe set error in Transformer"):
        transformer_instance.data = {"daily": {}}
    with pytest.raises(ValueError, match="Dataframe set error in Transformer"):
        transformer_instance.data = None


def test_hourly_date_transform(sample_raw_data):
    """Тестирование преобразования данных по часам."""
    hourly_df = pd.DataFrame(sample_raw_data['hourly'])
    transformed_df = _hourly_date_transform(hourly_df)
    assert 'time' in transformed_df.columns
    assert 'date' in transformed_df.columns
    assert pd.api.types.is_datetime64_any_dtype(transformed_df['time'])
    assert transformed_df['date'].dtype == 'object' # dt.date возвращает тип object


def test_daily_date_transform(sample_raw_data):
    """Тестирование преобразования ежедневных данных."""
    daily_df = pd.DataFrame(sample_raw_data['daily'])
    transformed_df = _daily_date_transform(daily_df)
    assert 'date' in transformed_df.columns
    assert 'sunrise_iso' in transformed_df.columns
    assert 'sunset_iso' in transformed_df.columns
    assert 'daylight_hours' in transformed_df.columns
    assert transformed_df['date'].dtype == 'object'
    assert transformed_df['daylight_hours'].iloc[0] == 10.0 # 10 * 3600 / 3600


def test_convert_units(sample_raw_data):
    """Тестирование преобразования единиц измерения."""
    df = pd.DataFrame(sample_raw_data['hourly'])
    converted_df = _convert_units(df)

    assert 'temperature_2m_celsius' in converted_df.columns
    assert 'wind_speed_10m_m_per_s' in converted_df.columns
    assert 'rain_mm' in converted_df.columns
    assert 'visibility_m' in converted_df.columns

    # Проверка, что исходные столбцы удалены
    assert 'temperature_2m' not in converted_df.columns
    assert 'wind_speed_10m' not in converted_df.columns
    assert 'rain' not in converted_df.columns
    assert 'visibility' not in converted_df.columns
    assert 'wind_direction_10m' not in converted_df.columns

    # Точечная проверка преобразования
    assert converted_df['temperature_2m_celsius'].iloc[0] == pytest.approx((50.0 - 32) * 5 / 9)
    assert converted_df['wind_speed_10m_m_per_s'].iloc[0] == pytest.approx(10.0 * 0.514444)
    assert converted_df['rain_mm'].iloc[2] == pytest.approx(0.1 * 25.4)
    assert converted_df['visibility_m'].iloc[0] == pytest.approx(10000 * 0.3048)


def test_aggregate_data():
    """Тестирование агрегации данных."""
    data = {
        'date': ['2023-01-01', '2023-01-01', '2023-01-02'],
        'temperature_2m_celsius': [10.0, 20.0, 5.0],
        'relative_humidity_2m': [50, 60, 70],
        'dew_point_2m_celsius': [5.0, 10.0, 2.0],
        'apparent_temperature_celsius': [8.0, 18.0, 3.0],
        'temperature_80m_celsius': [9.0, 19.0, 4.0],
        'temperature_120m_celsius': [8.5, 18.5, 3.5],
        'wind_speed_10m_m_per_s': [2.0, 4.0, 1.0],
        'wind_speed_80m_m_per_s': [3.0, 5.0, 2.0],
        'visibility_m': [1000.0, 2000.0, 500.0],
        'rain_mm': [1.0, 2.0, 0.5],
        'showers_mm': [0.5, 0.5, 0.1],
        'snowfall_mm': [0.0, 0.0, 0.0]
    }
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date']).dt.date
    grouped_df = df.groupby('date')
    agg_df = _aggregate_data(grouped_df, suffix='_test')

    assert 'avg_temperature_2m_test' in agg_df.columns
    assert agg_df.loc[pd.to_datetime('2023-01-01').date()]['avg_temperature_2m_test'] == pytest.approx(15.0)
    assert agg_df.loc[pd.to_datetime('2023-01-02').date()]['avg_temperature_2m_test'] == pytest.approx(5.0)
    assert agg_df.loc[pd.to_datetime('2023-01-01').date()]['total_rain_test'] == pytest.approx(3.0)


def test_structure_final_df(sample_raw_data):
    """Тестирование структурирования итогового DataFrame."""
    # Создаем фиктивный DataFrame, который содержит некоторые целевые столбцы
    data = {
        'time': pd.to_datetime(['1970-01-01T00:00:00Z', '1970-01-02T00:00:00Z']),
        'avg_temperature_2m_24h': [10.0, 12.0],
        'wind_speed_10m_m_per_s': [2.0, 3.0],
        'daylight_hours': [10.0, 11.0],
        'sunset_iso': ['1970-01-01T17:00:00Z', '1970-01-02T17:00:00Z'],
        'sunrise_iso': ['1970-01-01T00:00:00Z', '1970-01-02T07:00:00Z'],
        'extra_col': [1, 2] # Этот столбец должен быть удален
    }
    df = pd.DataFrame(data)
    df['date'] = df['time'].dt.date # Добавляем столбец даты для потенциальных проблем с объединением в полном запуске

    structured_df = _structure_final_df(df)

    expected_cols_subset = [
        'time',
        'avg_temperature_2m_24h',
        'wind_speed_10m_m_per_s',
        'daylight_hours',
        'sunset_iso',
        'sunrise_iso'
    ]
    assert list(structured_df.columns) == expected_cols_subset
    assert 'extra_col' not in structured_df.columns


def test_transformer_run_success(transformer_instance):
    """Тестирование успешного выполнения Transformer."""
    transformed_df = transformer_instance.run()
    assert isinstance(transformed_df, pd.DataFrame)
    assert not transformed_df.empty

    # Проверка ожидаемых столбцов после полной трансформации
    expected_final_columns = [
        'time',

        'avg_temperature_2m_24h', 'avg_relative_humidity_2m_24h', 'avg_dew_point_2m_24h',
        'avg_apparent_temperature_24h', 'avg_temperature_80m_24h', 'avg_temperature_120m_24h',
        'avg_wind_speed_10m_24h', 'avg_wind_speed_80m_24h', 'avg_visibility_24h',
        'total_rain_24h', 'total_showers_24h', 'total_snowfall_24h',

        'avg_temperature_2m_daylight', 'avg_relative_humidity_2m_daylight', 'avg_dew_point_2m_daylight',
        'avg_apparent_temperature_daylight', 'avg_temperature_80m_daylight', 'avg_temperature_120m_daylight',
        'avg_wind_speed_10m_daylight', 'avg_wind_speed_80m_daylight', 'avg_visibility_daylight',
        'total_rain_daylight', 'total_showers_daylight', 'total_snowfall_daylight',

        'wind_speed_10m_m_per_s', 'wind_speed_80m_m_per_s', 'temperature_2m_celsius',
        'apparent_temperature_celsius', 'temperature_80m_celsius', 'temperature_120m_celsius',
        'soil_temperature_0cm_celsius', 'soil_temperature_6cm_celsius', 'rain_mm', 'showers_mm', 'snowfall_mm',

        'daylight_hours', 'sunset_iso', 'sunrise_iso'
    ]
    for col in expected_final_columns:
        assert col in transformed_df.columns, f"Столбец {col} отсутствует в преобразованном DataFrame"

    # Проверка, что столбец 'date' удален (он должен использоваться для объединения, а затем удаляться из основного df)
    # Столбец 'date' используется как индекс, а затем сбрасывается или удаляется, в зависимости от окончательного объединения
    # Проверим, что индекс 'date' отсутствует в столбцах итогового DataFrame
    assert 'date' not in transformed_df.columns

    # Проверка нескольких точек данных или типов
    assert pd.api.types.is_datetime64_any_dtype(transformed_df['time'])
    assert transformed_df['avg_temperature_2m_24h'].dtype == 'float64'
    assert transformed_df['daylight_hours'].dtype == 'float64'
