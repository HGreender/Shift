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
    df['sunrise_iso'] = pd.to_datetime(data['sunrise'], unit='s').dt.strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    df['sunset_iso'] = pd.to_datetime(data['sunset'], unit='s').dt.strftime(
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
        df.drop(f'{'visibility'}', axis=1, inplace=True)

    drop_cols = ['wind_direction_10m', 'wind_direction_80m', 'visibility', 'weather_code']
    for col in drop_cols:
        if col in df.columns:
            df.drop(f'{col}', axis=1, inplace=True)

    if 'relative_humidity_2m' in df.columns:
        df.rename(columns={'relative_humidity_2m': 'relative_humidity_2m_%'}, inplace=True)
    return df


def _aggregate_data(grouped_df, suffix: str) -> pd.DataFrame:
    agg_dict = {
        f'avg_temperature_2m{suffix}': ('temperature_2m_celsius', 'mean'),
        f'avg_relative_humidity_2m_%{suffix}': ('relative_humidity_2m_%', 'mean'),
        f'avg_dew_point_2m{suffix}': ('dew_point_2m_celsius', 'mean'),
        f'avg_apparent_temperature{suffix}': ('apparent_temperature_celsius', 'mean'),
        f'avg_temperature_80m{suffix}': ('temperature_80m_celsius', 'mean'),
        f'avg_temperature_120m{suffix}': ('temperature_120m_celsius', 'mean'),
        f'avg_wind_speed_10m{suffix}': ('wind_speed_10m_m_per_s', 'mean'),
        f'avg_wind_speed_80m{suffix}': ('wind_speed_80m_m_per_s', 'mean'),
        f'avg_visibility{suffix}': ('visibility_m', 'mean'),
        f'total_rain{suffix}': ('rain_mm', 'sum'),
        f'total_showers{suffix}': ('showers_mm', 'sum'),
        f'total_snowfall{suffix}': ('snowfall_mm', 'sum')
    }
    return grouped_df.agg(**agg_dict).round(2)


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
            # print(merged_df.info())
            merged_df = _convert_units(merged_df)

            agg_24h = _aggregate_data(merged_df.groupby('date'), suffix='_24h')

            daylight_df = merged_df[
                (merged_df['time'] >= merged_df['sunrise_iso']) &
                (merged_df['time'] <= merged_df['sunset_iso'])
                ]
            agg_daylight = _aggregate_data(daylight_df.groupby('date'), suffix='_daylight')
            # merged_df.drop('date', axis=1, inplace=True)

            final_df = done_daily_df.set_index('date')
            final_df = final_df.join(agg_24h).join(agg_daylight)

            return final_df
        except (KeyError, TypeError) as error:
            print(f"Transformer error: {error}")
            raise
        except Exception as error:
            print(f"Transformer unknown error: {error}")
            raise
