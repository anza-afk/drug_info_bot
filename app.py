import filters
from aiologger.loggers.json import JsonLogger
from aiologger.handlers.files import AsyncFileHandler
from tempfile import NamedTemporaryFile
from aiohttp import ClientSession
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp
from settings import API_TOKEN
from filters.command_filter import CommandFilter
from aiohttp.client_exceptions import ContentTypeError

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
    await message.reply(
        (f"Hello, {message.from_user.full_name}!\n"
        "I am DrugBuddy!\nuse '/help'"
        "if you want to know me better!")
        )

@dp.message_handler(CommandHelp())
async def send_help(message: types.Message):
    """
    This handler will be called when user sends `/help` command
    """
    await message.reply(
        ("Hello!\nI'm DrugBuddy!\n"
        "use '/drug <your_drug_name>'"
        "to get similar drugs\n"
        "or '/acti <active ingredient name>'"
        "to get drugs with the same ingredient.")
        )


@dp.message_handler(CommandFilter())
async def get_data(message: types.Message):

    data_type = {
        '/drug': 'drug',
        '/acti': 'component',
    }

    command = message.get_command()
    data = message.get_args()
    if not data:
        await message.reply(
            f"Ожидалось, что будет введено название после комманды {command}"
            )

    async with ClientSession() as session: 
        url = f'http://127.0.0.1:8000/api/v1/drugs' #  change url to env variable
        params = {data_type[command]: data}
        async with session.get(url=url, params=params) as resp:
            resp_info = (f'{message.from_user.full_name}, '
                'request: {data}, status: {resp.status}'
                )
            try:
                api_response = await resp.json()
                await logger.info(resp_info)
            except ContentTypeError:
                await logger.error(resp_info)
            if resp.status in [200, 201]:
                res = ''
                # counter = 0  # Временная заглушка до улучшения квери с ценами
                for drug in api_response:
                    if any((
                        drug['name'].replace('®', '').split()[0] in res,
                        drug['name'].replace('®', '').split('-')[0] in res,
                        drug['name'].replace('®', '').split('(')[0] in res
                        )):
                        continue
                    ingridients = ', '.join([x['name'] for x in drug['active_ingredient']])
                    res += ("Найден препарат c действующим веществом"
                        f"{data}: {drug['name']}\n"
                        f"Активные вещества: {ingridients}\n"
                        f"{drug['pharmacological_class']}\n"
                        )

                    drug_recipe = 'Не известно'
                    if drug['recipe_only'] == True:
                        'Да'
                    elif drug['recipe_only'] == False:
                        drug_recipe = 'Нет'
                    
                    # if drug['form_of_release']:
                    #     res += f"Форма выпуска: {drug['form_of_release']}\n"

                    res += f"По рецепту: {drug_recipe}\n\n"

                    # counter += 1  # Временная заглушка до улучшения квери с ценами
                    # if counter == 10:  # Временная заглушка до улучшения квери с ценами
                    #     break
                await message.reply(res)

async def on_startup(dp):
    await logger.info('Bot starting!')
    filters.setup(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)