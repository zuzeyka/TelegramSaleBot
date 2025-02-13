import json
import os

class Storage:
    def __init__(self, filename="products.json", image_folder="images"):
        self.filename = filename
        self.image_folder = image_folder
        self._load_data()

        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)

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

    def add_item(self, category, name, price, quantity, description, image_path):
        if category not in self.data["categories"]:
            self.add_category(category)

        item_id = len(self.data["categories"][category]) + 1
        self.data["categories"][category].append({
            "id": item_id,
            "name": name,
            "price": price,
            "quantity": quantity,
            "description": description,
            "image_path": image_path
        })
        self._save_data()

    def get_all_items(self):
        all_items = []
        for category, items in self.data["categories"].items():
            for item in items:
                all_items.append({
                    "category": category,
                    "id": item["id"],
                    "name": item["name"],
                    "price": item["price"],
                    "quantity": item["quantity"],
                    "description": item["description"]
                })
        return all_items

    def get_item(self, category, item_id):
        items = self.data["categories"].get(category, [])
        for item in items:
            if item["id"] == item_id:
                return item
        return None

    def edit_item_property(self, category, item_id, property_name, new_value):
        items = self.data["categories"].get(category, [])
        for item in items:
            if item["id"] == item_id:
                item[property_name] = new_value
                self._save_data()
                return True
        return False

    def edit_item_image(self, category, item_id, new_image_path):
        items = self.data["categories"].get(category, [])
        for item in items:
            if item["id"] == item_id:
                item["image_path"] = new_image_path
                self._save_data()
                return True
        return False

    def get_categories(self):
        return list(self.data["categories"].keys())

    def get_items_by_category(self, category):
        return self.data["categories"].get(category, [])
