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

        loader = Loader(transformed_df)
        if args.target == 'csv':
            if not args.output_file:
                raise ValueError("Output file path is required for CSV target.")
            loader.load_to_csv(args.output_file)
        elif args.target == 'db':
            db_path = os.getenv("DATABASE_FILE")
            if not db_path:
                raise ValueError("Database file not exist")
            loader.load_to_db(db_path)

    except Exception as error:
        print(f'Error: {error}')
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', required=True, choices=['api', 'json'])
    parser.add_argument('-f', '--file-path', help="Path to input JSON-file source")
    parser.add_argument('-start', '--start-date', help="Start date for API source")
    parser.add_argument('-end', '--end-date', help="End date for API source")
    parser.add_argument('-t', '--target', required=True, choices=['csv', 'db'])
    parser.add_argument('-o', '--output-file', help="Path for output CSV file")

    args = parser.parse_args()

    if args.source == 'api' and (not args.start_date or not args.end_date):
        parser.error("--start-date and --end-date are required for the --source api")
    if args.source == 'json' and not args.file_path:
        parser.error("--file-path is required for --source json")
    if args.target == 'csv' and not args.output_file:
        parser.error("--output-file is required for --target csv")

    run_pipeline(args)


if __name__ == '__main__':
    main()
    print('Done!')

    # answer = input('Do yo wanna print table?\nPrint "yes" if wanna: ')
    # if (answer.lower() == 'yes') or (answer.lower() == 'yes'):
    #     df = read_db(os.getenv("DATABASE_FILE"), "weather_forecasts")
    #     print(df)
