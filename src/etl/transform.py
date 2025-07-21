import pandas as pd
from typing import Dict, Any
from .utils import converters

__all__ = [
    'Transformer'
]


def _hourly_date_transform(data: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(data['time'], unit='s', utc=True)
    df['date'] = df['time'].dt.date
    return df


def _daily_date_transform(data: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df['date'] = pd.to_datetime(data['time'], unit='s', utc=True).dt.date
    df['sunrise_iso'] = pd.to_datetime(data['sunrise'], unit='s', utc=True).dt.strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    df['sunset_iso'] = pd.to_datetime(data['sunset'], unit='s', utc=True).dt.strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    df['daylight_hours'] = data['daylight_duration'] / 3600
    return df


def _convert_units(data: pd.DataFrame):
    # TODO: Можно потом увеличить переиспользование
    df = data.copy()

    temp_cols = [
        'temperature_2m', 'dew_point_2m', 'apparent_temperature',
        'temperature_80m', 'temperature_120m', 'soil_temperature_0cm',
        'soil_temperature_6cm'
    ]
    for col in temp_cols:
        if col in df.columns:
            df[f'{col}_celsius'] = df[col].apply(converters.fahrenheit_to_celsius)
            df.drop(f'{col}', axis=1, inplace=True)

    wind_cols = ['wind_speed_10m', 'wind_speed_80m']
    for col in wind_cols:
        if col in df.columns:
            df[f'{col}_m_per_s'] = df[col].apply(converters.knots_to_m_per_s)
            df.drop(f'{col}', axis=1, inplace=True)

    precip_cols = ['evapotranspiration', 'rain', 'showers', 'snowfall']
    for col in precip_cols:
        if col in df.columns:
            df[f'{col}_mm'] = df[col].apply(converters.inches_to_mm)
            df.drop(f'{col}', axis=1, inplace=True)

    if 'visibility' in df.columns:
        df['visibility_m'] = df['visibility'].apply(converters.feet_to_meters)
        df.drop(f'{'visibility_m'}', axis=1, inplace=True)

    drop_cols = ['wind_direction_10m', 'wind_direction_80m', 'visibility', 'weather_code']
    for col in drop_cols:
        if col in df.columns:
            df.drop(f'{col}', axis=1, inplace=True)

    if 'relative_humidity_2m' in df.columns:
        df.rename(columns={'relative_humidity_2m': 'relative_humidity_2m_%'}, inplace=True)

    return df


class Transformer:
    def __init__(self, raw_data: Dict[str, Any]):
        if not isinstance(raw_data, dict) or 'hourly' not in raw_data or 'daily' not in raw_data:
            raise ValueError("Transformer ValueError")
        self.__data = raw_data

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value: Dict[str, Any]):
        # TODO: Перенести валидацию Transformer.data в validators.py
        if not isinstance(value, dict) or 'hourly' not in value or 'daily' not in value:
            raise ValueError("Transformer ValueError")
        self.__data = value

    def run(self):
        try:
            hourly_df = pd.DataFrame(self.__data['hourly'])
            daily_df = pd.DataFrame(self.__data['daily'])

            done_hourly_df = _hourly_date_transform(hourly_df)
            done_daily_df = _daily_date_transform(daily_df)

            merged_df = pd.merge(done_hourly_df, done_daily_df[['date', 'sunrise_iso', 'sunset_iso']], on='date')
            merged_df = _convert_units(merged_df)
            # merged_df.drop('date', axis=1, inplace=True)

            return merged_df
        except (KeyError, TypeError) as error:
            print(f"Transformer error: {error}")
            raise
        except Exception as error:
            print(f"Transformer unknown error: {error}")
            raise
