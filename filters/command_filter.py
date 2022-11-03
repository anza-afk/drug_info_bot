from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

class CommandFilter(BoundFilter):
    async def check(self, message: types.Message):
        return message.get_command() in ('/drug', '/acti')