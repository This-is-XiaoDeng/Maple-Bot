import asyncio
from random import randint, choice
from datetime import timedelta

from sympy import simplify

from nonebot import on_command, on_regex
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from ._lang import text
from ._credit import credits
from ._onebot import send_group_msg, delete_msg
from ._rule import group


@on_command("quick-math", aliases={"qm"}).handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    user_id = str(event.user_id)
    a = randint(1, 10)
    b = randint(1, 10)
    op = choice(["+", "-", "*", "/", "%", "//", "**"])
    if op == "**":
        b = randint(0, 3)
    message_id = (await send_group_msg(event.group_id, text(
        user_id,
        "quick-math.question",
        a=a, op=op, b=b
    )))["message_id"]
    ans = simplify(f"{a}{op}{b}")
    if ans.q != 1:
        ans = f"{ans.p}\s*?[/÷]\s*?{ans.q}"
    ans = f"^\s*?{ans}\s*?$"

    @on_regex(
        ans,
        rule=group(event.group_id),
        temp=True,
        expire_time=timedelta(seconds=10)
    ).handle()
    async def _(matcher: Matcher):
        credit = randint(1, 3)
        credits[user_id] += credit
        await matcher.send(text(
            user_id,
            "quick-math.correct",
            got=credit,
            total=credits[user_id]
        ), at_sender=True)
    await asyncio.sleep(10)
    await delete_msg(message_id)
