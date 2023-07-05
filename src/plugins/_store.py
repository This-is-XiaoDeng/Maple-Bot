import os
import json
from typing import Any, Callable, TypeVar, Generic

T = TypeVar("T")


def load_json(path: str, default_factory: Callable[[], T] = dict) -> T:
    if not os.path.exists(path):
        return default_factory()
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def dump_json(obj: Any, path: str) -> None:
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as file:
        json.dump(obj, file, ensure_ascii=False)


class JsonDict(dict, Generic[T]):
    def __init__(
        self,
        path: str,
        default_factory: Callable[[], T] = int
    ) -> None:
        self.path = os.path.join("data", path)
        data = load_json(self.path)
        assert isinstance(data, dict)
        super().__init__(data)
        self.default_factory = default_factory

    def __getitem__(self, key: str) -> T:
        if key not in self.keys():
            super().__setitem__(key, self.default_factory())
        return super().__getitem__(key)

    def save(self) -> None:
        dump_json(self, self.path)

    def __str__(self) -> str:
        return f"JsonDict at '{self.path}':\n{self}"

    def __del__(self) -> None:
        self.save()
