from datetime import datetime, timedelta
from .api import get_candles, compute_ichimoku, D
import diskord
import pandas as pd


ALERT_COOLDOWN = timedelta(hours=1)     # Prevent moments of constant fluctuation from flooding a single alert
CHART_BASE = "https://en.tradingview.com/chart/?symbol={}%3A{}{}"


def build_alerts():
    return {
        '1d': [
            ProximityAlert("PRICE", "SSB", 0.01),
            YesterdayAlert("PRICE", "LOW", 0.01),
            YesterdayAlert("PRICE", "HIGH", 0.01),
            CrossAlert("PRICE", "SSB"),
            CrossAlert("PRICE", "KJ"),
            CrossAlert("PRICE", "TK"),
            CrossAlert("CK", "TK"),
            CrossAlert("CK", "KJ")
        ],
        '4h': [
            # Empty
        ]
    }


class PriceAlerts:
    def __init__(self, exchange: str, base_coin: str, quote_coin: str):
        self.exchange = exchange.lower()
        self.base_coin = base_coin.upper()
        self.quote_coin = quote_coin.upper()
        self.alerts = build_alerts()
        self.color = diskord.Colour.random()

    async def send_alerts(self, channel: diskord.TextChannel):
        for timeframe in self.alerts:
            if not self.alerts[timeframe]:
                continue
            df = await get_candles(self.exchange, self.base_coin, self.quote_coin, timeframe)
            compute_ichimoku(df)
            for alert in self.alerts[timeframe]:
                if alert.triggered(df):
                    emb = diskord.Embed(
                        description=f"$**{self.base_coin}** ➭ {alert.message} ({timeframe.upper()}) {self.get_chart_link()}",
                        color=self.color
                    )
                    await channel.send(embed=emb)

    def get_chart_link(self):
        return f"[Chart]({CHART_BASE.format(self.exchange, self.base_coin, self.quote_coin)})"


class Alert:
    def __init__(self, message: str, col1: str, col2: str):
        self.message = message
        self.col1 = col1
        self.col2 = col2
        self.status = None
        self.last_trigger_time = None

    def triggered(self, df: pd.DataFrame) -> bool:
        result = self.analyze(df)
        if result and not self.is_on_cooldown():
            self.last_trigger_time = datetime.utcnow()
            return True
        else:
            return False

    def get_columns(self) -> list:
        return [self.col1, self.col2]

    def get_values(self, df):
        i = -D if "CK" in self.get_columns() else -1
        a, b = df[self.col1].iloc[i], df[self.col2].iloc[i]
        return pd.to_numeric(a), pd.to_numeric(b)

    def analyze(self, df: pd.DataFrame) -> bool:
        a, b = self.get_values(df)
        return True

    def is_on_cooldown(self) -> bool:
        if not self.last_trigger_time:
            return False
        time = datetime.utcnow() - self.last_trigger_time
        return time < ALERT_COOLDOWN


class CrossAlert(Alert):    # It will be fired whenever col1 crosses col2
    def __init__(self, col1: str, col2: str):
        self.col1, self.col2 = col1, col2
        super().__init__(f"{col1} crossed the {col2}", col1, col2)

    def analyze(self, df: pd.DataFrame) -> bool:
        a, b = self.get_values(df)
        if a >= b:
            now_status = "above"
        else:
            now_status = "below"
        if self.status is None or self.status == now_status:
            cross = False
        else:
            cross = True
        self.status = now_status
        return cross


class ProximityAlert(Alert):    # It will be fired whenever col1 approaches n% of col2
    def __init__(self, col1: str, col2: str, proximity: float, msg: str = None):
        self.col1, self.col2 = col1, col2
        self.proximity = proximity
        if not msg:
            msg = f"{col1} is {proximity * 100:.0f}% from {col2}"
        super().__init__(msg, col1, col2)

    def analyze(self, df: pd.DataFrame) -> bool:
        a, b = self.get_values(df)
        if abs(a - b) / a < self.proximity:
            now_status = "near"
        else:
            now_status = "far"
        if self.status == "far" and now_status == "near":
            approached = True
        else:
            approached = False
        self.status = now_status
        return approached


class YesterdayAlert(ProximityAlert):   # It is a proximity alert, but it compares today's data with yesterday's
    def __init__(self, col1: str, col2: str, proximity: float):
        msg = f"{col1} is close to yesterday's {col2}"
        super().__init__(col1, col2, proximity, msg)

    def get_values(self, df):
        a, b = df[self.col1].iloc[-1], df[self.col2].iloc[-2]
        return pd.to_numeric(a), pd.to_numeric(b)
