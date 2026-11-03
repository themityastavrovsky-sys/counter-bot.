import os, re, asyncio, aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

bot = Bot(os.environ["TELEGRAM_TOKEN"])
dp = Dispatcher()
DB = os.environ.get("DB_PATH", "count.db")

async def init():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS totals(
            chat_id INTEGER PRIMARY KEY, total INTEGER DEFAULT 0)""")
        await db.commit()

async def change(chat_id, delta):
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT OR IGNORE INTO totals(chat_id) VALUES(?)", (chat_id,))
        await db.execute("UPDATE totals SET total = total + ? WHERE chat_id=?",
                         (delta, chat_id))
        cur = await db.execute("SELECT total FROM totals WHERE chat_id=?", (chat_id,))
        total = (await cur.fetchone())[0]
        await db.commit()
    return total

@dp.message(F.text.regexp(r"^\s*[+-]\s*\d+\s*$"))
async def count(m: types.Message):
    delta = int(m.text.replace(" ", ""))
    await m.reply(str(await change(m.chat.id, delta)))

@dp.message(Command("reset"))
async def reset(m: types.Message):
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM totals WHERE chat_id=?", (m.chat.id,))
        await db.commit()
    await m.reply("Счёт обнулён: 0")

@dp.message(Command("total"))
async def total(m: types.Message):
    await m.reply(str(await change(m.chat.id, 0)))

async def main():
    await init()
    await dp.start_polling(bot)

asyncio.run(main())
