__all__ = ["send_group_msg", "delete_msg"]

from nonebot import get_bot


async def send_group_msg(group_id, message):
    return await get_bot().send_group_msg(group_id=group_id, message=message)


async def delete_msg(message_id):
    return await get_bot().delete_msg(message_id=message_id)
