import json
import requests
from typing import Dict, Any

from src.utils.validators import validate_date


class Extractor:
    def __init__(
            self, start_date: str, end_date: str,
            latitude: float = 55.0344, longitude: float = 82.9434
    ):
        self._DAILY_PARAMS = "sunrise,sunset,daylight_duration"
        self._HOURLY_PARAMS = ("temperature_2m,relative_humidity_2m,dew_point_2m,"
                          "apparent_temperature,temperature_80m,temperature_120m,"
                          "wind_speed_10m,wind_speed_80m,"
                          "visibility,rain,showers,snowfall")
        self.__start_date = validate_date(start_date)
        self.__end_date = validate_date(end_date)
        self.__latitude = latitude
        self.__longitude = longitude

        self._base_url = "https://api.open-meteo.com/v1/forecast"

    @property
    def start_date(self) -> str:
        return self.__start_date

    @start_date.setter
    def start_date(self, value: str):
        validate_date(value)
        self.__start_date = value

    @property
    def end_date(self) -> str:
        return self.__end_date

    @end_date.setter
    def end_date(self, value: str):
        validate_date(value)
        self.__end_date = value

    @property
    def latitude(self) -> float:
        return self.__latitude

    @latitude.setter
    def latitude(self, value: float):
        if not (-90 <= value <= 90):
            raise ValueError('latitude must be from -90 to 90')
        self.__latitude = value

    @property
    def longitude(self) -> float:
        return self.__longitude

    @longitude.setter
    def longitude(self, value: float):
        if not (-180 <= value <= 180):
            raise ValueError('longitude must be from -180 to 180')
        self.__longitude = value

    @property
    def _params(self) -> Dict[str, Any]:
        params = {
            "latitude": self.__latitude,
            "longitude": self.__longitude,
            "daily": self._DAILY_PARAMS,
            "hourly": self._HOURLY_PARAMS,
            "timezone": "auto",
            "timeformat": "unixtime",
            "wind_speed_unit": "kn",
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
            "start_date": self.__start_date,
            "end_date": self.__end_date
        }
        return params

    def run_api_extraction(self) -> Dict[str, Any]:
        try:
            response = requests.get(self._base_url, params=self._params)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, ValueError) as error:
            raise error

    @staticmethod
    def run_json_extraction(file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            raise
