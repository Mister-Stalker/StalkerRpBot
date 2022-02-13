import pymongo
from bson.objectid import ObjectId
import json
import os


def create_channel(_id, name=None, rp="no_rp"):
    if not name:
        name = f'channel_{_id}'
    locations = json.load(open(os.getcwd() + f"\\files\\configs\\locations\\locations.json", encoding="utf-8"))
    _id = str(_id)
    locations[_id] = name
    json.dump(locations, open(os.getcwd() + f"\\files\\configs\\locations\\locations.json", "w", encoding="utf-8"))
    loc_json = json.load(open(os.getcwd() + f"\\files\\configs\\locations\\mask.json", encoding="utf-8"))
    loc_json["id"] = _id
    loc_json["name"] = name
    loc_json["rp"] = rp
    json.dump(loc_json, open(os.getcwd() + f"\\files\\configs\\locations\\configs\\{name}.json", "w", encoding="utf-8"))
    tree = json.load(open(os.getcwd() + f"\\files\\configs\\locations\\location_tree.json", encoding="utf-8"))
    if not name in tree.keys():
        tree[name] = []
        json.dump(tree, open(os.getcwd() + f"\\files\\configs\\locations\\locations_tree.json", "w", encoding="utf-8"))
    client = pymongo.MongoClient("localhost", 27017)
    collection = client["stalker_rp"]["locations"]
    del loc_json["parameters"]
    collection.insert_one(loc_json)
    print(loc_json)
    return name, _id


class Locations:
    def __init__(self, _id=0, name=None) -> None:
        if _id != 0:
            if str(_id) in json.load(open(os.getcwd() + f"\\files\\configs\\locations\\locations.json",
                                     encoding="utf-8")).keys():
                name = get_name_for_id(int(_id))
            else:
                name, _ = create_channel(_id, name)
        print(name)
        self.name = name
        client = pymongo.MongoClient("localhost", 27017)
        self.collection = client["stalker_rp"]["locations"]

        self.data = self.collection.find_one({"name": self.name})
        self.info = self.get_configs()
        self.rp = True if self.info["rp"] == "rp" else False

    def get_data(self) -> dict:
        self.data = self.collection.find_one({"name": self.name})
        return self.data

    def update(self, key, value) -> None:
        self.collection.update_one({"name": self.name}, {'$set': {key: value}})

    def __getitem__(self, item):
        return self.get_data()[item]

    def get_configs(self) -> dict:
        return get_info_for_name(self.data["name"])

    def get_tree_channels(self) -> list:
        return json.load(open(os.getcwd() + f"\\files\\configs\\locations\\location_tree.json", encoding="utf-8"))[self.name]


def get_info_for_name(name: str) -> dict:
    return json.load(open(os.getcwd() + f"\\files\\configs\\locations\\configs\\{name}.json", encoding="utf-8"))


def get_name_for_id(_id):
    d = json.load(open(os.getcwd() + f"\\files\\configs\\locations\\locations.json", encoding="utf-8"))
    if str(_id) in d.keys():
        return d[str(_id)]
    return None
