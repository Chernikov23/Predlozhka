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

# Идентификаторы администраторов и канала
admins = [1477027628, 1847134066]
CHANNEL_ID = -1002404691921  # ID канала "Любят"
PREDLOZHKA_BOT_LINK = "https://t.me/predlozhkait_bot"

message_store = {}

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
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

# Обработчик команды /start
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
        "Привет! Я бот предложка для каналов [Цитатник IThub](https://t.me/ithubquotes) и [В IThub SPB любят](https://t.me/V_IThub_SPB_love). Пишите свои идеи и предложения",
        reply_markup=keyboard
    )

# Обработчик нажатия кнопки "Quote"
@dp.callback_query(F.data == "Quote")
async def handle_quote(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.callback)
    await state.update_data(callback="Quote")
    await state.set_state(Form.message)
    await call.message.answer("Введите текст для Цитатника! *Не забудьте оставить имя автора цитаты*")

# Обработчик нажатия кнопки "Love"
@dp.callback_query(F.data == "Love")
async def handle_love(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.callback)
    await state.update_data(callback="Love")
    await state.set_state(Form.message)
    await call.message.answer('Введите текст для "В IThub любят"! *Не забудьте оставить имя автора цитаты*')

# Обработчик сообщений в состоянии Form.message
@dp.message(Form.message)
async def send_message(msg: Message, state: FSMContext):
    data = await state.get_data()
    callback = data.get('callback')
    name = msg.from_user.username or msg.from_user.first_name
    user_id = msg.from_user.id
    user_link = f"[{name}](tg://user?id={user_id})"

    message_text = msg.text or msg.caption or "Ошибка получения текста"

    forward_caption = f"Сообщение от {user_link} для {'ЦИТАТНИКА' if callback == 'Quote' else 'ЛЮБЯТ'}:"

    for admin_id in admins:
        # Первое сообщение — текст от пользователя
        await bot.send_message(chat_id=admin_id, text=message_text, parse_mode=ParseMode.MARKDOWN)

        # Второе сообщение — информация о пользователе
        await bot.send_message(chat_id=admin_id, text=forward_caption, parse_mode=ParseMode.MARKDOWN)

        # Сохраняем сообщение в памяти
        message_store[msg.message_id] = {"user_id": user_id, "text": message_text}

        # Кнопка "Опубликовать в любят"
        if callback == "Love":
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Опубликовать в любят", callback_data=f"publish:{msg.message_id}")]
                ]
            )
            await bot.send_message(chat_id=admin_id, text="Опубликовать?", reply_markup=keyboard)

    await msg.answer("Ваше сообщение *успешно отправлено* администраторам на рассмотрение!")
    await state.clear()

# Обработчик нажатия кнопки "Опубликовать в любят"
@dp.callback_query(F.data.startswith("publish:"))
async def publish_to_channel(call: CallbackQuery):
    _, message_id = call.data.split(":")
    message_id = int(message_id)

    # Получаем сохраненное сообщение
    data = message_store.get(message_id)
    if not data:
        await call.answer("Ошибка: сообщение не найдено!", show_alert=True)
        return

    user_id = data["user_id"]
    message_text = data["text"]

    user_link = f"[пользователя](tg://user?id={user_id})"

    post_text = f"{message_text}\n\n[Предложка]({PREDLOZHKA_BOT_LINK})"

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=post_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        await call.answer("Сообщение опубликовано в канал!", show_alert=True)

    except Exception as e:
        logging.error(f"Ошибка публикации: {e}")
        await call.answer("Ошибка при публикации!", show_alert=True)

# Запуск бота
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
