import pandas as pd
from typing import Dict, Any
from src.utils import converters


class Transformer:
    def __init__(self, raw_data: Dict[str, Any]):
        if not isinstance(raw_data, dict) or 'hourly' not in raw_data or 'daily' not in raw_data:
            raise ValueError("Transformer ValueError")
        self.__raw_data = raw_data

    @property
    def raw_data(self):
        return self.__raw_data

    @raw_data.setter
    def raw_data(self, value: Dict[str, Any]):
        self.__raw_data = value
