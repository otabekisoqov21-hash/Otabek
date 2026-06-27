import telebot
import json
import os
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

# ------------------ DATA HANDLING ------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user(data, user_id):
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {"coins": 0}
    return data[user_id]

# ------------------ COMMANDS ------------------

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "💰 Welcome!\n\n"
        "/daily - 100 coin olish\n"
        "/balance - balansni ko‘rish"
    )

@bot.message_handler(commands=['balance'])
def balance(message):
    data = load_data()
    user = get_user(data, message.from_user.id)
    save_data(data)

    bot.send_message(message.chat.id, f"💰 Sizning coins: {user['coins']}")

@bot.message_handler(commands=['daily'])
def daily(message):
    data = load_data()
    user = get_user(data, message.from_user.id)

    user['coins'] += 100
    save_data(data)

    bot.send_message(message.chat.id, "🎁 Siz 100 coin oldingiz!")

# ------------------ EARN COINS BY TEXT ------------------

@bot.message_handler(func=lambda message: True)
def chat_reward(message):
    data = load_data()
    user = get_user(data, message.from_user.id)

    user['coins'] += 1   # har xabarga 1 coin
    save_data(data)

    bot.send_message(message.chat.id, f"+1 coin ✅ (Jami: {user['coins']})")

print("Coin bot ishlayapti...")
bot.infinity_polling()
