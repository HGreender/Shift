import datetime

def validate_date(date_text: str):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Given: {date_text}. Expected: YYYY-MM-DD")