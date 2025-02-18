import json
import os

class Storage:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Storage, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, filename="products.json", image_folder="images"):
        if not hasattr(self, 'initialized'):
            self.filename = filename
            self.image_folder = image_folder
            self._load_data()

            if not os.path.exists(self.image_folder):
                os.makedirs(self.image_folder)
            
            self.initialized = True

    def _load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.data = json.load(f)
            if "next_item_id" not in self.data:
                self.data["next_item_id"] = 1
        else:
            self.data = {"categories": {}, "next_item_id": 1}

    def _save_data(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_category(self, category_name):
        if category_name not in self.data["categories"]:
            self.data["categories"][category_name] = []
            self._save_data()

    def rename_category(self, old_category_name, new_category_name):
        if old_category_name in self.data["categories"]:
            self.data["categories"][new_category_name] = self.data["categories"].pop(old_category_name)
            self._save_data()
            return True
        return False

    def delete_category(self, category_name, transfer_to_category=None):
        if category_name in self.data["categories"]:
            if transfer_to_category:
                if transfer_to_category not in self.data["categories"]:
                    self.add_category(transfer_to_category)
                self.data["categories"][transfer_to_category].extend(self.data["categories"][category_name])
            del self.data["categories"][category_name]
            self._save_data()
            return True
        return False

    def transfer_items_to_category(self, source_category, target_category):
        if source_category in self.data["categories"] and target_category in self.data["categories"]:
            self.data["categories"][target_category].extend(self.data["categories"].pop(source_category))
            self._save_data()
            return True
        return False

    def add_item(self, category, name, price, quantity, description, image_path):
        if category not in self.data["categories"]:
            self.add_category(category)

        item_id = self.data["next_item_id"]
        self.data["next_item_id"] += 1

        self.data["categories"][category].append({
            "id": item_id,
            "name": name,
            "price": price,
            "quantity": quantity,
            "description": description,
            "image_path": image_path
        })
        self._save_data()

    def delete_item(self, category, item_id):
        items = self.data["categories"].get(category, [])
        for i, item in enumerate(items):
            if item["id"] == item_id:
                image_path = item["image_path"]
                del self.data["categories"][category][i]
                self._save_data()
                self._load_data()
                if os.path.exists(image_path):
                    os.remove(image_path)
                return True
        return False

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

    def change_item_quantity(self, category, item_id, new_quantity):
        items = self.data["categories"].get(category, [])
        for item in items:
            if item["id"] == item_id:
                item["quantity"] = new_quantity
                self._save_data()
                return True
        return False

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
