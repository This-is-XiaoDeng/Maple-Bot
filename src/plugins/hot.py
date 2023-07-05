import os
from time import time
from datetime import date
from typing import List, Tuple, cast

from nonebot import require
from nonebot import on_command, on_message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from nonebot_plugin_apscheduler import scheduler

from ._lang import text
from ._store import JsonDict
from ._onebot import GroupID, get_group_name


require("nonebot_plugin_apscheduler")

MINUTE = 60
HOUR = 3600


def filter_stamps(stamps: List[int], expire_time: int = HOUR) -> List[int]:
    return list(filter(
        lambda stamp: int(time()) - stamp <= expire_time,
        stamps
    ))


@on_message().handle()
async def hot_counter_handle(event: GroupMessageEvent):
    stamps = JsonDict(os.path.join("hot", "stamps.json"), list[int])
    stamps[str(event.group_id)].append(event.time)
    JsonDict(os.path.join("hot", "days", f"{date.today().isoformat()}.json"))[
        str(event.group_id)] += 1
    JsonDict(os.path.join("hot", "total.json"))[str(event.group_id)] += 1


@scheduler.scheduled_job("cron", minute="*", id="update_stamps")
async def update_stamps():
    stamps = JsonDict(os.path.join("hot", "stamps.json"), list[int])
    for group_id, group_stamps in stamps.items():
        stamps[group_id] = filter_stamps(group_stamps)


@on_command("hot").handle()
async def hot_handle(
    matcher: Matcher,
    event: GroupMessageEvent,
    arg: Message = CommandArg()
):
    match str(arg).lower().strip():
        case "" | "-m" | "min":
            key = "hot.10min"
            stamps = JsonDict(os.path.join("hot", "stamps.json"), list[int])
            ranks = [
                (group_id, len(filter_stamps(group_stamps, 10*MINUTE)))
                for group_id, group_stamps in stamps.items()
            ]
        case "-h" | "hour":
            key = "hot.hour"
            stamps = JsonDict(os.path.join("hot", "stamps.json"), list[int])
            ranks = [
                (group_id, len(filter_stamps(group_stamps, HOUR)))
                for group_id, group_stamps in stamps.items()
            ]
        case "-d" | "day":
            key = "hot.day"
            ranks = JsonDict(os.path.join(
                "hot", "days", f"{date.today().isoformat()}.json")).items()
        case "-t" | "total":
            key = "hot.total"
            ranks = JsonDict(os.path.join("hot", "total.json")).items()
        case _:
            await matcher.finish()
    ranks = [
        (await get_group_name(group_id), count, int(group_id))
        for group_id, count in ranks
        if count != 0
    ]
    ranks.sort(key=lambda x: x[1], reverse=True)
    await matcher.send(text(event.user_id, key,
                            ranks=ranks, event=event))
