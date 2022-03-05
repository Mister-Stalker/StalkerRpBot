import random

body_parts_translate = {
    "голова": "head",
    "": "body",
    "тело": "body",
    "рука": ["left_arm", "right_arm"],
    "левая рука": "left_arm",
    "правая рука": "right_arm",
    "нога": ["right_leg", "left_leg"],
    "правая нога": "right_leg",
    "левая нога": "left_leg",

}

npc_body_parts_translate = {

}


def translate_body_part(name, is_human=True) -> str:
    if is_human:
        if name in body_parts_translate.keys():
            r = body_parts_translate[name]
            if type(r) == list:
                return random.choice(r)
            return r

        else:
            return ""
    else:
        return ""
