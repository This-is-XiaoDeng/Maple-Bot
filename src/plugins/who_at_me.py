import os
import re
from typing import cast, List, Dict

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from ._store import JsonDict
from ._onebot import (
    ForwardNode,
    send_group_forward_msg,
    get_group_member_info,
    custom_forward_node
)


AT_PATTERN = r"\[CQ:at,qq=(\d+|all)\]"


@on_regex(AT_PATTERN).handle()
async def at_handle(event: GroupMessageEvent) -> None:
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    history = JsonDict(os.path.join("wam", f"{group_id}.json"), list)
    info = await get_group_member_info(group_id, user_id)
    node = {
        "time": event.time,
        "id": event.message_id,
        "name": info["card"] or info["nickname"],
        "uin": user_id,
        "content": event.raw_message
    }
    target_ids = set(re.findall(AT_PATTERN, node["content"]))
    if "all" in target_ids:
        target_ids = ["all"]
    for target_id in target_ids:
        cast(List, history[target_id]).append(node)
    history.save()


@on_command("who-at-me", aliases={"wam"}).handle()
async def who_at_me_handle(event: GroupMessageEvent) -> None:
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    history = JsonDict(os.path.join("wam", f"{group_id}.json"), list)
    messages: List[ForwardNode] = history[user_id] + history["all"]
    messages = list(filter(lambda node: node["uin"] != user_id, messages))
    messages.sort(key=lambda node: cast(int, node["time"]), reverse=True)
    messages = list(map(
        lambda node: custom_forward_node(
            name=cast(Dict[str, str], node)["name"],
            uin=cast(Dict[str, str], node)["uin"],
            content=cast(Dict[str, str], node)["content"]
        ),
        messages
    ))
    await send_group_forward_msg(group_id, messages)
