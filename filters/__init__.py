from aiogram import Dispatcher
from .command_filter import CommandFilter
 
def setup(dp: Dispatcher):
    pass
    dp.filters_factory.bind(CommandFilter)