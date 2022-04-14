from aiohttp import ClientSession
import pandas as pd
from datetime import datetime, timedelta


INTERVALS = {
    "m": [1, "min"],
    "h": [60, "hour"],
    "d": [1440, "day"],
    "w": [10080, "week"]
}
W1 = 9
W2 = 26
W3 = 52
D = 27


async def get_candles(
        exchange: str,
        base_symbol: str,
        quote_symbol: str,
        timeframe: str,
        max_results: int = 110
) -> pd.DataFrame:
    async with ClientSession() as session:
        if exchange == "binance":
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': f"{base_symbol}{quote_symbol}",
                'interval': timeframe,
                'limit': max_results
            }
            async with session.get(url=url, params=params) as resp:
                data = await resp.json()
            data = [d[:6] for d in data]
            df = pd.DataFrame(data, columns=["TIME", "OPEN", "HIGH", "LOW", "PRICE", "VOLUME"])
        elif exchange == "kucoin":
            url = "https://openapi-v2.kucoin.com/api/v1/market/candles"
            params = {
                'symbol': f"{base_symbol}-{quote_symbol}",
                'type': f"{timeframe[:-1]}{INTERVALS[timeframe[-1]][1]}",
                'startAt': compute_start_time(timeframe, max_results)
            }
            while True:
                async with session.get(url=url, params=params) as resp:
                    data = await resp.json()
                if data['code'] != '429000':  # Not Rate limited
                    break
            data = [d[:6] for d in reversed(data["data"])]
            df = pd.DataFrame(data, columns=["TIME", "OPEN", "PRICE", "HIGH", "LOW", "VOLUME"])
        else:
            raise NotImplementedError(f"Exchange {exchange} not implemented.")
        return df


def compute_start_time(timeframe: str, periods: int) -> int:
    amount = int(timeframe[:-1])
    unity = timeframe[-1]
    minutes = amount * INTERVALS[unity][0]
    time = timedelta(minutes=minutes)
    start_time = datetime.now() - periods * time
    return int(start_time.timestamp())


def compute_ichimoku(df: pd.DataFrame):
    df.rename(columns={"CLOSE": "PRICE"}, inplace=True)
    df['TK'] = (df['HIGH'].rolling(W1, min_periods=0).max() + df['LOW'].rolling(W1, min_periods=0).min()) / 2
    df['KJ'] = (df['HIGH'].rolling(W2, min_periods=0).max() + df['LOW'].rolling(W2, min_periods=0).min()) / 2
    df['CK'] = df['PRICE'].shift(-D, fill_value=df['PRICE'].iat[-1])
    df['SSA'] = ((df['TK'] + df['KJ']) / 2).shift(W2)
    df['SSB'] = ((df['HIGH'].rolling(W3).max() + df['LOW'].rolling(W3).min()) / 2).shift(W2)