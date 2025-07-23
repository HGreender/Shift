import pandas as pd
import pytest
from etl.utils import converters
# Да, импорт кривой - сделан только для docker'а
# При запуске обычного pytest не запустится, но выдаст ошибку при билде,
# если не пройдёт какой-либо тест


def test_unix_to_iso_8601():
    series = pd.Series([0, 86400])
    expected = pd.Series(['1970-01-01T00:00:00Z', '1970-01-02T00:00:00Z'])
    pd.testing.assert_series_equal(converters.unix_to_iso_8601(series), expected)


def test_fahrenheit_to_celsius():
    assert converters.fahrenheit_to_celsius(32) == 0.0
    assert converters.fahrenheit_to_celsius(212) == 100.0
    assert converters.fahrenheit_to_celsius(None) is None
    assert converters.fahrenheit_to_celsius(pd.NA) is None


def test_knots_to_m_per_s():
    assert converters.knots_to_m_per_s(1) == pytest.approx(0.514444)
    assert converters.knots_to_m_per_s(0) == 0.0
    assert converters.knots_to_m_per_s(None) is None
    assert converters.knots_to_m_per_s(pd.NA) is None


def test_inches_to_mm():
    assert converters.inches_to_mm(1) == 25.4
    assert converters.inches_to_mm(0) == 0.0
    assert converters.inches_to_mm(None) is None
    assert converters.inches_to_mm(pd.NA) is None


def test_feet_to_meters():
    assert converters.feet_to_meters(1) == pytest.approx(0.3048)
    assert converters.feet_to_meters(0) == 0.0
    assert converters.feet_to_meters(None) is None
    assert converters.feet_to_meters(pd.NA) is None
