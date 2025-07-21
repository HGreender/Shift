import pandas as pd
from typing import Dict, Any
from .utils import converters


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

            done_hourly_df = converters.hourly_date_convert(hourly_df)
            done_daily_df = converters.daily_date_convert(daily_df)

            merged_df = pd.merge(done_hourly_df, done_daily_df[['date', 'sunrise_iso', 'sunset_iso']], on='date')
            merged_df.drop('date', axis=1, inplace=True)

            return merged_df
        except (KeyError, TypeError) as error:
            print(f"Transformer error: {error}")
            raise
        except Exception as error:
            print(f"Transformer unknown error: {error}")
            raise
