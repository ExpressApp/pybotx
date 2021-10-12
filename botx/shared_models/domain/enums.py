from enum import auto

from botx.bot.models.commands.enums import AutoName


class ChatTypes(AutoName):
    PERSONAL_CHAT = auto()
    GROUP_CHAT = auto()
    CHANNEL = auto()
