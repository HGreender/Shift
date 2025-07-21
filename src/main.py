import sys

from src.etl.extract import Extractor


def run_pipeline(args):
    try:
        raw_data = None
        if args.source == 'api':
            extractor = Extractor(start_date=args.start_date, end_date=args.end_date)
            raw_data = extractor.run_api_extraction()
        elif args.source == 'json':
            raw_data = Extractor.run_json_extraction(args.file_path)
    except Exception as error:
        print(f'Error: {error}')
        sys.exit(1)


def main():
    pass


if __name__ == '__main__':
    main()
