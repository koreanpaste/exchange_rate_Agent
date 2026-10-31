import requests
from langchain_core.tools import tool

@tool
def get_exchange_rate(base: str, quote: str) -> str:
    """두 통화 간 최신 환율을 조회합니다. base, quote는 통화 코드(예: USD, KRW, JPY, EUR)."""
    url = f"https://api.frankfurter.dev/v2/rate/{base.lower()}/{quote.lower()}"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    data = res.json()
    date = data.get("date", "")
    return f"1 {base.upper()} = {data['rate']} {quote.upper()} (기준일: {date})"