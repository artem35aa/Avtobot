import os
from threading import Thread
import telebot
from flask import Flask

# 1. Получаем токен из настроек Render (или используем ваш прямой токен)
BOT_TOKEN = os.environ.get(
    "BOT_TOKEN", "8888657910:AAEWipCL5DbLnRypJiLHj-yWugN2sky32w"
)
bot = telebot.TeleBot(BOT_TOKEN)

# 2. Создаем веб-сервер Flask для требований Render
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running 24/7!"


def run_web():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


# ==========================================
# 3. ВАШИ КОМАНДЫ И ОБРАБОТЧИКИ БОТА
# ==========================================


# Команда /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(
      message,
      "👋 **Привет! Я бот-поисковик автозапчастей.**\n"
      "Отправь мне **артикул (каталожный номер)**.",
      parse_mode="Markdown",
  )


# Обработка текстовых сообщений (артикулов)
@bot.message_handler(func=lambda message: True)
def search_handler(message):
  article = message.text.strip().upper()

  if len(article) < 3:
    bot.reply_to(message, "⚠️ Введите корректный артикул (минимум 3 символа).")
    return

  # Здесь добавьте вашу логику поиска запчастей
  bot.reply_to(message, f"🔍 Ищу запчасть по артикулу: **{article}**...")


# ==========================================

if __name__ == "__main__":
  # Запускаем веб-сервер в фоновом потоке
  t = Thread(target=run_web)
  t.start()

  # Запускаем постоянную работу Telegram-бота
  bot.infinity_polling()
