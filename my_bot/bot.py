import asyncio
import os
import sqlite3
from datetime import datetime
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
    "book5": {"path": "my_bot/files/100 +10 Прилагательных - Simple Word English.pdf", "name": "100 +10 Прилагательных"},
    "book6": {"path": "my_bot/files/300 самых нужных слов - Simple Word English.pdf", "name": "От нуля до B2: 300 английских слов"},
    "book7": {"path": "my_bot/files/100 фразовых глаголов - Simple Word English.pdf", "name": "100 фразовых глаголов"}
}

DB_PATH = "my_bot/stats.db"

# ───────────────────────────────────────────
# База данных
# ───────────────────────────────────────────

def init_db():
    """Создаёт таблицы при первом запуске."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Общий счётчик скачиваний по файлу
    c.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            file_key  TEXT PRIMARY KEY,
            file_name TEXT,
            count     INTEGER DEFAULT 0
        )
    """)

    # Лог каждого скачивания (user_id + время)
    c.execute("""
        CREATE TABLE IF NOT EXISTS download_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            file_key  TEXT,
            user_id   INTEGER,
            username  TEXT,
            downloaded_at TEXT
        )
    """)

    # Инициализируем строки для всех файлов (если их ещё нет)
    for key, info in FILES.items():
        c.execute("""
            INSERT OR IGNORE INTO downloads (file_key, file_name, count)
            VALUES (?, ?, 0)
        """, (key, info["name"]))

    conn.commit()
    conn.close()


def increment_download(file_key: str, user_id: int, username: str):
    """Увеличивает счётчик и пишет строку в лог."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE downloads SET count = count + 1 WHERE file_key = ?", (file_key,))
    c.execute("""
        INSERT INTO download_log (file_key, user_id, username, downloaded_at)
        VALUES (?, ?, ?, ?)
    """, (file_key, user_id, username or "", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_stats() -> str:
    """Возвращает текст со статистикой для команды /stats."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT file_name, count FROM downloads ORDER BY count DESC")
    rows = c.fetchall()

    # Считаем уникальных пользователей
    c.execute("SELECT COUNT(DISTINCT user_id) FROM download_log")
    unique_users = c.fetchone()[0]

    # Всего скачиваний
    total = sum(r[1] for r in rows)

    conn.close()

    lines = ["📊 Статистика скачиваний:\n"]
    for name, count in rows:
        lines.append(f"📄 {name}: {count}")
    lines.append(f"\n📥 Всего скачиваний: {total}")
    lines.append(f"👤 Уникальных пользователей: {unique_users}")
    return "\n".join(lines)


# ───────────────────────────────────────────
# Бот
# ───────────────────────────────────────────

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


async def is_subscribed(user_id: int) -> bool:
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
            "❌ Для доступа к файлам необходимо подписаться на канал @Simple_Word_English.\n"
            "Нажмите кнопку ниже, чтобы подписаться, а затем попробуйте снова.",
            reply_markup=keyboard
        )
        await callback.answer()
        return

    file_key = callback.data
    file_info = FILES[file_key]
    username = callback.from_user.username

    # Сохраняем в БД
    increment_download(file_key, user_id, username)

    with open(file_info["path"], "rb") as f:
        await callback.message.answer_document(f, caption=file_info["name"])
    await callback.answer()


@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    if message.from_user.id != 477713863:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    await message.answer(get_stats())


async def main():
    init_db()  # создаём БД при старте
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
