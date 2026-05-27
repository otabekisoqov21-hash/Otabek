# Otabek
Men eng yaxshi oʻyinlar yaratmoqchiman 
# ONLY COIN BOT
# PYTHON + AIOGRAM 3.X
# main.py

import asyncio
import logging
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

TOKEN = "BOT_TOKENINGIZ"

# =========================
# DATABASE
# =========================

db = sqlite3.connect("onlycoin.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    energy INTEGER DEFAULT 100,
    boost INTEGER DEFAULT 1,
    spins INTEGER DEFAULT 1,
    referrals INTEGER DEFAULT 0
)
""")

db.commit()

# =========================
# BOT
# =========================

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# =========================
# FUNCTIONS
# =========================

def get_user(user_id):
    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )
    return cursor.fetchone()


def add_user(user_id):
    if not get_user(user_id):
        cursor.execute(
            "INSERT INTO users(user_id) VALUES(?)",
            (user_id,)
        )
        db.commit()


def add_coin(user_id, amount):
    cursor.execute(
        "UPDATE users SET coins = coins + ? WHERE user_id=?",
        (amount, user_id)
    )
    db.commit()


def remove_energy(user_id):
    cursor.execute(
        "UPDATE users SET energy = energy - 1 WHERE user_id=?",
        (user_id,)
    )
    db.commit()


def get_data(user_id):
    cursor.execute(
        "SELECT coins, energy, boost, spins FROM users WHERE user_id=?",
        (user_id,)
    )
    return cursor.fetchone()


# =========================
# KEYBOARDS
# =========================

def main_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🦁 ONLY COIN",
                    callback_data="tap"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚡ BOOST",
                    callback_data="boost"
                ),
                InlineKeyboardButton(
                    text="🎰 BARABAN",
                    callback_data="wheel"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 REFERRAL",
                    callback_data="ref"
                ),
                InlineKeyboardButton(
                    text="💰 WALLET",
                    callback_data="wallet"
                )
            ],
        ]
    )

    return keyboard


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    user_id = message.from_user.id
    add_user(user_id)

    ref_id = message.text.replace("/start ", "")

    if ref_id.isdigit():
        ref_id = int(ref_id)

        if ref_id != user_id:
            cursor.execute(
                "UPDATE users SET referrals = referrals + 1, spins = spins + 2 WHERE user_id=?",
                (ref_id,)
            )

            db.commit()

    coins, energy, boost, spins = get_data(user_id)

    text = f"""
<b>🦁 ONLY COIN BOT</b>

💰 Coin: <b>{coins}</b>
⚡ Energy: <b>{energy}</b>
🚀 Boost: <b>x{boost}</b>
🎰 Spins: <b>{spins}</b>

Tangani bosib ONLY COIN yig'ing.
"""

    await message.answer(
        text,
        reply_markup=main_menu()
    )


# =========================
# TAP
# =========================

@dp.callback_query(F.data == "tap")
async def tap_coin(callback: CallbackQuery):

    user_id = callback.from_user.id

    coins, energy, boost, spins = get_data(user_id)

    if energy <= 0:
        await callback.answer(
            "⚠️ Energy tugagan!",
            show_alert=True
        )
        return

    earned = boost

    add_coin(user_id, earned)
    remove_energy(user_id)

    coins, energy, boost, spins = get_data(user_id)

    text = f"""
🦁 <b>ONLY COIN</b>

💰 Coin: <b>{coins}</b>
⚡ Energy: <b>{energy}</b>
🚀 Boost: <b>x{boost}</b>

+{earned} ONLY COIN
"""

    await callback.message.edit_text(
        text,
        reply_markup=main_menu()
    )

    await callback.answer()


# =========================
# BOOST
# =========================

@dp.callback_query(F.data == "boost")
async def boost_menu(callback: CallbackQuery):

    text = """
🚀 <b>BOOST SHOP</b>

1$ = x2
2$ = x4
3$ = x6
4$ = x8
5$ = x10

💳 To'lov karta:
<code>4231 2000 8098 2977</code>

Admin tasdiqlaydi.
"""

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 ORQAGA",
                        callback_data="back"
                    )
                ]
            ]
        )
    )


# =========================
# WHEEL
# =========================

@dp.callback_query(F.data == "wheel")
async def wheel(callback: CallbackQuery):

    import random

    rewards = [
        0.20,
        0.30,
        0.40,
        1,
        2,
        3,
        4,
        5,
        10,
        20
    ]

    user_id = callback.from_user.id

    coins, energy, boost, spins = get_data(user_id)

    if spins <= 0:
        await callback.answer(
            "❌ Spin yo'q",
            show_alert=True
        )
        return

    reward = random.choice(rewards)

    cursor.execute(
        "UPDATE users SET spins = spins - 1 WHERE user_id=?",
        (user_id,)
    )

    db.commit()

    text = f"""
🎰 <b>BARABAN</b>

Siz yutdingiz:

💵 <b>{reward}$</b>

🎁 Pul walletga qo'shildi.
"""

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 MENU",
                        callback_data="back"
                    )
                ]
            ]
        )
    )

    await callback.answer()


# =========================
# REFERRAL
# =========================

@dp.callback_query(F.data == "ref")
async def referral(callback: CallbackQuery):

    user_id = callback.from_user.id

    link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"

    text = f"""
👥 <b>REFERRAL</b>

Do'st taklif qiling.

Har do'st uchun:
🎰 +2 spin

Sizning linkingiz:

{link}
"""

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 MENU",
                        callback_data="back"
                    )
                ]
            ]
        )
    )


# =========================
# WALLET
# =========================

@dp.callback_query(F.data == "wallet")
async def wallet(callback: CallbackQuery):

    user_id = callback.from_user.id

    coins, energy, boost, spins = get_data(user_id)

    usd = coins * 0.1

    text = f"""
💰 <b>WALLET</b>

🪙 Coin: <b>{coins}</b>
💵 Dollar: <b>{usd}$</b>

Minimum chiqarish:
1000 ONLY COIN

Kartalar:
✅ HUMO
✅ UZCARD
✅ VISA
"""

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 MENU",
                        callback_data="back"
                    )
                ]
            ]
        )
    )


# =========================
# BACK
# =========================

@dp.callback_query(F.data == "back")
async def back_menu(callback: CallbackQuery):

    user_id = callback.from_user.id

    coins, energy, boost, spins = get_data(user_id)

    text = f"""
🦁 <b>ONLY COIN BOT</b>

💰 Coin: <b>{coins}</b>
⚡ Energy: <b>{energy}</b>
🚀 Boost: <b>x{boost}</b>
🎰 Spins: <b>{spins}</b>
"""

    await callback.message.edit_text(
        text,
        reply_markup=main_menu()
    )


# =========================
# RUN
# =========================

async def main():
    logging.basicConfig(level=logging.INFO)

    print("BOT ISHGA TUSHDI ✅")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
