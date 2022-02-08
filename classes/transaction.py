from datetime import datetime


class Transaction:
    def __init__(self, data, value):
        self.id = data["transaction_id"]
        self.token = data["token_info"]["symbol"]
        self.from_wallet = data["from"]
        self.to_wallet = data["to"]
        self.value = value
        self.timestamp = datetime.fromtimestamp(data["block_timestamp"] / 1e3)

    def age(self):
        return datetime.now() - self.timestamp