import os
from threading import Thread
import telebot
from flask import Flask

# Точный токен бота
BOT_TOKEN = "8888657910:AAEWWipCL5DbLnRypJilHj-yWugN2sky32w"
bot = telebot.TeleBot(BOT_TOKEN)

# Веб-сервер Flask для требований Render
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running 24/7!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# 📚 Встроенный каталог запчастей (сюда можно добавлять новые детали)
PARTS_CATALOG = {
    "71631": {
        "name": "Масляный фильтр MANN-FILTER",
        "OEM": "HU 711/51 x",
        "price": "850 руб.",
        "stock": "В наличии (склад)",
        "analogs": "Bosch, Mahle, Filtron"
    },
    "W71275": {
        "name": "Масляный фильтр Mann",
        "OEM": "06A115561B",
        "price": "620 руб.",
        "stock": "В наличии",
        "analogs": "Knecht, Fram"
    },
    "BKR6E": {
        "name": "Свеча зажигания NGK",
        "OEM": "22401AA530",
        "price": "450 руб. / шт.",
        "stock": "Под заказ (1 день)",
        "analogs": "Denso K20PR-U"
    }
}


# Команда /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "👋 **Привет! Я бот-поисковик автозапчастей по каталогу.**\n\n"
        "Отправь мне **артикул** детали (например: `71631`, `W71275` или `BKR6E`).",
        parse_mode="Markdown",
    )


# Обработка текстовых сообщений (поиск по каталогу)
@bot.message_handler(func=lambda message: True)
def search_handler(message):
    article = message.text.strip().upper()

    if len(article) < 2:
        bot.reply_to(message, "⚠️ Введите корректный артикул.")
        return

    # Ищем деталь в словаре каталога
    part = PARTS_CATALOG.get(article)

    if part:
        response_text = (
            f"✅ **Найдено в каталоге:**\n\n"
            f"📦 **Деталь:** {part['name']}\n"
            f"🔢 **Артикул / OEM:** {article} ({part['OEM']})\n"
            f"💰 **Цена:** {part['price']}\n"
            f"📍 **Наличие:** {part['stock']}\n"
            f"🔄 **Аналоги:** {part['analogs']}"
        )
    else:
        response_text = (
            f"❌ По артикулу **{article}** ничего не найдено в каталоге.\n\n"
            f"💡 Попробуйте тестовые артикулы: `71631`, `W71275`, `BKR6E`"
        )

    bot.reply_to(message, response_text, parse_mode="Markdown")


if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    bot.infinity_polling()
