import os
import sqlite3
import logging
from aiogram import Bot, Dispatcher, executor, types

# 🔑 Token environment variable orqali olinadi
API_TOKEN = os.getenv("8169900677:AAEXIHrqPpH8B9feXuwP81xwe5RN27D_XGs")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# 📚 SQLite baza
conn = sqlite3.connect("books.db")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT,
    title TEXT
)""")
conn.commit()

# 📌 Guruhda fayl saqlash
@dp.message_handler(content_types=['document'], chat_type=['group', 'supergroup'])
async def handle_docs(message: types.Message):
    file_id = message.document.file_id
    title = message.document.file_name
    cur.execute("INSERT INTO books (file_id, title) VALUES (?, ?)", (file_id, title))
    conn.commit()
    await message.reply(f"✅ {title} darslik bazaga qo‘shildi!")

# 📌 /start komandasi (shaxsiy chat)
@dp.message_handler(commands=['start'], chat_type='private')
async def send_welcome(message: types.Message):
    await message.reply(
        "Salom! Men darsliklar botiman 📚\n\n"
        "Komandalar:\n"
        "👉 /list — darsliklar ro‘yxati\n"
        "👉 /get [raqam] — darslikni olish"
    )

# 📌 /list komandasi (shaxsiy chat)
@dp.message_handler(commands=['list'], chat_type='private')
async def send_list(message: types.Message):
    cur.execute("SELECT id, title FROM books")
    rows = cur.fetchall()
    if not rows:
        await message.reply("📚 Hozircha darslik yo‘q")
        return
    text = "📖 Darsliklar ro‘yxati:\n\n"
    for row in rows:
        text += f"{row[0]}. {row[1]}\n"
    text += "\n📌 Faylni olish uchun: /get [raqam]"
    await message.reply(text)

# 📌 /get komandasi (shaxsiy chat)
@dp.message_handler(commands=['get'], chat_type='private')
async def send_book(message: types.Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply("❗ /get [raqam] shaklida yozing")
        return
    book_id = int(args[1])
    cur.execute("SELECT file_id, title FROM books WHERE id=?", (book_id,))
    row = cur.fetchone()
    if row:
        await message.reply_document(row[0], caption=row[1])
    else:
        await message.reply("❌ Bunday darslik topilmadi")

# 🚀 Ishga tushirish
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
