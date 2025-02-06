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
            self.data = {"categories": {}}

    def _save_data(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_category(self, category_name):
        if category_name not in self.data["categories"]:
            self.data["categories"][category_name] = []
            self._save_data()

    def add_item(self, category, name, price, quantity, description):
        if category not in self.data["categories"]:
            self.add_category(category)

        item_id = len(self.data["categories"][category]) + 1
        self.data["categories"][category].append({
            "id": item_id,
            "name": name,
            "price": price,
            "quantity": quantity,
            "description": description
        })
        self._save_data()

    def get_categories(self):
        return list(self.data["categories"].keys())

    def get_items_by_category(self, category):
        return self.data["categories"].get(category, [])
