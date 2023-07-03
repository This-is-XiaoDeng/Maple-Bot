import os
import re
from typing import cast

from nonebot import on_command, on_regex
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from ._store import JsonDict
from ._onebot import send_group_forward_msg, get_group_member_info, custom_forward_node


@on_regex(r"\[CQ:at,qq=\d+\]").handle()
async def at_handle(event: GroupMessageEvent) -> None:
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    history = JsonDict(os.path.join("wam", f"{group_id}.json"), list)
    info = await get_group_member_info(group_id, user_id)
    node = info["card"] or info["nickname"], user_id, event.raw_message
    for target_id in set(re.findall(r"\[CQ:at,qq=(\d+)\]", event.raw_message)):
        cast(list, history[target_id]).append(node)
    history.save()


@on_command("wam").handle()
async def lang_handle(event: GroupMessageEvent) -> None:
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    history = JsonDict(os.path.join("wam", f"{group_id}.json"), list)
    messages = list(map(lambda x: custom_forward_node(*x), history[user_id]))
    await send_group_forward_msg(group_id, messages)
