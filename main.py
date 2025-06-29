import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

from flask import Flask
from threading import Thread


TOKEN = "7503402744:AAF7MWB0x_6Eh7AwE3GLdmGLuxkpottqt4s"
OWNER_ID = 7397365971
PDF_FILE_PATH = "book.pdf"

logging.basicConfig(level=logging.INFO)

# 📥 Сохраняем ID пользователей
def save_user_id(user_id):
    try:
        with open("users.txt", "r+") as f:
            ids = set(f.read().splitlines())
            if str(user_id) not in ids:
                f.write(str(user_id) + "\n")
    except FileNotFoundError:
        with open("users.txt", "w") as f:
            f.write(str(user_id) + "\n")

# 📋 Главное меню
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

# ▶️ Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user_id(user_id)
    context.user_data["is_admin"] = user_id == OWNER_ID
    await update.message.reply_text(
        "Привет! 👋\n\nТы можешь купить книгу или доступ к роботу.",
        reply_markup=main_menu(context.user_data["is_admin"])
    )

# 🎛 Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "about":
        await query.edit_message_text(
            "📘 *О книге*\n\n"
            "✅ Бесплатно — читай онлайн без оплаты и регистрации\n"
            "✅ Поддержка — покупая PDF, ты поддерживаешь авторов\n"
            "✅ Удобство — PDF работает без интернета\n"
            "✅ Качество — чистый файл, без рекламы\n\n"
            "[Подробнее на сайте](https://treyding.org/premium)",
            parse_mode="Markdown", disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back")]])
        )
    elif data == "robot":
        await query.edit_message_text(
            "🤖 *О автоматической торговле*\n\n"
            "📌 Торговый робот с шаблоном установки\n"
            "🔁 Возврат 50% если за неделю теста будет слив\n"
            "📚 Все стратегии — в одной книге\n\n"
            "💱 Работает на рынке Forex\n"
            "💸 Минимальный депозит — 400 $\n"
            "🎯 Цель: +30 $ прибыли в день\n"
            "⚙️ Работа 24/7 без участия\n"
            "🧠 Фокус на стабильность, а не риск\n\n"
            "Робот уже работает без сбоев — наблюдай, как растёт твой капитал.\n\n"
            "[Подробнее](https://treyding.org/robot)",
            parse_mode="Markdown", disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Купить доступ", callback_data="buy_robot")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
            ])
        )
    elif data == "buy":
        context.user_data["last_button"] = "buy"
        await query.edit_message_text(
            "💳 Оплата 799₽ на карту 5536 9140 2072 3742 (Ravshan Kayumov).\nПосле оплаты нажми 🧾 Отправить чек.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back")]])
        )
    elif data == "buy_robot":
        context.user_data["last_button"] = "buy_robot"
        await query.edit_message_text(
            "💳 Оплата 6000₽ на карту 5536 9140 2072 3742 (Ravshan Kayumov).\nПосле оплаты нажми 🧾 Отправить чек.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back")]])
        )
    elif data == "receipt":
        await query.edit_message_text(
            "📤 Отправьте чек (фото, текст или документ). После проверки вы получите доступ.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back")]])
        )
    elif data == "new":
        await query.edit_message_text("🆕 Новое обновление скоро!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]))
    elif data == "back":
        await query.edit_message_text("🔙 Главное меню:", reply_markup=main_menu(context.user_data.get("is_admin", False)))
    elif data == "admin_post":
        if query.from_user.id != OWNER_ID:
            await query.edit_message_text("❌ Только админ может публиковать посты.")
        else:
            context.user_data["awaiting_post"] = True
            await query.edit_message_text("✏️ Введите текст или файл. Затем подтвердите рассылку.")
    elif data == "confirm_post":
        post = context.user_data.get("post_data")
        if not post:
            await query.edit_message_text("❌ Нет данных для рассылки.")
            return
        count = 0
        with open("users.txt", "r") as f:
            ids = list(set(f.read().splitlines()))
        for uid in ids:
            try:
                uid_int = int(uid)
                if post["photo"]:
                    await context.bot.send_photo(chat_id=uid_int, photo=post["photo"], caption=post.get("caption", ""))
                elif post["document"]:
                    await context.bot.send_document(chat_id=uid_int, document=post["document"], caption=post.get("caption", ""))
                elif post["text"]:
                    await context.bot.send_message(chat_id=uid_int, text=post["text"])
                count += 1
            except Exception as e:
                logging.warning(f"Ошибка при отправке {uid}: {e}")
        context.user_data["post_data"] = None
        await query.edit_message_text(f"✅ Пост отправлен {count} пользователям.")
    elif data == "cancel_post":
        context.user_data["post_data"] = None
        await query.edit_message_text("❌ Рассылка отменена.")
    elif data.startswith("approve_"):
        parts = data.split("_")
        user_id, kind = int(parts[1]), parts[2]
        if kind == "book":
            with open(PDF_FILE_PATH, "rb") as f:
                await context.bot.send_document(chat_id=user_id, document=InputFile(f, filename="Анализ_рынка.pdf"))
            await query.edit_message_text("✅ Книга отправлена.")
        elif kind == "robot":
            await context.bot.send_message(chat_id=user_id, text="✅ Оплата подтверждена! Ссылка: https://treyding.org/vip12\n🎁 Книга в подарок.")
            await query.edit_message_text("✅ Ссылка отправлена.")

# 📤 Обработка сообщений (чеков или постов)
async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    save_user_id(user_id)

    if context.user_data.get("awaiting_post"):
        context.user_data["awaiting_post"] = False
        context.user_data["post_data"] = {
            "text": update.message.text,
            "photo": update.message.photo[-1].file_id if update.message.photo else None,
            "document": update.message.document.file_id if update.message.document else None,
            "caption": update.message.caption
        }
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_post")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel_post")]
        ])
        if update.message.photo:
            await update.message.reply_photo(photo=update.message.photo[-1].file_id, caption=update.message.caption or "", reply_markup=buttons)
        elif update.message.document:
            await update.message.reply_document(document=update.message.document.file_id, caption=update.message.caption or "", reply_markup=buttons)
        elif update.message.text:
            await update.message.reply_text(update.message.text, reply_markup=buttons)
        return

    kind = "robot" if context.user_data.get("last_button") == "buy_robot" else "book"
    caption = f"📩 Чек от @{user.username or 'без username'} (ID: {user_id})"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve_{user_id}_{kind}")]
    ])
    await update.message.reply_text("✅ Чек получен, ожидайте подтверждения.")
    if update.message.text:
        await context.bot.send_message(OWNER_ID, caption + ":\n\n" + update.message.text, reply_markup=reply_markup)
    elif update.message.photo:
        await context.bot.send_photo(OWNER_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=reply_markup)
    elif update.message.document:
        await context.bot.send_document(OWNER_ID, document=update.message.document.file_id, caption=caption, reply_markup=reply_markup)

# 📊 Команда /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔️ У вас нет доступа.")
        return
    try:
        with open("users.txt", "r") as f:
            ids = set(f.read().splitlines())
            await update.message.reply_text(f"📈 Пользователей всего: {len(ids)}")
    except FileNotFoundError:
        await update.message.reply_text("📂 Список пользователей пока пуст.")

# 🌐 Flask сервер для Replit
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Бот жив! ✅"

def run():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run)
    thread.start()

# 🚀 Запуск
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.Document.ALL, handle_receipt))
    print("Бот запущен ✅")
    app.run_polling()

if __name__ == "__main__":
    keep_alive()
    main()
