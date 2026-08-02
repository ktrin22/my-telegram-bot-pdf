import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

TOKEN = '8811607158:AAGIoLeOrctkPEeVRaH91PjywTt6dRdOiHQ'   # Временно
CHANNEL_ID = '@Simple_Word_English'

FILES = {
    "book1": {"path": "files/Английский для путешествий- Simple_Word_English_Workbook.pdf", "name": "Английский для путешествий"},
    "book2": {"path": "files/200 глаголов_Simple_Word_English.pdf", "name": "200 глаголов"},
    "book3": {"path": "files/200 слов Шопинг  - Simple Word English.pdf", "name": "200 слов Шопинг"}, 
    "book4": {"path": "files/110 слов Офис и работа - Simple Word English.pdf", "name": "110 слов Офис и работа"}, 
    "book5": {"path": "files/100 +10 Прилагательных - Simple Word English.pdf", "name": "100 +10 Прилагательных"}
}

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)  # В aiogram 2.x нужно передавать bot в Dispatcher

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# Используем старый синтаксис для команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for cmd, info in FILES.items():
        keyboard.add(InlineKeyboardButton(info["name"], callback_data=cmd))
    await message.answer("📚 Выберите книгу:", reply_markup=keyboard)

# Старый синтаксис для callback
@dp.callback_query_handler(lambda c: c.data in FILES)
async def send_file(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not await is_subscribed(user_id):
        await callback.message.answer(f"❌ Подпишитесь на канал {CHANNEL_ID}")
        await callback.answer()
        return
    file_info = FILES[callback.data]
    with open(file_info["path"], "rb") as f:
        await callback.message.answer_document(f, caption=file_info["name"])
    await callback.answer()

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
