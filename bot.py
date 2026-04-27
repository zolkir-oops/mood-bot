import os
from datetime import datetime
from telegram import Update, MenuButtonWebApp, WebAppInfo
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters,
)
import db

TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_URL = os.environ["WEBAPP_URL"]


def contains_emoji(text: str) -> bool:
    if not text:
        return False
    cp = ord(text[0])
    return (
        0x1F000 <= cp <= 0x1FFFF
        or 0x2600 <= cp <= 0x27BF
        or 0x2300 <= cp <= 0x23FF
        or cp in (0x2764, 0x2665, 0x2666, 0x2663, 0x2660)
    )


def extract_emoji(text: str):
    i = 0
    while i < len(text):
        cp = ord(text[i])
        is_e = (
            0x1F000 <= cp <= 0x1FFFF or 0x2600 <= cp <= 0x27BF
            or 0x2300 <= cp <= 0x23FF
            or cp in (0x2764, 0x2665, 0x2666, 0x2663, 0x2660)
            or cp in (0xFE0F, 0x200D) or 0x1F3FB <= cp <= 0x1F3FF
        )
        if is_e:
            i += 1
        else:
            break
    return text[:i].strip(), text[i:].strip()


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.set_chat_menu_button(
        chat_id=update.effective_chat.id,
        menu_button=MenuButtonWebApp(
            text="📅 Календарь",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    )
    await update.message.reply_text(
        "Привет! 🌸\n\n"
        "Просто отправляй смайлик — я запомню время и настроение.\n"
        "Можно добавить текст: `😊 встретились с подругами`\n\n"
        "Кнопка *📅 Календарь* внизу слева — открывает весь дневник.",
        parse_mode="Markdown"
    )


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    if not contains_emoji(text):
        await update.message.reply_text(
            "Отправь смайлик 😊\nИли смайлик с текстом: `🥰 отличный день`",
            parse_mode="Markdown"
        )
        return

    emoji, rest = extract_emoji(text)
    db.add_entry(user_id, emoji, rest)
    now = datetime.now()

    note = f"\n_{rest}_" if rest else ""
    await update.message.reply_text(
        f"Записала {emoji}  {now.strftime('%H:%M')} ✨{note}",
        parse_mode="Markdown"
    )


def build_app():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app


def main():
    db.init_db()
    print("Бот запущен 🌸")
    build_app().run_polling()


if __name__ == "__main__":
    main()
