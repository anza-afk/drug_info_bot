import filters
from aiologger.loggers.json import JsonLogger
from aiologger.handlers.files import AsyncFileHandler
from tempfile import NamedTemporaryFile
from aiohttp import ClientSession
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp
from settings import API_TOKEN
from filters.command_filter import CommandFilter

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
temp_file = NamedTemporaryFile()
print(temp_file.name)
handler = AsyncFileHandler(filename=temp_file.name),
logger = JsonLogger.with_default_handlers(
            level='DEBUG',
            serializer_kwargs={'ensure_ascii': False},
        )

@dp.message_handler(CommandStart())
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    await message.reply(f"Hello, {message.from_user.full_name}!\nI am DrugBuddy!\nuse '/help' if you want to know me better!")

@dp.message_handler(CommandHelp())
async def send_help(message: types.Message):
    """
    This handler will be called when user sends `/help` command
    """
    await message.reply("Hello!\nI'm DrugBuddy!\nuse '/drug <your_drug_name>' to get similar drugs\n or '/acti <active ingredient name>' to get drugs with the same ingredient.")


@dp.message_handler(CommandFilter())
async def get_data(message: types.Message):

    data_type = {
        '/drug': 'drug',
        '/acti': 'component',
    }

    command = message.get_command()
    data = message.get_args()
    if not data:
        await message.reply(f"Ожидалось, что будет введено название после комманды {message.get_command()}")

    async with ClientSession() as session: 
        url = f'http://127.0.0.1:8000/api/v1/drugs'
        params = {data_type[command]: data}
        async with session.get(url=url, params=params) as resp:
            api_response = await resp.json()

            # print(message.from_user.full_name ,message.get_args(), resp.status)
            await logger.info(f'{message.from_user.full_name}, request: {message.get_args()}, status: {resp.status}')

            if resp.status in [200, 201]:
                counter = 0  # Временная заглушка до улучшения квери с ценами
                for drug in api_response:
                    ingridients = ', '.join([x['name'] for x in drug['active_ingredient']])
                    drug_recipe = 'Не известно'
                    if drug['recipe_only'] == True:
                        'Да'  
                    elif drug['recipe_only'] == False:
                        drug_recipe = 'Нет'

                    await message.reply(f"Найден препарат c действующим веществом {data}: {drug['name']}\nАктивные вещества: {ingridients}\n{drug['pharmacological_class']}\n\nПо рецепту: {drug_recipe}") #  {drug['form_of_release']}
                    counter += 1  # Временная заглушка до улучшения квери с ценами
                    if counter == 10:  # Временная заглушка до улучшения квери с ценами
                        break


async def on_startup(dp):
    await logger.info('Bot starting!')
    filters.setup(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)