import os
import sys
import argparse

from etl.extract import Extractor
from etl.transform import Transformer
from etl.load import Loader
from etl.utils.db_tools import read_db


def run_pipeline(args):
    try:
        raw_data = None
        if args.source == 'api':
            extractor = Extractor(start_date=args.start_date, end_date=args.end_date)
            raw_data = extractor.run_api_extraction()
        elif args.source == 'json':
            raw_data = Extractor.run_json_extraction(args.file_path)

        transformer = Transformer(raw_data)
        transformed_df = transformer.run()

        # print(transformed_df.to_string())

        loader = Loader(transformed_df)
        if args.target == 'csv':
            loader.load_to_csv()
        elif args.target == 'db':
            # db_path = os.getenv("DATABASE_FILE")
            db_path = "./../output/weather_data.db"
            if not db_path:
                raise ValueError("Database file not exist")
            loader.load_to_db(db_path)

    except Exception as error:
        print(f'Error: {error}')
        sys.exit(1)


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-s', '--source', required=True, choices=['api', 'json'])
    # # parser.add_argument('--target', required=True, choices=['csv', 'db'])
    # parser.add_argument('--file-path', help="Path to JSON-file")
    # parser.add_argument('-start', '--start-date')
    # parser.add_argument('-end', '--end-date')
    #
    # args = parser.parse_args()
    #
    # if args.source == 'api' and (not args.start_date or not args.end_date):
    #     parser.error("--start-date и --end-date обязательны для --source api.")
    # if args.source == 'json' and not args.file_path:
    #     parser.error("--file-path обязателен для --source json.")

    class Args:
        def __init__(self):
            self.source = 'api'
            self.start_date = "2025-07-23"
            self.end_date = "2025-07-24"
            self.target = 'db'

    args = Args()

    run_pipeline(args)


if __name__ == '__main__':
    main()
    df = read_db("./../output/weather_data.db", "weather_forecasts")
    print(df.to_string())
