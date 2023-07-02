__all__ = ["text"]

import os
import re
from typing import cast

import yaml

from nonebot.adapters.onebot.v11 import MessageEvent

from ._store import JsonDict


langs = {}
lang_use = JsonDict("lang_use.json", "zh-hans")


for filename in os.listdir("lang"):
    lang = os.path.splitext(filename)[0]
    file_path = os.path.join("lang", filename)
    with open(file_path, "r", encoding="utf-8") as file:
        langs[lang] = yaml.safe_load(file)


def text(__lang: MessageEvent | str | int, __key: str, **kwargs):
    lang, key = __lang, __key
    if isinstance(lang, MessageEvent):
        lang = lang.user_id
    lang = str(lang)
    if lang.isdecimal():
        lang = lang_use[lang]

    def gets(data: dict, key: str):
        for subkey in key.split("."):
            data = data[subkey]
        return data

    try:
        data = gets(langs[lang], key)
    except KeyError:
        lang = lang_use.default
        data = gets(langs[lang], key)

    def repl(match: re.Match):
        matched = cast(str, match.group())
        expr = matched[2:-2]
        try:
            return str(eval(expr.strip(), {"__builtins__": None}, kwargs))
        except Exception as e:
            print(e)
            return matched

    return re.sub("{{.*?}}", repl, data, flags=re.DOTALL)
