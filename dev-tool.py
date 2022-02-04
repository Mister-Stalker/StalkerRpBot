import json

import pymongo


def update_item(item: dict, mask: dict):

    edited_item = mask | item

    for p in edited_item.keys():
        if type(edited_item[p]) == dict:
            edited_item[p] = mask[p] | edited_item[p]
    return edited_item


def update_db(db_name: str, mask: dict):
    client = pymongo.MongoClient("localhost", 27017)
    collection = client["stalker_rp"][db_name]
    for item in collection.find({}):
        collection.replace_one({"_id": item["_id"]}, update_item(item, mask), upsert=False)


if __name__ == '__main__':
    mask_ = json.load(open("files/configs/profile_mask.json"))
    print(mask_)
    update_db("users", mask_)
