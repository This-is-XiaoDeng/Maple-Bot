from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from . import _lang
from ._lang import text


langs = _lang.langs.keys()


@on_command("lang").handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    user_id = str(event.user_id)
    match str(arg).lower().strip():
        case  "-l" | "list":
            await matcher.send(text(user_id, "lang.list", langs=langs))
        case lang if lang in langs:
            _lang.lang_use[user_id] = lang
            await matcher.send(text(user_id, "lang.set", lang=lang))
        case _:
            pass
