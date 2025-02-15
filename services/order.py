from datetime import datetime

class Order:
    def __init__(self, item_name, category, price, quantity):
        self.item_name = item_name
        self.category = category
        self.price = price
        self.quantity = quantity
        self.total_price = price * quantity
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "item_name": self.item_name,
            "category": self.category,
            "price": self.price,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "date": self.date
        }
