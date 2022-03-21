from .alerts import PriceAlerts
from classes import DataBase


def get_coin_alerts(db: DataBase) -> list:
    coin_alerts = []
    data = db.get("SELECT exchange, base, quote FROM coins ORDER BY random()")
    for d in data:
        coin_alerts.append(PriceAlerts(*d))
    return coin_alerts