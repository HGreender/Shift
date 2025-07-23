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

    def run_csv_load(self, csv_path: str = "output/weather_data.csv"):
        pass

    def run_db_load(self, db_path: str, table_name: str = "weather_forecasts"):
        pass
