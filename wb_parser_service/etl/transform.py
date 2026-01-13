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
    df['sunrise_iso'] = converters.unix_to_iso_8601(data['sunrise'])
    df['sunset_iso'] = converters.unix_to_iso_8601(data['sunset'])
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
    return df


def _aggregate_data(grouped_df, suffix: str) -> pd.DataFrame:
    agg_dict = {
        f'avg_temperature_2m{suffix}': ('temperature_2m_celsius', 'mean'),
        f'avg_relative_humidity_2m{suffix}': ('relative_humidity_2m', 'mean'),
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


def _structure_final_df(df: pd.DataFrame) -> pd.DataFrame:
    final_columns_order = [
        # Почему я добавил время? Для идентификации
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

    existing_columns = [col for col in final_columns_order if col in df.columns]
    return df[existing_columns]


class Transformer:
    # TODO: Если будет время, добавить валидацию и очистку данных на NaN-значения
    def __init__(self, raw_data: Dict[str, Any]):
        if not isinstance(raw_data, dict) or 'hourly' not in raw_data or 'daily' not in raw_data:
            raise ValueError("Dataframe initialization error in Transformer")
        self.__data = raw_data

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value: Dict[str, Any]):
        # TODO: Перенести валидацию Transformer.data в validators.py
        if not isinstance(value, dict) or 'hourly' not in value or 'daily' not in value:
            raise ValueError("Dataframe set error in Transformer")
        self.__data = value

    def run(self):
        try:
            print('Start data transform...')
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

            final_agg_df = done_daily_df.set_index('date')
            final_agg_df = final_agg_df.join(agg_24h).join(agg_daylight)

            cols_to_drop = ['sunrise_iso', 'sunset_iso']
            final_agg_df_for_join = final_agg_df.drop(
                columns=[col for col in cols_to_drop if col in final_agg_df.columns],
                errors='ignore'
            )

            final_df = merged_df.set_index('date')
            final_df = final_df.join(final_agg_df_for_join)

            final_df = _structure_final_df(final_df)

            print('Data transform done!')

            return final_df
        except (KeyError, TypeError) as error:
            print(f"Transformer error: {error}")
            raise
        except Exception as error:
            print(f"Transformer unknown error: {error}")
            raise
