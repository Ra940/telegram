import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from flask import Flask
from threading import Thread

# --- Константы и настройки ---
TOKEN = "7503402744:AAF7MWB0x_6Eh7AwE3GLdmGLuxkpottqt4s"
OWNER_ID = 7397365971
PDF_FILE_PATH = "book.pdf"

print(f"BOT_TOKEN: {TOKEN}")
logging.basicConfig(level=logging.INFO)

# --- Flask ---
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "Бот жив! ✅"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

# --- Сохранение ID пользователей ---
def save_user_id(user_id):
    try:
        with open("users.txt", "r+") as f:
            ids = set(f.read().splitlines())
            if str(user_id) not in ids:
                f.write(str(user_id) + "\n")
    except FileNotFoundError:
        with open("users.txt", "w") as f:
            f.write(str(user_id) + "\n")

# --- Главное меню ---
def main_menu(is_admin=False):
    buttons = [
        [InlineKeyboardButton("📘 О книге", callback_data="about")],
        [InlineKeyboardButton("🤖 Автоматическая торговля", callback_data="robot")],
        [InlineKeyboardButton("💰 Купить за 799₽", callback_data="buy")],
        [InlineKeyboardButton("🧾 Отправить чек", callback_data="receipt")],
        [InlineKeyboardButton("🆕 Новое", callback_data="new")]
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton("📝 Публикация поста", callback_data="admin_post")])
    return InlineKeyboardMarkup(buttons)

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📥 Получена команда /start")
    user_id = update.effective_user.id
    save_user_id(user_id)
    context.user_data["is_admin"] = user_id == OWNER_ID
    await update.message.reply_text(
        "Привет! 👋\n\nТы можешь купить книгу или доступ к роботу.",
        reply_markup=main_menu(context.user_data["is_admin"])
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔️ У вас нет доступа.")
        return
    try:
        with open("users.txt", "r") as f:
            ids = set(f.read().splitlines())
        await update.message.reply_text(f"📈 Пользователей всего: {len(ids)}")
    except FileNotFoundError:
        await update.message.reply_text("📂 Список пользователей пока пуст.")

# --- Обработка кнопок ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "about":
        await query.edit_message_text("📘 Это книга по трейдингу. Полезная и практичная.")
    elif data == "robot":
        await query.edit_message_text("🤖 Наш торговый робот работает 24/7 и показывает отличные результаты.")
    elif data == "buy":
        await query.edit_message_text("💳 Переведите 799₽ на карту Ravshan Kayumov, затем нажмите «🧾 Отправить чек».")
    elif data == "receipt":
        await query.edit_message_text("📩 Отправьте сюда фото или скриншот чека.")
    elif data == "new":
        await query.edit_message_text("🆕 Следите за новостями, скоро обновления!")
    elif data == "admin_post" and update.effective_user.id == OWNER_ID:
        context.user_data["awaiting_post"] = True
        await query.edit_message_text("📝 Отправьте текст публикации, и я разошлю его всем пользователям.")
    else:
        await query.edit_message_text("❗ Неизвестная команда.")

# --- Обработка сообщений ---
async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.user_data.get("awaiting_post") and user_id == OWNER_ID:
        context.user_data["awaiting_post"] = False
        try:
            with open("users.txt", "r") as f:
                ids = set(f.read().splitlines())
            for uid in ids:
                try:
                    await context.bot.send_message(chat_id=int(uid), text=update.message.text)
                except Exception as e:
                    logging.warning(f"Не удалось отправить сообщение {uid}: {e}")
            await update.message.reply_text("✅ Пост разослан.")
        except FileNotFoundError:
            await update.message.reply_text("❌ Нет пользователей.")
        return

    await update.message.reply_text("✅ Чек получен. Ожидайте подтверждения.")

# --- Запуск бота (исправленный способ) ---
async def run_bot():
    print("🚀 Бот запускается...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.Document.ALL, handle_receipt))

    print("✅ Бот запущен!")
    await app.run_polling()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(run_bot())
