import pandas as pd

KNOTS_TO_M_PER_S = 0.514444
INCH_TO_MM = 25.4
FEET_TO_M = 0.3048


def unix_to_iso_8601(date: pd.Series) -> pd.Series:
    return pd.to_datetime(date, unit='s').dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def fahrenheit_to_celsius(temp_f: float) -> float | None:
    if pd.isna(temp_f):
        return None
    return (temp_f - 32) * 5 / 9


def knots_to_m_per_s(speed_kn: float) -> float | None:
    if pd.isna(speed_kn):
        return None
    return speed_kn * KNOTS_TO_M_PER_S


def inches_to_mm(precip_in: float) -> float | None:
    if pd.isna(precip_in):
        return None
    return precip_in * INCH_TO_MM


def feet_to_meters(dist_ft: float) -> float | None:
    if pd.isna(dist_ft):
        return None
    return dist_ft * FEET_TO_M
