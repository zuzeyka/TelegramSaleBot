import json
import os

class Storage:
    def __init__(self, filename="products.json"):
        self.filename = filename
        self._load_data()

    def _load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {"products": []}

    def _save_data(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_item(self, name, price, description):
        item_id = len(self.data["products"]) + 1
        self.data["products"].append({"id": item_id, "name": name, "price": price, "description": description})
        self._save_data()

    def get_all_items(self):
        return self.data["products"]
