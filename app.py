import logging
import requests
from aiogram import Bot, Dispatcher, executor, types
from settings import API_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hello!\nI'm DrugBuddy!\nuse '/help' if you want to know me better!")

@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hello!\nI'm DrugBuddy!\nuse '/drug <your_drug_name>' to get similar drugs\n or '/acti <active ingredient name>' to get drugs with the same ingredient.")


@dp.message_handler(commands=['drug',])
async def get_drug(message: types.Message):
    drug_name = message.text.replace('/drug ', '')
    if drug_name == '/drug':
        await message.reply("Ожидалось, что будет введено название препарата после комманды /test") 
    url = f'http://127.0.0.1:8000/api/v1/drugs/drug/{drug_name}'
    api_response = requests.get(url)
    print(api_response.status_code)
    if api_response.status_code in [200, 201]:
        drug_json = api_response.json()
        
        if len(drug_json)>0:
            for drug in drug_json:
                print(drug['active_ingredient'])
                ingridients = ', '.join([x['name'] for x in drug['active_ingredient']])
                await message.reply(f"Найден похожий на {drug_name} препарат: {drug['name']}\nАктивные вещества: {ingridients}")

@dp.message_handler(commands=['acti',])
async def get_active_ingredient(message: types.Message):
    active_ingredient_name = message.text.replace('/acti ', '')
    if active_ingredient_name == '/acti':
        await message.reply("Ожидалось, что будет введено название действующего вещества после комманды /acti") 
    url = f'http://127.0.0.1:8000/api/v1/drugs/ingredient/{active_ingredient_name}'
    api_response = requests.get(url)
    print(api_response.status_code)
    if api_response.status_code in [200, 201]:
        drug_json = api_response.json()
        
        if len(drug_json)>0:
            for drug in drug_json:
                print(drug['active_ingredient'])
                ingridients = ', '.join([x['name'] for x in drug['active_ingredient']])
                await message.reply(f"Найден препарат c действующим веществом {active_ingredient_name}: {drug['name']}\nАктивные вещества: {ingridients}")


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)