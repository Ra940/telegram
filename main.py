import logging import os from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile from telegram.ext import ( Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters ) from flask import Flask from threading import Thread
--- Константы и настройки ---
TOKEN = os.getenv("BOT_TOKEN") OWNER_ID = 7397365971 PDF_FILE_PATH = "book.pdf" logging.basicConfig(level=logging.INFO)
--- Flask ---
flask_app = Flask(name)
@flask_app.route("/") def index(): return "Бот жив! ✅"
def run_flask(): flask_app.run(host="0.0.0.0", port=8080)
--- Сохранение ID пользователей ---
def save_user_id(user_id): try: with open("users.txt", "r+") as f: ids = set(f.read().splitlines()) if str(user_id) not in ids: f.write(str(user_id) + "\n") except FileNotFoundError: with open("users.txt", "w") as f: f.write(str(user_id) + "\n")
--- Главное меню ---
def main_menu(is_admin=False): buttons = [ [InlineKeyboardButton("\ud83d\udcd8 \u041e \u043a\u043d\u0438\u0433\u0435", callback_data="about")], [InlineKeyboardButton("\ud83e\udd16 \u0410\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0442\u043e\u0440\u0433\u043e\u0432\u043b\u044f", callback_data="robot")], [InlineKeyboardButton("\ud83d\udcb0 \u041a\u0443\u043f\u0438\u0442\u044c \u0437\u0430 799\u20bd", callback_data="buy")], [InlineKeyboardButton("\ud83e\uddfe \u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u0447\u0435\u043a", callback_data="receipt")], [InlineKeyboardButton("\ud83c\udd95 \u041d\u043e\u0432\u043e\u0435", callback_data="new")] ] if is_admin: buttons.append([InlineKeyboardButton("\ud83d\udcdd \u041f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u044f \u043f\u043e\u0441\u0442\u0430", callback_data="admin_post")]) return InlineKeyboardMarkup(buttons)
--- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = update.effective_user.id save_user_id(user_id) context.user_data["is_admin"] = user_id == OWNER_ID await update.message.reply_text( "Привет! \ud83d\udc4b\n\nТы можешь купить книгу или доступ к роботу.", reply_markup=main_menu(context.user_data["is_admin"]) )
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.effective_user.id != OWNER_ID: await update.message.reply_text("⛔️ У вас нет доступа.") return try: with open("users.txt", "r") as f: ids = set(f.read().splitlines()) await update.message.reply_text(f"📈 Пользователей всего: {len(ids)}") except FileNotFoundError: await update.message.reply_text("📂 Список пользователей пока пуст.")
--- Обработка кнопок ---
(сюда вставим button_handler без изменений из твоего кода)
--- Обработка сообщений ---
(сюда вставим handle_receipt без изменений)
--- Основной запуск ---
def main(): app = Application.builder().token(TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(CommandHandler("stats", stats)) app.add_handler(CallbackQueryHandler(button_handler)) app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.Document.ALL, handle_receipt))
print("✅ Бот запущен!") app.run_polling() 
if name == "main": Thread(target=run_flask).start() main()
