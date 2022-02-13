import json
import os
import pymongo
from bson.objectid import ObjectId
from files.scripts import items


class User:
    def __init__(self, _id: ObjectId):
        self._id = _id
        client = pymongo.MongoClient("localhost", 27017)
        self.collection = client["stalker_rp"]["npc"]
        self.data = self.collection.find_one({"_id": self._id})
        self.is_reg = bool(self.data)

    def get_data(self):
        return self.collection.find_one({"_id": self._id})

    def update(self, key, value):
        self.collection.update_one({"_id": self._id}, {'$set': {key: value}})

    def add_to_inventory_stackable(self, tpl, count=1):
        self.get_data()
        if not items.get_info_for_tpl(tpl)["stackable"]:
            return
        flag = True
        for i, item in enumerate(self.data["inventory"]):
            if item["tpl"] == tpl:
                item["StackObjectsCount"] += count
                flag = False
                self.collection.update_one({"_id": self._id}, {'$pull': {"inventory": {"tpl": tpl}}})
                self.collection.update_one({"_id": self._id}, {'$push': {"inventory": item}})
        if flag:
            item = {
                "tpl": tpl,
                "stackable": True,
                "StackObjectsCount": count
            }
            self.collection.update_one({"_id": self._id}, {'$pull': {"inventory": {"tpl": tpl}}})
            self.collection.update_one({"_id": self._id}, {'$push': {"inventory": item}})

    def get_from_inventory_stackable(self, tpl):
        self.get_data()
        if not items.get_info_for_tpl(tpl)["stackable"]:
            return
        for i, item in enumerate(self.data["inventory"]):
            if item["tpl"] == tpl:
                return item
        return None

    def remove_from_inventory_stackable(self, tpl, count):
        self.get_data()
        if not items.get_info_for_tpl(tpl)["stackable"]:
            return
        flag = True
        print("remove", tpl, count)
        for i, item in enumerate(self.data["inventory"]):
            if item["tpl"] == tpl:
                item["StackObjectsCount"] -= count
                if item["StackObjectsCount"] < 0:
                    item["StackObjectsCount"] = 0
                flag = False
                print(item)
                self.collection.update_one({"_id": self._id}, {'$pull': {"inventory": {"tpl": tpl}}})
                self.collection.update_one({"_id": self._id}, {'$push': {"inventory": item}})
        if flag:
            return "no obj"
        return "del"

    def get_from_inventory(self, item_id):
        self.get_data()
        return list(filter(lambda x: not x["stackable"] and x["_id"] == item_id, self.data["inventory"]))[0]

    def get_from_inventory_tpl(self, tpl):
        self.get_data()
        if items.get_info_for_tpl(tpl)["stackable"]:
            return
        _items = []
        for i, item in enumerate(self.data["inventory"]):
            if item["tpl"] == tpl:
                _items.append(item)
        return _items

    def add_to_inventory(self, item):
        self.collection.update_one({"_id": self._id}, {'$push': {"inventory": item}})

    def remove_from_inventory(self, item_id):
        self.collection.update_one({"_id": self._id}, {'$pull': {"inventory": {"_id": ObjectId(item_id)}}})

    def __getitem__(self, item):
        return self.get_data()[item]
