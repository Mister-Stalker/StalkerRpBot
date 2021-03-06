import json
import os
import pymongo
from bson.objectid import ObjectId
import json
import os



class ErrorItemType(Exception):
    pass


class Item:
    associate = {}
    def __init__(self, _id: ObjectId):
        self._id = _id
        client = pymongo.MongoClient("localhost", 27017)
        self.collection = client["stalker_rp"]["items"]

        self.data = self.collection.find_one({"_id": self._id})
        self.info = self.get_configs()

    def get_data(self):
        self.data = self.collection.find_one({"_id": self._id})
        return self.data

    def update(self, key, value):
        self.collection.update_one({"_id": self._id}, {'$set': {key: value}})
        
    def __getitem__(self, item):
        return self.get_data()[item]
    
    @staticmethod
    def get_info_for_tpl(tpl: str):
        item_type = None
        if tpl in Item.associate.keys():
            item_type = associate[tpl]
        else:
            for folder in os.listdir(os.getcwd() + f"\\files\\configs\\items\\"):
                if tpl + ".py" in os.listdir(os.getcwd() + f"\\files\\configs\\items\\{folder}"):
                    item_type = folder
            if item_type is None:
                raise ErrorItemType

            Item.associate[tpl] = item_type
        data = json.load(open(os.getcwd() + f"\\files\\configs\\items\\{item_type}\\{tpl}.json", encoding="utf-8"))
        return data
    
    # @staticmethod
    # def get_info_for_tpl(tpl):
    #     data = json.load(open(os.getcwd() + f"\\files\\configs\\items\\{associate[tpl]}\\{tpl}.json", encoding="utf-8"))
    #     return data

    def get_type(self):
        return associate[self.data["tpl"]]

    def get_configs(self):
        return get_info_for_tpl(self.data["tpl"])


item_mask = {
        "tpl": "",
        "modules": {},
        "stats": {},
  }


def create_empty_item(tpl: str):
    item_json = get_info_for_tpl(tpl)
    del item_json["description"]
    del item_json["parameters"]
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
    return Item.get_info_for_tpl(tpl)

