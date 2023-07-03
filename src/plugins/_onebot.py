__all__ = ["send_group_msg", "delete_msg"]

from typing import List, Dict

from nonebot import get_bot
from nonebot.adapters import Message, MessageSegment, MessageTemplate


ID = str | int
UserID = GroupID = MessageID = ID
AnyMessage = str | Message | MessageSegment | MessageTemplate
ForwardNode = Dict[str, str | Dict[str, AnyMessage | Dict[str, AnyMessage]]]


async def send_group_msg(group_id: GroupID, message: AnyMessage) -> MessageID:
    return (await get_bot().send_group_msg(
        group_id=int(group_id),
        message=message
    ))["message_id"]


async def delete_msg(message_id: MessageID) -> None:
    await get_bot().delete_msg(message_id=int(message_id))


async def get_group_member_info(
    group_id: GroupID,
    user_id: UserID,
    no_cache: bool = False
) -> Dict[str, str]:
    return await get_bot().get_group_member_info(
        group_id=int(group_id),
        user_id=int(user_id),
        no_cache=no_cache
    )


def custom_forward_node(
    name: str,
    uin: UserID,
    content: AnyMessage
) -> ForwardNode:
    return {
        "type": "node",
        "data": {
            "name": name,
            "uin": str(uin),
            "content": content
        }
    }


def referencing_forward_node(id_: MessageID)-> ForwardNode:
    return {
        "type": "node",
        "data": {
            "id": str(id_)
        }
    }


async def send_group_forward_msg(
    group_id: GroupID,
    messages: List[ForwardNode],
) -> None:
    await get_bot().send_group_forward_msg(
        group_id=int(group_id),
        messages=messages
    )


async def get_group_msg_history(
    message_seq: MessageID,
    group_id: GroupID
) -> List[AnyMessage]:
    return await get_bot().get_group_msg_history(
        message_seq=message_seq,
        group_id=int(group_id)
    )
