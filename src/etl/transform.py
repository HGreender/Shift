import pandas as pd
from typing import Dict, Any
from .utils import converters

__all__ = [
    'Transformer'
]


def hourly_date_transform(data: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df['time'] = pd.to_datetime(data['time'], unit='s', utc=True)
    df['date'] = df['time'].dt.date
    return df


def daily_date_transform(data: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df['date'] = pd.to_datetime(data['time'], unit='s', utc=True).dt.date
    df['sunrise_iso'] = pd.to_datetime(data['sunrise'], unit='s', utc=True).dt.strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    df['sunset_iso'] = pd.to_datetime(data['sunset'], unit='s', utc=True).dt.strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    df['daylight_hours'] = data['daylight_duration'] / 3600
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

            done_hourly_df = hourly_date_transform(hourly_df)
            done_daily_df = daily_date_transform(daily_df)

            merged_df = pd.merge(done_hourly_df, done_daily_df[['date', 'sunrise_iso', 'sunset_iso']], on='date')
            merged_df.drop('date', axis=1, inplace=True)

            return merged_df
        except (KeyError, TypeError) as error:
            print(f"Transformer error: {error}")
            raise
        except Exception as error:
            print(f"Transformer unknown error: {error}")
            raise
