import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = '@Simple_Word_English'

FILES = {
    "book1": {"path": "my_bot/files/Английский для путешествий- Simple_Word_English_Workbook.pdf", "name": "Английский для путешествий"},
    "book2": {"path": "my_bot/files/200 глаголов_Simple_Word_English.pdf", "name": "200 глаголов"},
    "book3": {"path": "my_bot/files/200 слов Шопинг  - Simple Word English.pdf", "name": "200 слов Шопинг"}, 
    "book4": {"path": "my_bot/files/110 слов Офис и работа - Simple Word English.pdf", "name": "110 слов Офис и работа"}, 
    "book5": {"path": "my_bot/files/100 +10 Прилагательных - Simple Word English.pdf", "name": "100 +10 Прилагательных"}
}

# Статистика скачиваний
download_stats = {key: 0 for key in FILES.keys()}

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for cmd, info in FILES.items():
        keyboard.add(InlineKeyboardButton(info["name"], callback_data=cmd))
    
    welcome_text = (
        "👋 Добро пожаловать в библиотеку Simple Word English!\n\n"
        "📚 Чтобы скачать PDF-словарь, выберите нужный файл ниже.\n"
        "🔔 Для доступа необходимо быть подписанным на наш канал @Simple_Word_English.\n\n"
        "✅ Подпишитесь и скачивайте файлы бесплатно!"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in FILES)
async def send_file(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not await is_subscribed(user_id):
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(
            text="📢 Подписаться на канал",
            url="https://t.me/Simple_Word_English"
        ))
        await callback.message.answer(
            f"❌ Для доступа к файлам необходимо подписаться на канал @Simple_Word_English.\n"
            f"Нажмите кнопку ниже, чтобы подписаться, а затем попробуйте снова.",
            reply_markup=keyboard
        )
        await callback.answer()
        return
    
    file_info = FILES[callback.data]
    
    # Увеличиваем счётчик
    download_stats[callback.data] += 1
    print(f"📊 Файл '{file_info['name']}' скачан {download_stats[callback.data]} раз(а)")
    
    with open(file_info["path"], "rb") as f:
        await callback.message.answer_document(f, caption=file_info["name"])
    await callback.answer()

@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    # Замените 123456789 на ваш Telegram ID
    if message.from_user.id != 477713863:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    stats_text = "📊 Статистика скачиваний:\n\n"
    for key, count in download_stats.items():
        stats_text += f"📄 {FILES[key]['name']}: {count} скачиваний\n"
    
    await message.answer(stats_text)

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
