import json
import os
import random

import pymongo
from bson.objectid import ObjectId
from files.scripts import items


class NPCBase:
    def __init__(self, key, _id, db):
        self._id = _id
        self.key = key
        client = pymongo.MongoClient("localhost", 27017)
        self.collection = client["stalker_rp"][db]
        self.data = self.collection.find_one({key: _id})
        
    def get_data(self) -> dict:
        return self.collection.find_one({self.key: self._id})
    
    def update(self, key, value) -> None:
        self.collection.update_one({self.key: self._id}, {'$set': {key: value}})
    
    def add_to_inventory_stackable(self, tpl, count=1) -> None:
        self.get_data()
        if not items.get_info_for_tpl(tpl)["stackable"]:
            return
        flag = True
        for i, item in enumerate(self.data["inventory"]):
            if item["tpl"] == tpl:
                item["StackObjectsCount"] += count
                flag = False
                self.collection.update_one({self.key: self._id}, {'$pull': {"inventory": {"tpl": tpl}}})
                self.collection.update_one({self.key: self._id}, {'$push': {"inventory": item}})
        if flag:
            item = {
                "tpl": tpl,
                "stackable": True,
                "StackObjectsCount": count
            }
            self.collection.update_one({self.key: self._id}, {'$pull': {"inventory": {"tpl": tpl}}})
            self.collection.update_one({self.key: self._id}, {'$push': {"inventory": item}})

    def get_from_inventory_stackable(self, tpl) -> dict:
        self.get_data()
        if not items.get_info_for_tpl(tpl)["stackable"]:
            return {}
        for i, item in enumerate(self.data["inventory"]):
            if item["tpl"] == tpl:
                return item
        return {}

    def remove_from_inventory_stackable(self, tpl, count) -> bool:
        self.get_data()
        if not items.get_info_for_tpl(tpl)["stackable"]:
            return False
        flag = True
        print("remove", tpl, count)
        for i, item in enumerate(self.data["inventory"]):
            if item["tpl"] == tpl:
                item["StackObjectsCount"] -= count
                if item["StackObjectsCount"] < 0:
                    item["StackObjectsCount"] = 0
                flag = False
                print(item)
                self.collection.update_one({self.key: self._id}, {'$pull': {"inventory": {"tpl": tpl}}})
                self.collection.update_one({self.key: self._id}, {'$push': {"inventory": item}})
        return not flag

    def get_from_inventory(self, item_id) -> list:
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

    def add_to_inventory(self, item) -> None:
        self.collection.update_one({self.key: self._id}, {'$push': {"inventory": item}})

    def remove_from_inventory(self, item_id) -> None:
        self.collection.update_one({self.key: self._id}, {'$pull': {"inventory": {"_id": ObjectId(item_id)}}})
        
    def __getitem__(self, item):
        return self.get_data()[item]

    
class NPC(NPCBase):
    def __init__(self, _id: ObjectId):
        self._id = _id
        super().__init__("_id",  ObjectId(_id), "npc")
        self.config = self._get_config(self.data["tpl"])

    @staticmethod
    def create_new_npc(tpl):
        npc_json = json.load(open(os.getcwd()+fr"files/configs/npc/npc/{tpl}.json"))
        npc_json["health"]["max"] = random.randint(npc_json["health"]["max"][0], npc_json["health"]["max"][1])
        npc_json["health"]["min"] = npc_json["health"]["max"]
        inv = []
        for item in random.choice(npc_json["loot"]):
            if type(item) == list:
                inv.append(
                    {
                        "tpl": item[0],
                        "stackable": True,
                        "StackObjectCount": random.randint(item[1][0], item[1][1])
                    }
                )
            else:
                inv.append(items.create_empty_item(item)[1])
        del npc_json["loot"]

        client = pymongo.MongoClient("localhost", 27017)
        collection = client["stalker_rp"]["npc"]
        collection.insert_one(npc_json)

    @staticmethod
    def _get_config(name):
        d = json.load(open(os.getcwd()+fr"files/configs/npc/npc/{name}.json"))
        return d
    
    def attack(location):
        pass
    
    def gun_damage(self, ammo, weapon_tpl, scope_arg):
        print(f"[DEBUG]: npc damage. ammo: {ammo}, weapon: {weapon_tpl}, scope_arg: {scope_arg}")
        pass
    
    
class QuestNPC(NPCBase):
    def __init__(self, tpl):
        self.tpl = tpl
        super().__init__("tpl", tpl, "npc")
        self.config = self._get_config(self.tpl)
        
    @staticmethod
    def _get_config(name):
        d = json.load(open(os.getcwd()+fr"files/configs/npc/quest_npc/{name}.json"))
        return d
    
        
