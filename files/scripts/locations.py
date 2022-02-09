import pymongo
from bson.objectid import ObjectId
import json
import os


class Item:
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

    def get_configs(self):
        return get_info_for_tpl(self.data["tpl"])


def create_empty_item(tpl: str):
    loc_json = get_info_for_tpl(tpl)

    loc_json["tpl"] = tpl
    client = pymongo.MongoClient("localhost", 27017)
    collection = client["stalker_rp"]["locations"]
    r = collection.insert_one(loc_json)
    print(r.inserted_id)
    item = {
        "_id": r.inserted_id,
        "tpl": tpl,
    }
    return r.inserted_id, item


def get_info_for_tpl(tpl):
    data = json.load(open(os.getcwd() + f"\\files\\configs\\locations\\{tpl}.json", encoding="utf-8"))
    return data
