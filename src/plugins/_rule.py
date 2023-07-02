__all__ = ["group"]

from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import GroupMessageEvent


def group(group_id: int | str):
    def wapper(event: GroupMessageEvent):
        return event.group_id == int(group_id)
    return Rule(wapper)
