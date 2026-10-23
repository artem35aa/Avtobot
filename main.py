import os
import sys
from threading import Thread
import telebot
from flask import Flask

# Настройка логирования в stdout
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Точный токен бота
BOT_TOKEN = os.environ.get(
    "BOT_TOKEN", "8888657910:AAEWWipCL5DbLnRypJilHj-yWugN2sky32w"
)
bot = telebot.TeleBot(BOT_TOKEN)

# Веб-сервер Flask для требований Render
app = Flask(__name__)


@app.route("/")
def home():
    logger.info("Веб-сервер Flask: GET запрос к /")
    return "Bot is running 24/7!"


def run_web():
    logger.info("Запускаем поток веб-сервера Flask...")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    logger.info(f"Веб-сервер Flask запущен на порту {port} (в потоке)")


# ==========================================
# 3. ВАШИ КОМАНДЫ И ОБРАБОТЧИКИ БОТА
# ==========================================


# Команда /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
    bot.reply_to(
        message,
        "👋 **Привет! Я бот-поисковик автозапчастей.**\n"
        "Отправь мне **артикул (каталожный номер)**.",
        parse_mode="Markdown",
    )
    logger.info("Ответ на /start отправлен.")


# Обработка текстовых сообщений (артикулов)
@bot.message_handler(func=lambda message: True)
def search_handler(message):
    article = message.text.strip().upper()
    logger.info(f"Получен текст от пользователя {message.from_user.id}: {article}")

    if len(article) < 3:
        bot.reply_to(message, "⚠️ Введите корректный артикул (минимум 3 символа).")
        return

    bot.reply_to(message, f"🔍 Ищу запчасть по артикулу: **{article}**...")
    logger.info(f"Ответ на артикул {article} отправлен.")


# ==========================================

if __name__ == "__main__":
    logger.info("Запуск бота...")
    
    # Запускаем веб-сервер в фоновом потоке
    t = Thread(target=run_web)
    t.start()
    
    logger.info("Главный поток: поток веб-сервера запущен. Начинаем Telegram polling...")

    try:
        # Запускаем постоянную работу Telegram-бота
        bot.infinity_polling(timeout=20)
        logger.info("Telegram polling завершен.")
    except Exception as e:
        logger.error(f"Произошла ошибка при polling: {e}")
        # Если polling упал, не выходим, чтобы Render не решил, что сервис мертв
        t.join() 
    
    logger.info("Завершение работы.")
