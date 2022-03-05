import json
import os
import random
import asyncio
import pymongo
from bson.objectid import ObjectId
from files.scripts import translate
# import files.scripts.item_classes
# from files.scripts.item_classes import Weapons
from files.scripts import items


shoot_list = {
    "head": [
        ["head", 0.7],
        ["body", 0.3]
    ],
    "body": [
        ["body", 1]
    ],
    "left_arm": [
        ["left_arm", 0.8],
        ["body", 0.2]
    ],
    "right_arm": [
        ["right_arm", 0.8],
        ["body", 0.2]
    ],
    "left_leg": [
        ["left_leg", 0.8],
        ["body", 0.2]
    ],
    "right_leg": [
        ["right_leg", 0.8],
        ["body", 0.2]
    ],
}


class Player:
    shoot_list = shoot_list

    def __init__(self, discord_id: int):
        self.id = discord_id
        client = pymongo.MongoClient("localhost", 27017)
        self.collection = client["stalker_rp"]["players"]
        self.data = self.collection.find_one({"id": int(self.id)})
        self.is_reg = bool(self.data)
        print(f"[DEBUG] user init, is_reg: {self.is_reg}, {self.id}, {self.data}")

    def get_data(self):
        return self.collection.find_one({"id": self.id})

    def update(self, key, value):
        self.collection.update_one({"id": self.id}, {'$set': {key: value}})

    def add_to_inventory_stackable(self, tpl, count=1):
        self.get_data()
        if not items.get_info_for_tpl(tpl)["stackable"]:
            return
        flag = True
        for i, item in enumerate(self.data["inventory"]):
            if item["tpl"] == tpl:
                item["StackObjectsCount"] += count
                flag = False
                self.collection.update_one({"id": self.id}, {'$pull': {"inventory": {"tpl": tpl}}})
                self.collection.update_one({"id": self.id}, {'$push': {"inventory": item}})
        if flag:
            item = {
                "tpl": tpl,
                "stackable": True,
                "StackObjectsCount": count
            }
            self.collection.update_one({"id": self.id}, {'$pull': {"inventory": {"tpl": tpl}}})
            self.collection.update_one({"id": self.id}, {'$push': {"inventory": item}})

    def get_from_inventory_stackable(self, tpl):
        self.get_data()
        if not items.get_info_for_tpl(tpl)["stackable"]:
            return
        flag = True
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
                self.collection.update_one({"id": self.id}, {'$pull': {"inventory": {"tpl": tpl}}})
                self.collection.update_one({"id": self.id}, {'$push': {"inventory": item}})
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
        items_ = []
        for i, item in enumerate(self.data["inventory"]):
            if item["tpl"] == tpl:
                items_.append(item)
        return items_

    def add_to_inventory(self, item):
        self.collection.update_one({"id": self.id}, {'$push': {"inventory": item}})

    def remove_from_inventory(self, item_id):
        self.collection.update_one({"id": self.id}, {'$pull': {"inventory": {"_id": ObjectId(item_id)}}})

    def __getitem__(self, item):
        return self.get_data()[item]

    async def attack(self, opponent, shoot_type: str = "1", is_scope=False, scope_arg=""):
        from files.scripts.item_classes import Weapons
        weapon = Weapons(self)
        count = 1
        if weapon["data"]["lock"]:
            return "weapon_locked", {}
        if weapon["data"]["misfire"]:
            return "misfire", {}
        # weapon.update("data.lock", True)
        if not is_scope:
            if -1 in weapon.info["parameters"]["fire_modes"]:
                if shoot_type.isdigit():
                    count = int(shoot_type)
                    if count > 3:
                        if self["skills"][weapon.type] >= 100:
                            count += random.randint(1, 3)-2
                        else:
                            count = random.randint(3, 8)
                    elif count <= 0:
                        count = 1
                elif shoot_type in ["о", "а", "a"]:
                    count = random.randint(2, 4)
        else:
            if -1 in weapon.info["parameters"]["fire_modes"]:
                if shoot_type.isdigit():
                    count = int(shoot_type)
                    if count > 3:
                        if self["skills"][weapon.type] >= 100:
                            count += random.randint(1, 3) - 2
                        else:
                            count = random.randint(3, 8)
                    elif count <= 0:
                        count = 1
                elif shoot_type in ["о", "а", "a"] and self["skills"][weapon.type] >= 200:
                    count = random.randint(2, 4)
        real_shoots = 0
        hits = 0
        for i in range(count):
            try:
                r = await weapon.shoot(i, is_scope)
                print("r", r)
                ammo, weapon_dmg_k = r
            except:
                weapon.update("data.lock", False)
                return "error"
            real_shoots += 1
            if not ammo:
                continue
            if ammo == "misfire":
                weapon.update("data.lock", False)
                return "misfire", {"shoots": count, "real_shoots": real_shoots, "hits": hits}
            elif ammo == "no_ammo":
                weapon.update("data.lock", False)
                return "no_ammo", {"shoots": count, "real_shoots": real_shoots, "hits": hits}
            opponent.gun_damage(ammo, weapon["tpl"], scope_arg)
            hits += 1
            await asyncio.sleep(1 / weapon.info["parameters"]["rpm"])
        weapon.update("data.lock", False)
        return "done", {"shoots": count, "real_shoots": real_shoots, "hits": hits}

    def _gun_damage(self, body_part, ammo_tpl):
        from files.scripts.item_classes import Armor
        armor = Armor(self)
        damage = armor.damage(body_part, ammo_tpl)
        print(body_part)
        self.update(f"health.{body_part}.current", self["health"][body_part]["current"] - damage)

        if self["health"]["exhaustion"]["current"] >= self["health"]["exhaustion"]["max"]:
            self.kill()
        elif self["health"]["head"]["current"] <= 0:
            self.kill()

    def gun_damage(self, ammo_tpl, weapon_tpl, scope_arg):
        print(f"[DEBUG]: user damage. ammo: {ammo_tpl}, weapon: {weapon_tpl}, scope_arg: {scope_arg}")
        body_part = translate.translate_body_part(scope_arg)
        if not body_part:
            body_part = "body"

        r = random.random()
        d = 0
        for part in self.shoot_list[body_part]:
            d += part[1]
            if r <= d:
                body_part = part[0]
                break

        self._gun_damage(body_part, ammo_tpl)



    def kill(self):
        pass


class UserJson:
    def __init__(self, user_id: int):
        self.id = user_id
        self.json = json.load(open(str(os.getcwd()) + f"\\server\\profiles\\{user_id}.json"))

    def __getitem__(self, item):
        return self.json[item]

    def dump(self):
        json.dump(self.json, open(str(os.getcwd()) + f"\\server\\profiles\\{self.id}.json", "w"))
