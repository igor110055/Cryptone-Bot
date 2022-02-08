

class Plan:
    def __init__(self, price: float, duraction: str):
        self.id = duraction.replace(" ", "_")
        self.price = price
        self.duraction = duraction

    def get_price(self) -> float:
        return self.price

    def show_duraction(self) -> str:
        if self.duraction == "1000 years":
            return "Lifetime"
        return self.duraction.title()

    def get_duraction(self) -> str:
        return self.duraction