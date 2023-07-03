__all__ = ["JsonDict"]

import os
import json
from typing import Type, Any


def load_json(path: str, type_: Type = dict) -> Any:
    if not os.path.exists(path):
        return type_()
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def dump_json(obj: Any, path: str) -> None:
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as file:
        json.dump(obj, file)


class JsonDict:
    def __init__(self, path: str, default: Any = 0) -> None:
        self.path = os.path.join("data", path)
        self.data = load_json(self.path)
        assert isinstance(self.data, dict)
        self.default = default

    def __getitem__(self, key: str) -> Any:
        return self.data.get(key, self.default)

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value
        dump_json(self.data, self.path)

    def __deliem__(self, key: str) -> None:
        del self.data[key]
        dump_json(self.data, self.path)
