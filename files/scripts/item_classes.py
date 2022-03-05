import asyncio
import random

from files.scripts.items import Item, get_info_for_tpl
from files.scripts.users import Player
from files.scripts.functions import rand
from pprint import pformat


class Weapons(Item):
    def __init__(self, player: Player, _id=None):
        self.player = player
        if _id is None:
            _id = self.player["equipment"][self.player["equipment"]["active_weapon"]]["_id"]
        super().__init__(_id)
        self.info = self.get_configs()
        self.type = self.info["parameters"]["type"]

    async def shoot(self, iterator, is_scope: bool):
        player_skill = self.player["skills"][self.type]
        player_k = 0.8

        if player_skill > 1000:
            player_k = 1
        elif player_skill > 100:
            player_k = 0.9

        if self["data"]["misfire"]:
            return "misfire", False
        scope_k = 0.4
        if is_scope:
            scope_k = 1  # Will be added in the future...
        weather_k = 1  # Will be added in the future...
        weapon_k = self.info["parameters"]["accuracy"]
        print(f"[DEBUG] weapon shoot: player_k={player_k}, scope_k={scope_k}, weather_k={weather_k}, "
              f"weapon_k={weapon_k}", "="*25)

        mag = Magazines(self.player, self["data"]["magazine"]["_id"])
        ammo_count = mag["data"]["ammo_count"]

        if ammo_count <= 0:
            return "no_ammo", False

        mag.update("data.ammo_count", ammo_count-1)

        dispersion = self.info["parameters"]["dispersion"]*iterator
        dispersion = min(dispersion, self.info["parameters"]["dispersion"]*5)

        if not rand(player_k * scope_k * weapon_k * weather_k - dispersion): 
            return False, False
        else:
            return mag["data"]["ammo_type"], self.info["parameters"]["damage_k"]

    def reload(self, flag="", *_):
        if not flag:
            belt = Belts(player=self.player)
            magazine = belt.reload(self["tpl"], self["data"]["magazine"])
            if magazine == "no mag":
                return "no mag"
            else:
                self.update("data.magazine", magazine)
                return "done"

    def reload_r_slot(self, slot):
        belt = Belts(player=self.player)

        magazine = belt.reload_slot(self["tpl"], self["data"]["magazine"], slot)
        if magazine == "no mag":
            return "no mag"
        else:
            self.update("data.magazine", magazine)
            return "done"

    def reload_inv_slot(self, slot):
        magazine = self.player["inventory"][slot]
        if magazine["tpl"] not in self.info["parameters"]["magazines"]:
            return "no mag"
        else:
            self.player.remove_from_inventory(magazine["_id"])
            self.update("data.magazine", magazine)
            return "done"


class Belts(Item):
    def __init__(self, player: Player):
        belt = player["equipment"]["slot_6"]
        if not belt:
            belt = player["equipment"]["slot_4"]
        self.user = player
        print(f"[DEBUG]: Belts class init\n    belt_obj: {pformat(belt)}")
        super().__init__(belt["_id"])

        self.info = self.get_configs()

    def reload_slot(self, weapon_tpl, old_mag=False, slot=None):
        weapon_info = get_info_for_tpl(weapon_tpl)
        m = self["data"]["belt"][slot]
        if not m:
            return "no mag"
        if not m["tpl"] in weapon_info["parameters"]["magazines"]:
            return "no mag"
        magazine = self["data"]["belt"][slot]

        if not old_mag or old_mag == "no_mag" or old_mag == "no mag":
            self.update(f"data.belt.{slot}", {})
        else:
            self.update(f"data.belt.{slot}", old_mag)

        return magazine

    def reload(self, weapon_tpl, old_mag=False):
        weapon_info = get_info_for_tpl(weapon_tpl)
        max_ammo_key = 0
        max_ammo = 0
        for key in self["data"]["belt"].keys():
            obj = self["data"]["belt"][key]
            if obj:
                if obj["tpl"] in weapon_info["parameters"]["magazines"]:
                    ammo = Item(obj["_id"])["data"]["ammo_count"]
                    if ammo > max_ammo:
                        max_ammo_key = key
        if max_ammo_key == 0:
            return "no mag"
        magazine = self["data"]["belt"][max_ammo_key]
        print(max_ammo_key)
        if not old_mag or old_mag == "no_mag":
            self.update(f"data.belt.{max_ammo_key}", {})
        else:
            self.update(f"data.belt.{max_ammo_key}", old_mag)

        return magazine


class Magazines(Item):
    def __init__(self, player: Player, _id):
        super().__init__(_id)
        self.player = player
        self.info = self.get_configs()
        print(f"[DEBUG]: Mag class init\n    mag_obj: {pformat(self.data)}")

    def reload(self, ammo_inv_id=None):
        if ammo_inv_id is None or ammo_inv_id == -1:
            ammo_old = [self["data"]["ammo_type"], self["data"]["ammo_count"]]
            ammo_obj = self.player.get_from_inventory_stackable(ammo_old[0])
            print(ammo_obj)
            if ammo_obj is None:
                return "no ammo"
            if ammo_obj["StackObjectsCount"] == 0:
                return "no ammo"
            if ammo_old[1] == self.info["parameters"]["mag_size"]:
                return "mag full"
            reload_ammo_count = self.info["parameters"]["mag_size"] - ammo_old[1]
            if reload_ammo_count > ammo_obj["StackObjectsCount"]:
                reload_ammo_count = ammo_obj["StackObjectsCount"]
            self["data"]["ammo_count"] = self["data"]["ammo_count"] + reload_ammo_count
            self.update("data.ammo_count", self["data"]["ammo_count"] + reload_ammo_count)
            self.player.remove_from_inventory_stackable(ammo_obj["tpl"], reload_ammo_count)
            return "done"

        else:
            ammo_obj = self.player["inventory"][ammo_inv_id]
            print(ammo_obj)
            if ammo_obj["tpl"] in self.info["parameters"]["ammo"]:
                if ammo_obj["StackObjectsCount"] > 0:
                    ammo_old = [self["data"]["ammo_type"], self["data"]["ammo_count"]]
                    self.player.add_to_inventory_stackable(*ammo_old)
                    if ammo_obj["StackObjectsCount"] < self.info["parameters"]["mag_size"]:
                        self["data"]["ammo_type"] = ammo_obj["tpl"]
                        self["data"]["ammo_count"] = ammo_obj["StackObjectsCount"]
                        self.update("data.ammo_count", ammo_obj["StackObjectsCount"])
                        self.update("data.ammo_type", ammo_obj["tpl"])
                        self.player.remove_from_inventory_stackable(ammo_obj["tpl"], ammo_obj["StackObjectsCount"])
                    else:
                        self["data"]["ammo_type"] = ammo_obj["tpl"]
                        self["data"]["ammo_count"] = self.info["parameters"]["mag_size"]
                        self.update("data.ammo_count", self.info["parameters"]["mag_size"])
                        self.update("data.ammo_type", ammo_obj["tpl"])
                        self.player.remove_from_inventory_stackable(self["data"]["ammo_type"],
                                                                    self["data"]["ammo_count"])
                else:
                    return "no ammo"
            else:
                return "incorrect ammo"
            return "done"


class Armor(Item):
    def __init__(self, player: Player):
        armor = player["equipment"]["slot_4"]
        if not armor:
            armor = player["equipment"]["slot_4"]
        self.player = player
        print(f"[DEBUG]: Belts class init\n    belt_obj: {pformat(armor)}")
        super().__init__(armor["_id"])

        self.info = self.get_configs()

    def damage(self, body_part, ammo_tpl):
        ammo_info = get_info_for_tpl(tpl=ammo_tpl)
        if ammo_info["parameters"]["damage"]["class"] >= self.info["parameters"]["armor"][body_part]["class"]:
            cond = self["data"]["condition"]
            self.update("data.condition", cond - ammo_info["parameters"]["damage"]["armor_2"])
            dmg = random.randint(ammo_info["parameters"]["damage"]["body"][0],
                                 ammo_info["parameters"]["damage"]["body"][1])
            c = self.info["parameters"]["armor"][body_part]["coefficient"]

            k = c - (c * (1 - cond) / 2)

            dmg *= k
            return dmg
        else:
            return 0