import classes
from datetime import datetime, timedelta
from telebot.types import User, Chat
from typing import Union
TIMEOUT_MINUTES = 40
TIMEOUT = timedelta(minutes=TIMEOUT_MINUTES)
SQL_OLDEST_USED_WALLET = '''
    WITH available AS(
        SELECT id FROM wallets
        WHERE last_use=(SELECT min(last_use) FROM wallets)
        LIMIT 1
    )
    UPDATE wallets
    SET last_use=now()
    FROM available
    WHERE wallets.id=available.id
    RETURNING address
'''


class Purchase:
    def __init__(self, user: Union[User, Chat], plan: classes.Plan, db: classes.DataBase):
        self.user = user
        self.plan = plan
        self.db = db
        self.wallet = None
        self.transaction = None
        self.start_time = datetime.now()

    def get_wallet(self) -> str:
        self.check_expired()
        self.start_time = datetime.now()
        if not self.wallet:
            data = self.db.get(SQL_OLDEST_USED_WALLET)
            self.wallet = data[0][0]
        return self.wallet

    def get_price(self) -> float:
        return self.plan.get_price()

    def get_min_price(self) -> float:
        return self.get_price() - 1

    def check_expired(self):
        session_time = datetime.now() - self.start_time
        if session_time > TIMEOUT:
            raise TimeoutError