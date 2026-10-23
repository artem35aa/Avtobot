import os
from threading import Thread
import telebot
from flask import Flask
import urllib.parse

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


# Команда /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "👋 **Привет! Я бот-поисковик автозапчастей.**\n\n"
        "Отправь мне **артикул (каталожный номер)** детальки, и я сформирую "
        "прямые ссылки на поиск по крупным каталогам и магазинам, где можно выбрать из множества вариантов.",
        parse_mode="Markdown",
    )


# Обработка текстовых сообщений (формирование ссылок на поиск)
@bot.message_handler(func=lambda message: True)
def search_handler(message):
    article = message.text.strip()

    if len(article) < 2:
        bot.reply_to(message, "⚠️ Введите корректный артикул.")
        return

    # Кодируем артикул для использования в URL (чтобы корректно обрабатывать пробелы и спецсимволы)
    encoded_article = urllib.parse.quote(article)

    # Формируем ссылки на поисковые страницы разных платформ
    url_exist = f"https://www.exist.ru/Price/?pcode={encoded_article}"
    url_autodoc = f"https://www.autodoc.ru/price/{encoded_article}"
    url_emex = f"https://www.emex.ru/autoparts?searchString={encoded_article}"
    url_ozon = f"https://www.ozon.ru/search/?text={encoded_article}"
    url_avito = f"https://www.avito.ru/rossiya/zapchasti_i_aksessuary?q={encoded_article}"

    response_text = (
        f"🔍 Результаты поиска по артикулу: **{article}**\n\n"
        "Нажмите на любую ссылку, чтобы открыть сайты и найти много предложений:\n\n"
        f"🔹 [Искать на Exist.ru]({url_exist})\n"
        f"🔹 [Искать на Autodoc.ru]({url_autodoc})\n"
        f"🔹 [Искать на Emex.ru]({url_emex})\n"
        f"🔹 [Искать на Ozon]({url_ozon})\n"
        f"🔹 [Искать б/у на Avito]({url_avito})"
    )

    bot.reply_to(message, response_text, parse_mode="Markdown", disable_web_page_preview=True)


if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    bot.infinity_polling()
 
