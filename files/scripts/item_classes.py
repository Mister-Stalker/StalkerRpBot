from files.scripts.items import Item, get_info_for_tpl
from files.scripts.users import User
from pprint import pformat


class Weapons(Item):
    def __init__(self, user: User, _id):
        super().__init__(_id)
        self.user = user
        self.info = self.get_configs()

    def reload(self, flag="", *args):
        if not flag:
            belt = Belts(user=self.user)
            magazine = belt.reload(self["tpl"], self["data"]["magazine"])
            if magazine == "no mag":
                return "no mag"
            else:
                self.update("data.magazine", magazine)
                return "done"

    def reload_r_slot(self, slot):
        belt = Belts(user=self.user)

        magazine = belt.reload_slot(self["tpl"], self["data"]["magazine"], slot)
        if magazine == "no mag":
            return "no mag"
        else:
            self.update("data.magazine", magazine)
            return "done"

    def reload_inv_slot(self, slot):
        magazine = self.user["inventory"][slot]
        if magazine["tpl"] not in self.info["parameters"]["magazines"]:
            return "no mag"
        else:
            self.user.remove_from_inventory(magazine["_id"])
            self.update("data.magazine", magazine)
            return "done"


class Belts(Item):
    def __init__(self, user: User):
        belt = user["equipment"]["slot_6"]
        if not belt:
            belt = user["equipment"]["slot_4"]
        self.user = user
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
    def __init__(self, user: User, _id):
        super().__init__(_id)
        self.user = user
        self.info = self.get_configs()
        print(f"[DEBUG]: Mag class init\n    mag_obj: {pformat(self.data)}")

    def reload(self, ammo_inv_id=None):
        if ammo_inv_id is None or ammo_inv_id == -1:
            ammo_old = [self["data"]["ammo_type"], self["data"]["ammo_count"]]
            ammo_obj = self.user.get_from_inventory_stackable(ammo_old[0])
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
            self.user.remove_from_inventory_stackable(ammo_obj["tpl"], reload_ammo_count)
            return "done"

        else:
            ammo_obj = self.user["inventory"][ammo_inv_id]
            print(ammo_obj)
            if ammo_obj["tpl"] in self.info["parameters"]["ammo"]:
                if ammo_obj["StackObjectsCount"] > 0:
                    ammo_old = [self["data"]["ammo_type"], self["data"]["ammo_count"]]
                    self.user.add_to_inventory_stackable(*ammo_old)
                    if ammo_obj["StackObjectsCount"] < self.info["parameters"]["mag_size"]:
                        self["data"]["ammo_type"] = ammo_obj["tpl"]
                        self["data"]["ammo_count"] = ammo_obj["StackObjectsCount"]
                        self.update("data.ammo_count", ammo_obj["StackObjectsCount"])
                        self.update("data.ammo_type", ammo_obj["tpl"])
                        self.user.remove_from_inventory_stackable(ammo_obj["tpl"], ammo_obj["StackObjectsCount"])
                    else:
                        self["data"]["ammo_type"] = ammo_obj["tpl"]
                        self["data"]["ammo_count"] = self.info["parameters"]["mag_size"]
                        self.update("data.ammo_count", self.info["parameters"]["mag_size"])
                        self.update("data.ammo_type", ammo_obj["tpl"])
                        self.user.remove_from_inventory_stackable(self["data"]["ammo_type"], self["data"]["ammo_count"])
                else:
                    return "no ammo"
            else:
                return "incorrect ammo"
            return "done"
