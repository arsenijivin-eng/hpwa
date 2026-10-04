import asyncio
import os
import random
import sqlite3
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 7894051808
CHANNEL = "@hoqanft"
VPN_URL = "https://t.me/CristyVPN_bot?start=7894051808"
APPLY_URL = "https://t.me/+IxVXx6qkPEpjZTYy"
DB = "hoqabot.db"

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Put your new bot token into the BOT_TOKEN environment variable.")

bot = Bot(TOKEN)
dp = Dispatcher()


def db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_seen TEXT, last_seen TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS actions (user_id INTEGER, action TEXT, ts TEXT)")
    con.commit()
    return con


def touch_user(user):
    con = db()
    now = datetime.now(timezone.utc).isoformat()
    con.execute("INSERT INTO users(user_id,username,first_seen,last_seen) VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,last_seen=excluded.last_seen", (user.id, user.username or "", now, now))
    con.commit(); con.close()


def action(user_id, name):
    con = db(); con.execute("INSERT INTO actions VALUES(?,?,?)", (user_id, name, datetime.now(timezone.utc).isoformat())); con.commit(); con.close()


def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Удар по воротам", callback_data="game:football"), InlineKeyboardButton(text="🏀 Бросок в кольцо", callback_data="game:basketball")],
    ])


def reward_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Посмотреть NFT", callback_data="nft:view"), InlineKeyboardButton(text="🔄 Перекрутить", callback_data="nft:spin")],
    ])


def tasks_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1️⃣ Задание", url="https://t.me/hoqanft")],
        [InlineKeyboardButton(text="2️⃣ Лучший VPN", url=VPN_URL)],
        [InlineKeyboardButton(text="3️⃣ Подать заявку", url=APPLY_URL)],
        [InlineKeyboardButton(text="✅ Проверить", callback_data="tasks:check")],
    ])


@dp.message(CommandStart())
async def start(message: Message):
    touch_user(message.from_user)
    # Put your Hoqa start image at images/start.jpg
    try:
        from aiogram.types import FSInputFile
        await message.answer_photo(FSInputFile("images/start.jpg"), caption="Испытайте удачу!\n\nВыберите, ударить по воротам или бросить мяч в кольцо, чтобы получить приз ⚽🏀", reply_markup=main_kb())
    except Exception:
        await message.answer("Испытайте удачу!\n\nВыберите действие:", reply_markup=main_kb())


@dp.callback_query(F.data.startswith("game:"))
async def game(call: CallbackQuery):
    touch_user(call.from_user)
    sport = call.data.split(":",1)[1]
    won = random.random() < 0.5
    action(call.from_user.id, f"game_{sport}_{'win' if won else 'lose'}")
    label = "Удар по воротам" if sport == "football" else "Бросок в кольцо"
    if won:
        caption = f"Вы попали! 🎉\n\n{label}\n\nВыберите приз:"
        img = "images/hit.jpg"
    else:
        caption = f"Вы промахнулись 😔\n\n{label}\n\nНо мы всё равно можем выдать вам приз за простое задание!"
        img = "images/miss.jpg"
    try:
        from aiogram.types import FSInputFile
        await call.message.answer_photo(FSInputFile(img), caption=caption, reply_markup=reward_kb())
    except Exception:
        await call.message.answer(caption, reply_markup=reward_kb())
    await call.answer()


@dp.callback_query(F.data == "nft:view")
async def nft_view(call: CallbackQuery):
    touch_user(call.from_user); action(call.from_user.id, "nft_view")
    # Replace these with your actual NFT IDs/links.
    nft_id = random.randint(1500, 2500)
    await call.message.answer(f"🎁 Вам выпал NFT\n\nОценка: примерно {nft_id} ₽\n\nЧтобы забрать приз, выполните задания.", reply_markup=tasks_kb())
    await call.answer()


@dp.callback_query(F.data == "nft:spin")
async def nft_spin(call: CallbackQuery):
    touch_user(call.from_user); action(call.from_user.id, "nft_spin")
    value = random.randint(2000, 4000)
    await call.message.answer(f"🔄 Перекрутка\n\nВыпал NFT примерно на {value} ₽.\n\nЧтобы забрать приз, выполните задания.", reply_markup=tasks_kb())
    await call.answer()


@dp.callback_query(F.data == "tasks:check")
async def tasks_check(call: CallbackQuery):
    touch_user(call.from_user)
    # Telegram can verify channel membership, but the bot must be an admin/member with permission to inspect members.
    subscribed = False
    try:
        member = await bot.get_chat_member(CHANNEL, call.from_user.id)
        subscribed = member.status in {"member", "administrator", "creator"}
    except Exception:
        pass
    if not subscribed:
        await call.answer("Сначала подпишитесь на @hoqanft", show_alert=True)
        return
    action(call.from_user.id, "tasks_verified")
    await call.message.answer("✅ Задания выполнены.\n\nОжидайте выдачи NFT.")
    await call.answer()


@dp.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    con = db()
    total = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    today = datetime.now(timezone.utc).date().isoformat()
    today_count = con.execute("SELECT COUNT(*) FROM users WHERE substr(first_seen,1,10)=?", (today,)).fetchone()[0]
    con.close()
    await message.answer(f"🛠 Админка\n\nПользователей всего: {total}\nНовых сегодня: {today_count}\n\nДля рассылки: /broadcast текст")


@dp.message(Command("broadcast"))
async def broadcast(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.partition(" ")[2].strip()
    if not text:
        await message.answer("Использование: /broadcast текст")
        return
    con = db(); ids = [r[0] for r in con.execute("SELECT user_id FROM users")]; con.close()
    sent = 0
    for uid in ids:
        try:
            await bot.send_message(uid, text)
            sent += 1
            await asyncio.sleep(0.04)
        except Exception:
            pass
    await message.answer(f"Рассылка завершена: {sent}/{len(ids)}")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
