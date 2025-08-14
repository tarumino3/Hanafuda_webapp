# クラス名の略称と正式名称の対応辞書
TYPE_ABBREVIATION_MAP = {
    'hkr': '光',
    'tne': 'タネ',
    'tan': '短冊',
    'kas': 'カス'
}

ITSUMONO_HACHIHACHI_RULES = {
    "game_name": "八八", "score_unit": "貫/点", "zetsuba_oba": True,
    "enable_orichin": False,   # 下り賃を有効化
    "enable_oikomi": False,  # 追い込み賃を有効化
    "enable_mizuten": False,   # みずてんを有効化
    "dekiyaku": {
        "五光": {"score": 144, "active": True, "is_variable": False, "hatto_applicable": False},
        "四光": {"score": 120, "active": True, "is_variable": False, "hatto_applicable": True},
        "猪鹿蝶": {"score": 84, "active": True, "is_variable": False, "hatto_applicable": True},
        "赤短": {"score": 84, "active": True, "is_variable": False, "hatto_applicable": True},
        "青短": {"score": 84, "active": True, "is_variable": False, "hatto_applicable": True},
        "七短": {"score": 120, "active": True, "is_variable": True, "hatto_applicable": False}
    },
    "teyaku": {
        "三本": {"score": 24, "active": True}, "立三本": {"score": 36, "active": True},
        "赤": {"score": 36, "active": True}, "短一": {"score": 36, "active": True},
        "十一": {"score": 36, "active": True},"光一": {"score": 48, "active": True},
        "空素": {"score": 48, "active": True},"喰付": {"score": 48, "active": True},
        "手四": {"score": 72, "active": True},"はねけん": {"score": 84, "active": True},
        "一二四": {"score": 96, "active": True},"四三": {"score": 240, "active": True},
        "二三本": {"score": 72, "active": True},"二立三本": {"score": 96, "active": True}
    },
    "special_yaku": {
        "素十六": {"score": 144, "active": True, "is_variable": True, "per_item_score": 24, "item_unit": "枚"},
        "二た八": {"score": 120, "active": True, "is_variable": True, "per_item_score": 12, "item_unit": "点"},
        "総八": {"score": 120, "active": True, "is_variable": False}
    },
    "card_scores": {"光": 20, "タネ": 10, "短冊": 5, "カス": 1}
}

DEFAULT_HACHIHACHI_RULES = {
    "game_name": "八八", "score_unit": "貫/点", "zetsuba_oba": True,
    "enable_orichin": True,   # 下り賃を有効化
    "enable_oikomi": True,  # 追い込み賃を有効化
    "enable_mizuten": True,   # みずてんを有効化
    "dekiyaku": {
        "五光": {"score": 144, "active": True, "is_variable": False, "hatto_applicable": False},
        "四光": {"score": 120, "active": True, "is_variable": False, "hatto_applicable": True},
        "赤短": {"score": 84, "active": True, "is_variable": False, "hatto_applicable": True},
        "青短": {"score": 84, "active": True, "is_variable": False, "hatto_applicable": True},
        "七短": {"score": 120, "active": True, "is_variable": True, "hatto_applicable": False}
    },
    "teyaku": {
        "三本": {"score": 24, "active": True}, "立三本": {"score": 36, "active": True},
        "赤": {"score": 36, "active": True}, "短一": {"score": 36, "active": True},
        "十一": {"score": 36, "active": True},"光一": {"score": 48, "active": True},
        "空素": {"score": 48, "active": True},"喰付": {"score": 48, "active": True},
        "手四": {"score": 72, "active": True},"はねけん": {"score": 84, "active": True},
        "一二四": {"score": 96, "active": True},"四三": {"score": 240, "active": True},
        "二三本": {"score": 72, "active": True},"二立三本": {"score": 96, "active": True}
    },
    "special_yaku": {
        "素十六": {"score": 144, "active": True, "is_variable": True, "per_item_score": 24, "item_unit": "枚"},
        "二た八": {"score": 120, "active": True, "is_variable": True, "per_item_score": 12, "item_unit": "点"},
        "総八": {"score": 120, "active": True, "is_variable": False}
    },
    "card_scores": {"光": 20, "タネ": 10, "短冊": 5, "カス": 1}
}

DEFAULT_KOIKOI_RULES = {
    "game_name": "こいこい",
    "score_unit": "文",
    "enable_orichin": False,   # 下り賃を有効化
    "enable_oikomi": False,  # 追い込み賃を有効化
    "enable_mizuten": False,   # みずてんを有効化
    "zetsuba_oba": False,
    "dekiyaku": {
        "五光": {"score": 15, "active": True, "is_variable": False, "hatto_applicable": False}, 
        "四光": {"score": 10, "active": True, "is_variable": False, "hatto_applicable": False},
        "雨四光": {"score": 8, "active": True, "is_variable": False, "hatto_applicable": False}, 
        "三光": {"score": 6, "active": True, "is_variable": False, "hatto_applicable": False},
        "猪鹿蝶": {"score": 5, "active": True, "is_variable": False, "hatto_applicable": False}, 
        "赤短": {"score": 6, "active": True, "is_variable": False, "hatto_applicable": False},
        "青短": {"score": 6, "active": True, "is_variable": False, "hatto_applicable": False}, 
        "花見で一杯": {"score": 5, "active": True, "is_variable": False, "hatto_applicable": False},
        "月見で一杯": {"score": 5, "active": True, "is_variable": False, "hatto_applicable": False},
        "タネ": {"score": 1, "active": True, "is_variable": True, "per_item_score": 1, "item_unit": "枚", "hatto_applicable": False},
        "短冊": {"score": 1, "active": True, "is_variable": True, "per_item_score": 1, "item_unit": "枚", "hatto_applicable": False},
        "カス": {"score": 1, "active": True, "is_variable": True, "per_item_score": 1, "item_unit": "枚", "hatto_applicable": False}
    },
    "teyaku": {},
    "special_yaku": {},
    "card_scores": {"光": 20, "タネ": 10, "短冊": 5, "カス": 1}
}
