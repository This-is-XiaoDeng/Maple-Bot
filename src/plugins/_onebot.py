__all__ = ["send_group_msg", "delete_msg"]

from typing import TypeAlias

from nonebot import get_bot
from nonebot.adapters import Message, MessageSegment, MessageTemplate


ID: TypeAlias = str | int
UserID = GroupID = MessageID = ID
AnyMessage = str | Message | MessageSegment | MessageTemplate


async def send_group_msg(group_id: GroupID, message: AnyMessage):
    return await get_bot().send_group_msg(group_id=int(group_id), message=message)


async def delete_msg(message_id: MessageID):
    return await get_bot().delete_msg(message_id=int(message_id))
