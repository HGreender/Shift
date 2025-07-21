import pandas as pd
from typing import Dict, Any
from src.utils import converters


class Transformer:
    def __init__(self, raw_data: Dict[str, Any]):
        if not isinstance(raw_data, dict) or 'hourly' not in raw_data or 'daily' not in raw_data:
            raise ValueError("Transformer ValueError")
        self.__data = raw_data

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value: Dict[str, Any]):
        if not isinstance(value, dict) or 'hourly' not in value or 'daily' not in value:
            raise ValueError("Transformer ValueError")
        self.__data = value
