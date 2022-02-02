import json
import os
import pymongo
from bson.objectid import ObjectId
import json
import os
from files.configs.items.associate_type import associate


class Item:
    def __init__(self, _id: ObjectId):
        self._id = _id
        client = pymongo.MongoClient("localhost", 27017)
        self.collection = client["stalker_rp"]["items"]
        self.data = self.collection.find_one({"_id": self._id})   

    def get_data(self):
        self.data = self.collection.find_one({"_id": self._id})
        return self.data

    def update(self, key, value):
        self.collection.update_one({"_id": self._id}, {'$set': {key: value}})

    def add_to_inventory(self, item):
        self.collection.update_one({"_id": self._id}, {'$push': {"inventory": item}})
        
    def __getitem__(self, item):
        return self.get_data()[item]


item_mask = {
        "tpl": "",
        "modules": {},
        "stats": {},
  }


def create_empty_item(tpl: str):
    item_json = get_info_for_tpl(tpl)
    del item_json["description"]
    del item_json["cost"]
    del item_json["name"]
    item_json["tpl"] = tpl
    client = pymongo.MongoClient("localhost", 27017)
    collection = client["stalker_rp"]["items"]
    r = collection.insert_one(item_json)
    print(r.inserted_id)
    item = {
        "_id": r.inserted_id,
        "tpl": tpl,
        "stackable": item_json["stackable"],

        "StackObjectsCount": 0

    }
    return r.inserted_id, item


def get_info_for_tpl(tpl):
    data = json.load(open(os.getcwd()+f"\\files\\configs\\items\\{associate[tpl]}\\{tpl}.json", encoding="utf-8"))
    return data

