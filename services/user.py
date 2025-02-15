import json
import os

class UserManager:
    def __init__(self, filename="users.json"):
        self.filename = filename
        self._load_data()

    def _load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def _save_data(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def create_user(self, user_id, username):
        if str(user_id) not in self.data:
            self.data[str(user_id)] = {
                "username": username,
                "balance": 0.0,
                "orders": []
            }
            self._save_data()

    def get_balance(self, user_id):
        return self.data.get(str(user_id), {}).get("balance", 0.0)

    def add_balance(self, user_id, amount):
        if str(user_id) in self.data:
            self.data[str(user_id)]["balance"] += amount
            self._save_data()

    def subtract_balance(self, user_id, amount):
        if str(user_id) in self.data and self.data[str(user_id)]["balance"] >= amount:
            self.data[str(user_id)]["balance"] -= amount
            self._save_data()
            return True
        return False

    def add_order(self, user_id, order):
        if str(user_id) in self.data:
            self.data[str(user_id)]["orders"].append(order)
            self._save_data()

    def get_orders(self, user_id):
        return self.data.get(str(user_id), {}).get("orders", [])
