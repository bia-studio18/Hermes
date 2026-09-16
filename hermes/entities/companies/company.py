from hermes.acquisition.cache import RawCache
from hermes.acquisition.client import Client

from hermes.connectors.sec import SECEDGAR
from hermes.connectors.yfinance import Yfinance

class Company:

    def __init__(self, company: dict[str, str], cache: RawCache | None = None):
        self._company = company
        self._sec = SECEDGAR()
        self._yf = Yfinance()
        
        self._cache = cache or RawCache()
        self._client = Client()
    
    @property
    def financials(self):
        ...

    @property
    def fillings(self):
        ...

    @property
    def market_data(self):
        ...
