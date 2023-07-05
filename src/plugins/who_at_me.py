import os
import re
from typing import cast, List, Dict

from nonebot import on_command, on_regex, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from ._rule import group
from ._store import JsonDict
from ._onebot import (
    MessageType,
    send_group_forward_msg,
    get_group_member_info,
    custom_forward_node,
    get_group_msg_history,
    get_user_name
)


MessageNode = Dict[str, str | int]

AT_PATTERN = r"\[CQ:at,qq=(\d+|all)\]"

PREVIOUS_MESSAGE_COUNT = 7
NEXT_MESSAGE_COUNT = 7
assert PREVIOUS_MESSAGE_COUNT <= 18


def message_to_node(message: MessageType) -> MessageNode:
    return {
        "time": cast(int, message["time"]),
        "user_id": cast(str, message["user_id"]),
        "content": cast(str, message["message"])
    }


@on_regex(AT_PATTERN).handle()
async def at_handle(event: GroupMessageEvent) -> None:
    messages = await get_group_msg_history(event.group_id)
    messages = messages[-(1 + PREVIOUS_MESSAGE_COUNT):-1]
    messages = list(map(message_to_node, messages))
    node: MessageNode = {
        "time": event.time,
        "user_id": event.user_id,
        "content": event.raw_message
    }
    target_ids = set(re.findall(AT_PATTERN, cast(str, node["content"])))
    messages.append(node)
    if "all" in target_ids:
        target_ids = {"all"}
    history = JsonDict(os.path.join("wam", f"{event.group_id}.json"), dict)
    for target_id in target_ids:
        cast(Dict[str, List[MessageNode]], history[target_id])[
            str(event.message_id)] = messages
    history.save()

    message_count = NEXT_MESSAGE_COUNT
    matcher = on_message(group(event.group_id))

    @matcher.handle()
    async def at_successor_handle(sub_event: GroupMessageEvent) -> None:
        node: MessageNode = {
            "time": sub_event.time,
            "user_id": sub_event.user_id,
            "content": sub_event.raw_message
        }
        history = JsonDict(os.path.join("wam", f"{event.group_id}.json"), dict)
        for target_id in target_ids:
            cast(Dict, history[target_id])[str(event.message_id)].append(node)
        history.save()
        nonlocal message_count
        message_count -= 1
        if message_count == 0:
            matcher.destroy()


@on_command("who-at-me", aliases={"wam"}).handle()
async def who_at_me_handle(event: GroupMessageEvent) -> None:
    history = JsonDict(os.path.join("wam", f"{event.group_id}.json"), dict)
    messages = cast(List[List[MessageNode]],
                    list(history[str(event.user_id)].values()))
    messages += list(filter(
        lambda node: node[PREVIOUS_MESSAGE_COUNT]["user_id"] != event.user_id,
        cast(List[List[MessageNode]], history["all"].values())
    ))
    messages.sort(
        key=lambda node: node[PREVIOUS_MESSAGE_COUNT]["time"], reverse=True)

    async def subs(content: str) -> str:
        for matched in re.findall(AT_PATTERN, content):
            content = content.replace(f"[CQ:at,qq={matched}]", "[@{}]".format(
                "全体成员" if matched == "all"
                else await get_user_name(matched, event.group_id)
            ))
        return content

    await send_group_forward_msg(event.group_id, [
        await custom_forward_node(
            time=nodes[PREVIOUS_MESSAGE_COUNT]["time"],
            user_id=nodes[PREVIOUS_MESSAGE_COUNT]["user_id"],
            group_id=event.group_id,
            content=[
                await custom_forward_node(
                    time=cast(Dict[str, str], node)["time"],
                    user_id=cast(Dict[str, str], node)["user_id"],
                    group_id=event.group_id,
                    content=await subs(cast(Dict[str, str], node)["content"])
                )
                for node in nodes
            ]
        )
        for nodes in messages
    ])
