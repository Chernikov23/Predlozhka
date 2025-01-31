from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
import asyncio
import os
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Идентификаторы администраторов
admins = [1477027628, 1847134066]

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
dp = Dispatcher()

# Определение состояний
class Form(StatesGroup):
    callback = State()
    message = State()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Бот запущен и работает...")

# Обработчик команды /start
@dp.message(CommandStart())
async def start(msg: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Цитатник IThub", callback_data="Quote"),
                InlineKeyboardButton(text="В IThub любят", callback_data="Love")
            ]
        ]
    )
    await msg.answer(
        "Привет\! Я бот предложка для каналов [Цитатник IThub](https://t.me/ithubquotes) и [В IThub SPB любят](https://t.me/V_IThub_SPB_love)\. Пишите свои идеи и предложения",
        reply_markup=keyboard
    )

# Обработчик нажатия кнопки "Quote"
@dp.callback_query(F.data == "Quote")
async def handle_quote(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.callback)
    await state.update_data(callback="Quote")
    await state.set_state(Form.message)
    await call.message.answer("Введите текст для Цитатника\! *Не забудьте оставить имя автора цитаты*")

# Обработчик нажатия кнопки "Love"
@dp.callback_query(F.data == "Love")
async def handle_love(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.callback)
    await state.update_data(callback="Love")
    await state.set_state(Form.message)
    await call.message.answer('Введите текст для "В IThub любят"\! *Не забудьте оставить имя автора цитаты*')

# Обработчик сообщений в состоянии Form.message
@dp.message(Form.message)
async def send_message(msg: Message, state: FSMContext):
    data = await state.get_data()
    callback = data.get('callback')
    name = msg.from_user.username or msg.from_user.first_name
    user_id = msg.from_user.id
    link = f"tg://user?id={user_id}"
    user_link = f"[{name}]({link})"

    forward_caption = f"Сообщение от {user_link} для {'ЦИТАТНИКА' if callback == 'Quote' else 'ЛЮБЯТ'}:"

    for admin_id in admins:
        await msg.forward(chat_id=admin_id)
        await bot.send_message(chat_id=admin_id, text=forward_caption)

    await msg.answer("Ваше сообщение *успешно отправлено* администраторам на рассмотрение\!")
    await state.clear()

# Запуск бота
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
