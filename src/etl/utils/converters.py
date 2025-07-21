import pandas as pd


def hourly_date_convert(data: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df['time'] = pd.to_datetime(data['time'], unit='s', utc=True)
    df['date'] = df['time'].dt.date
    return df


def daily_date_convert(data: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df['date'] = pd.to_datetime(data['time'], unit='s', utc=True).dt.date
    df['sunrise_iso'] = pd.to_datetime(data['sunrise'], unit='s', utc=True).dt.strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    df['sunset_iso'] = pd.to_datetime(data['sunset'], unit='s', utc=True).dt.strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    df['daylight_hours'] = data['daylight_duration'] / 3600
    return df
