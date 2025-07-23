import os
import sqlite3
import pandas as pd


class Loader:
    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("Для загрузки требуется непустой DataFrame.")
        self.__df = df

    def _create_table(self, connection: sqlite3.Connection, table_name: str):
        pass

    def _prepare_df_for_db(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def load_to_csv(self, csv_path: str = "./../output/weather_data.csv"):
        try:
            dir_name = os.path.dirname(csv_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            print('Start saving CSV')
            self.__df.to_csv(csv_path, index=True)
            print('CSV has been saved')
        except IOError:
            raise IOError('Failed load data to CSV-file')

    def load_to_db(self, db_path: str, table_name: str = "weather_forecasts"):
        pass
