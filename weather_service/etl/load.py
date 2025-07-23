import os
import sqlite3
import pandas as pd


class Loader:
    def __init__(self, df: pd.DataFrame):
        self.__df = df

    # TODO: тоже перекинуть в валидатор
    @property
    def df(self) -> pd.DataFrame:
        if not isinstance(self.__df, pd.DataFrame) or self.__df.empty:
            raise ValueError("Empty DataFrame")
        return self.__df

    @df.setter
    def df(self, value: pd.DataFrame):
        if not isinstance(value, pd.DataFrame) or value.empty:
            raise ValueError("Empty DataFrame")
        self.__df = value

    def load_to_csv(self, csv_path: str):
        try:
            csv_path = os.path.join('data', csv_path)
            dir_name = os.path.dirname(csv_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            print('Start saving CSV')
            self.__df.to_csv(csv_path, index=False)
            print('CSV has been saved')
        except IOError:
            raise IOError('Failed load data to CSV-file')
        except Exception:
            print(f"load_to_csv unknown error")
            raise

    def load_to_db(self, db_path: str = "data/weather_data.db", table_name: str = "weather_forecasts"):
        try:
            dir_name = os.path.dirname(db_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            print('Connecting to SQL...')
            with sqlite3.connect(db_path) as conn:
                print('Connected!')
                try:
                    existing_df = pd.read_sql(f"SELECT * FROM {table_name}", conn, parse_dates='time')
                    merged = pd.merge(self.df, existing_df, how='left', indicator=True)
                    df_to_insert = merged[merged['_merge'] == 'left_only'].drop('_merge', axis=1)
                except pd.errors.DatabaseError:
                    df_to_insert = self.df

                if not df_to_insert.empty:
                    print('Appending data in the DB...')
                    df_to_insert.to_sql(table_name, conn, if_exists='append', index=False)
                    print('Appended!')
            print('Connecting to SQL has been closed')
        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(f"load_to_db SQLite operational error: {e}") from e
        except sqlite3.DatabaseError as e:
            raise sqlite3.DatabaseError(f"load_to_db SQLite database error: {e}") from e
        except OSError as e:
            raise OSError(f"load_to_db OSError: {e}") from e
        except Exception as e:
            print(f"load_to_db unknown error")
            raise
