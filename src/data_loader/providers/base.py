from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional

class DataProvider(ABC):
    @abstractmethod
    def fetch_price(self, ticker: str, start: str, end: str) -> Optional[pd.DataFrame]:
        pass

    @abstractmethod
    def fetch_financials(self, ticker: str) -> Optional[pd.DataFrame]:
        pass
