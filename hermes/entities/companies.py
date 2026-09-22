from hermes.connectors.public_data.connector import sec_mapping

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
    return sec_mapping(symbol=ticker)


__all__ = ["get_cik"]
