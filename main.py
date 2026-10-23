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


# Словарь для сохранения шагов пользователя: {user_id: {'brand': ..., 'model': ..., 'year': ..., 'step': ...}}
user_data = {}


# Команда /start — первый шаг (спрос марки)
@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    user_data[user_id] = {"step": "brand"}
    bot.reply_to(
        message,
        "👋 **Привет! Я бот-поисковик автозапчастей.**\n\n"
        "Давайте подберем деталь правильно. Сначала укажите **марку автомобиля** (например: `BMW`, `Toyota`, `Ford`):",
        parse_mode="Markdown",
    )


# Пошаговый обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_steps(message):
    user_id = message.from_user.id
    text = message.text.strip()

    # Если пользователь написал что-то без /start, инициализируем с нуля
    if user_id not in user_data:
        user_data[user_id] = {"step": "brand"}
        bot.reply_to(message, "Давайте начнем сначала. Укажите **марку автомобиля**:", parse_mode="Markdown")
        return

    current_step = user_data[user_id].get("step")

    # Шаг 1: Получаем марку
    if current_step == "brand":
        user_data[user_id]["brand"] = text
        user_data[user_id]["step"] = "model"
        bot.reply_to(
            message,
            f"Отлично, марка: **{text}**.\nТеперь укажите **модель автомобиля** (например: `M5 E39`, `Camry`, `Focus`):",
            parse_mode="Markdown",
        )

    # Шаг 2: Получаем модель
    elif current_step == "model":
        user_data[user_id]["model"] = text
        user_data[user_id]["step"] = "year"
        bot.reply_to(
            message,
            f"Модель: **{text}**.\nТеперь укажите **год выпуска** (например: `2003`):",
            parse_mode="Markdown",
        )

    # Шаг 3: Получаем год
    elif current_step == "year":
        user_data[user_id]["year"] = text
        user_data[user_id]["step"] = "article"
        bot.reply_to(
            message,
            f"Год: **{text}**.\nТеперь введите **артикул (каталожный номер)** или название запчасти:",
            parse_mode="Markdown",
        )

    # Шаг 4: Получаем артикул и выдаем результат
    elif current_step == "article":
        article = text
        brand = user_data[user_id].get("brand")
        model = user_data[user_id].get("model")
        year = user_data[user_id].get("year")

        # Формируем поисковые запросы (чистый артикул для каталогов + общий запрос для маркетплейсов)
        encoded_article = urllib.parse.quote(article)
        full_query = f"{brand} {model} {year} {article}"
        encoded_full = urllib.parse.quote(full_query)

        url_exist = f"https://www.exist.ru/Price/?pcode={encoded_article}"
        url_autodoc = f"https://www.autodoc.ru/price/{encoded_article}"
        url_ozon = f"https://www.ozon.ru/search/?text={encoded_full}"
        url_avito = f"https://www.avito.ru/rossiya/zapchasti_i_aksessuary?q={encoded_full}"

        response_text = (
            f"🚗 **Автомобиль:** {brand} {model} ({year} г.)\n"
            f"🔍 **Запчасть / Артикул:** {article}\n\n"
            "Ссылки для поиска нужной детали:\n\n"
            f"🔹 [Искать на Exist.ru]({url_exist})\n"
            f"🔹 [Искать на Autodoc.ru]({url_autodoc})\n"
            f"🔹 [Искать на Ozon]({url_ozon})\n"
            f"🔹 [Искать б/у на Avito]({url_avito})\n\n"
            "🔄 Чтобы найти другую деталь, просто отправьте команду /start"
        )

        # Сбрасываем шаг на начало для следующего поиска
        user_data[user_id] = {"step": "brand"}

        bot.reply_to(message, response_text, parse_mode="Markdown", disable_web_page_preview=True)
        bot.send_message(
            message.chat.id,
            "Хотите найти еще запчасть? Укажите **марку автомобиля** для нового поиска:",
            parse_mode="Markdown"
        )


if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    bot.infinity_polling()
