
from email import message_from_file
from gettext import Catalog
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import asyncio
import aiohttp
from twilio.rest import Client
from conf import API_TOKEN, WEATHER_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

bot = Bot(token=API_TOKEN)
db = Dispatcher()  # Передаем хранилище в Dispatcher

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание клавиатуры
main_key = ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text='Погода')],
        [types.KeyboardButton(text='Время')]
    ],
    resize_keyboard=True
)

# Создание клавиатуры
catalog_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Погода', callback_data="weather")],
    [InlineKeyboardButton(text='Время', callback_data="time")]
])


@db.message(Command('menu'))
async def menu(message: types.Message):
    await message.answer('Меню', reply_markup=catalog_list)


@db.message(Command('start'))
async def send_welcome(message: types.Message):
    # await message.reply("Привет, КРИСТИНА я твой БОТ!")
    await message.answer(f'{message.from_user.first_name}, добро пожаловать!', reply_markup=main_key)
    # print("Привет, КРИСТИНА я твой БОТ!")
    logger.info(f"Sent welcome message to {message.from_user.username}")


@db.message(Command('time'))
async def send_time(message: types.Message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await message.reply(f"Текущее время: {current_time}")
    print(f"Текущее время: {current_time}")
    logger.info(f"Sent current time to {message.from_user.username}")


@db.message(Command('phone'))
async def send_phone(message: types.Message):
    # Удаляем команду и разбиваем текст на части
    # Разбиваем на 3 части: команда, номер и сообщение
    args = message.text.split(" ", 2)
    if len(args) < 3:
        await message.reply("Пожалуйста, укажите номер телефона и сообщение. Пример: /phone +375291586850 Привет!")
        return
    phone_number = args[1]  # Номер телефона
    text_message = args[2]   # Сообщение
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    try:
        sent_message = client.messages.create(
            from_='+18155521040',
            body=text_message,
            to=phone_number
        )
        logger.info(f"Отправлено сообщение с SID: {sent_message.sid}")
        await message.reply("Сообщение успешно отправлено!")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        await message.reply("Не удалось отправить сообщение. Проверьте номер телефона и попробуйте снова.")


@db.message(Command('weather'))
async def send_weather(message: types.Message):
    city = message.text.split(" ", 1)[1] if len(
        message.text.split(" ")) > 1 else None
    if not city:
        await message.reply("Пожалуйста, укажите город. Пример: /weather Москва")
        return

    async with aiohttp.ClientSession() as session:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                weather_description = data['weather'][0]['description']
                temperature = data['main']['temp']
                await message.reply(f"Погода в {city}:\nТемпература: {temperature}°C\nОписание: {weather_description}")
                logger.info(
                    f"Sent weather info for {city} to {message.from_user.username}")
            else:
                await message.reply("Не удалось получить данные о погоде. Проверьте название города.")
                logger.error(
                    f"Failed to get weather data for {city}: {response.status}")


@db.message(lambda message: message.text == 'Погода')
async def handle_weather_request(message: types.Message):
    await message.answer('Все норм!')


@db.callback_query(lambda c: c.data == 'time')
async def process_time_callback(callback_query: types.CallbackQuery):
    await send_time(callback_query.message)


async def main():
    try:
        print("Бот запущен ...")
        logger.info("Бот запущен ...")
        await db.start_polling(bot)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        logger.error(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
        logger.info("Бот остановлен.")

# Может еще чего тут удалить?
# ВСЕ ОТЛИЧНО. ВРОДЕ РАЗОБРАЛСЯ
# ЧТо то еще добавить?.ValueError