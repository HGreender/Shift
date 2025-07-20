from src.etl.extract import Extractor


def run_pipeline(args):
    raw_data = None
    extractor = Extractor(start_date=args.start_date, end_date=args.end_date)
    raw_data = extractor.run()




def main():
    pass

if __name__ == '__main__':
    main()
