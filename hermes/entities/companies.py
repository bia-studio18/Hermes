from sec_cik_mapper import StockMapper

"""
 each company should have these feild

{
  "hrm_id": "HRM-CMP-01K4Y8M2Z7FQ3N8",
  "legal_name": "Apple Inc.",
  "country": "United States",
  "jurisdiction": "US-DE",
  "registration_number": "C0806592",
  "registry_id": "California Secretary of State C0806592",
  "lei": "HWUPKR0MPOU8FGXBT394",
  "sec_cik": "0000320193",
  "ticker": "AAPL",
  "exchange": "NASDAQ",
  "isin": "US0378331005",
  "figi": "BBG000B9XRY4",
  "cusip": "037833100",
  "sedol": "2046251",
  "website": "https://www.apple.com",
  "domain": "apple.com"
}
"""


def get_cik(ticker: str) -> str:
    mapper = StockMapper()
    ticker_to_cik_dict = mapper.ticker_to_cik  # type: ignore[operator]

    cik = ticker_to_cik_dict.get(ticker.upper())
    return f"CIK{cik}" if cik else "Not Found"


__all__ = ["get_cik"]
