"""
Telegram To'lov Bot (UZS - So'm)
Kerakli kutubxonalar: pip install python-telegram-bot==20.7
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# ===================== SOZLAMALAR =====================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # @BotFather dan olingan token
ADMIN_ID = 123456789               # Sizning Telegram ID'ingiz

# To'lov rekvizitlari
CARD_NUMBER = "8600 1234 5678 9012"
CARD_OWNER = "Abdullayev Abdulla"

# Miqdorlar (so'mda)
PAYMENT_AMOUNTS = [10000, 25000, 50000, 100000]

# ConversationHandler holatlari
CHOOSE_AMOUNT, ENTER_CUSTOM, CONFIRM_PAYMENT = range(3)

# ===================== LOGGING =====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== YORDAMCHI FUNKSIYALAR =====================

def format_uzs(amount: int) -> str:
    """Summani UZS formatida chiqaradi: 50,000 so'm"""
    return f"{amount:,} so'm".replace(",", " ")


# ===================== BOT HANDLERLARI =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    user = update.effective_user
    text = (
        f"👋 Salom, {user.first_name}!\n\n"
        f"💳 Bu bot orqali to'lov amalga oshirishingiz mumkin.\n\n"
        f"Quyidagi tugmadan to'lov miqdorini tanlang:"
    )
    keyboard = [
        [InlineKeyboardButton(f"💰 {format_uzs(amt)}", callback_data=f"amount_{amt}")]
        for amt in PAYMENT_AMOUNTS
    ]
    keyboard.append([InlineKeyboardButton("✏️ Boshqa miqdor kiritish", callback_data="amount_custom")])

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_AMOUNT


async def choose_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Miqdor tanlash"""
    query = update.callback_query
    await query.answer()

    if query.data == "amount_custom":
        await query.edit_message_text(
            "✏️ To'lov miqdorini kiriting (faqat raqam, so'mda):\n\n"
            "Misol: 75000"
        )
        return ENTER_CUSTOM

    amount = int(query.data.split("_")[1])
    context.user_data["amount"] = amount
    return await show_payment_details(query, context)


async def enter_custom_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi miqdorni qo'lda kiritadi"""
    text = update.message.text.strip().replace(" ", "").replace(",", "")

    if not text.isdigit():
        await update.message.reply_text("❌ Iltimos, faqat raqam kiriting!\n\nMisol: 75000")
        return ENTER_CUSTOM

    amount = int(text)
    if amount < 1000:
        await update.message.reply_text("❌ Minimal to'lov miqdori: 1 000 so'm")
        return ENTER_CUSTOM

    context.user_data["amount"] = amount

    keyboard = [[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_amount"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"),
    ]]
    await update.message.reply_text(
        f"💰 Tanlangan miqdor: *{format_uzs(amount)}*\n\nDavom etamizmi?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONFIRM_PAYMENT


async def confirm_amount_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Miqdorni tasdiqlash"""
    query = update.callback_query
    await query.answer()
    return await show_payment_details(query, context)


async def show_payment_details(query, context: ContextTypes.DEFAULT_TYPE):
    """To'lov rekvizitlarini ko'rsatish"""
    amount = context.user_data.get("amount", 0)
    user = query.from_user

    text = (
        f"💳 *TO'LOV MA'LUMOTLARI*\n"
        f"{'─' * 30}\n"
        f"👤 Karta egasi: `{CARD_OWNER}`\n"
        f"💳 Karta raqami: `{CARD_NUMBER}`\n"
        f"💰 To'lov miqdori: *{format_uzs(amount)}*\n"
        f"{'─' * 30}\n\n"
        f"📌 *Ko'rsatma:*\n"
        f"1️⃣ Yuqoridagi karta raqamiga pul o'tkazing\n"
        f"2️⃣ To'lovni amalga oshirgach, chekni shu yerga yuboring\n\n"
        f"⚠️ Izoh sifatida *Telegram ID*'ingizni yozing: `{user.id}`"
    )

    keyboard = [[
        InlineKeyboardButton("📸 Chek yubordim", callback_data="receipt_sent"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"),
    ]]

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM_PAYMENT


async def receipt_sent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi chek yubordi deb bildirdi"""
    query = update.callback_query
    await query.answer()
    amount = context.user_data.get("amount", 0)

    await query.edit_message_text(
        f"✅ Rahmat! Chekingiz ko'rib chiqilmoqda.\n\n"
        f"💰 Miqdor: *{format_uzs(amount)}*\n\n"
        f"⏳ Adminimiz 5-30 daqiqa ichida to'lovingizni tasdiqlaydi.",
        parse_mode="Markdown"
    )

    # Adminga xabar yuborish
    user = query.from_user
    admin_text = (
        f"🔔 *YANGI TO'LOV SO'ROVI*\n"
        f"{'─' * 30}\n"
        f"👤 Foydalanuvchi: {user.full_name}\n"
        f"🆔 Telegram ID: `{user.id}`\n"
        f"🔗 Username: @{user.username or 'yo\'q'}\n"
        f"💰 Miqdor: *{format_uzs(amount)}*\n"
        f"{'─' * 30}\n"
        f"Chekni yuborishini kuting..."
    )

    keyboard = [[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"admin_approve_{user.id}_{amount}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"admin_reject_{user.id}"),
    ]]

    await context.bot.send_message(
        ADMIN_ID,
        admin_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return ConversationHandler.END


async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi chek rasmini yuborsa adminga yo'naltirish"""
    user = update.effective_user
    amount = context.user_data.get("amount", 0)

    caption = (
        f"📸 *CHEK RASMI*\n"
        f"👤 {user.full_name} | ID: `{user.id}`\n"
        f"💰 Miqdor: *{format_uzs(amount)}*"
    )

    keyboard = [[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"admin_approve_{user.id}_{amount}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"admin_reject_{user.id}"),
    ]]

    await context.bot.send_photo(
        ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(
        "✅ Chekingiz adminga yuborildi! Tez orada javob olasiz."
    )


# ===================== ADMIN HANDLERLARI =====================

async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin to'lovni tasdiqlaydi yoki rad etadi"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return

    data = query.data
    if data.startswith("admin_approve_"):
        parts = data.split("_")
        user_id = int(parts[2])
        amount = int(parts[3])

        await context.bot.send_message(
            user_id,
            f"✅ *To'lovingiz tasdiqlandi!*\n\n"
            f"💰 Miqdor: *{format_uzs(amount)}*\n\n"
            f"Rahmat! 🎉",
            parse_mode="Markdown"
        )
        await query.edit_message_text(
            query.message.text + f"\n\n✅ *TASDIQLANDI* ({format_uzs(amount)})",
            parse_mode="Markdown"
        )

    elif data.startswith("admin_reject_"):
        user_id = int(data.split("_")[2])

        await context.bot.send_message(
            user_id,
            "❌ *To'lovingiz tasdiqlanmadi.*\n\n"
            "Sabab: Noto'g'ri chek yoki miqdor.\n"
            "Qayta urinish uchun /start bosing.",
            parse_mode="Markdown"
        )
        await query.edit_message_text(
            query.message.text + "\n\n❌ *RAD ETILDI*",
            parse_mode="Markdown"
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bekor qilish"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ To'lov bekor qilindi. Qayta boshlash: /start")
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Yordam*\n\n"
        "/start — To'lov boshlash\n"
        "/help — Yordam\n\n"
        "Muammo bo'lsa admin bilan bog'laning.",
        parse_mode="Markdown"
    )


# ===================== MAIN =====================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_AMOUNT: [
                CallbackQueryHandler(choose_amount, pattern="^amount_"),
                CallbackQueryHandler(cancel, pattern="^cancel$"),
            ],
            ENTER_CUSTOM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_custom_amount),
            ],
            CONFIRM_PAYMENT: [
                CallbackQueryHandler(confirm_amount_callback, pattern="^confirm_amount$"),
                CallbackQueryHandler(receipt_sent, pattern="^receipt_sent$"),
                CallbackQueryHandler(cancel, pattern="^cancel$"),
                MessageHandler(filters.PHOTO, handle_receipt_photo),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(admin_action, pattern="^admin_(approve|reject)_"))

    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
