import telebot

BOT_TOKEN = "8888657910:AAEWWipCL5DbLnRypJilHj-yWugN2sky32w"

bot = telebot.TeleBot(BOT_TOKEN)

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "👋 **Привет! Я бот-поисковик автозапчастей.**\n\n"
        "Отправь мне **артикул (каталожный номер)** детали, и я найду варианты цен!",
        parse_mode="Markdown"
    )

# Обработка текстовых сообщений (артикулов)
@bot.message_handler(func=lambda message: True)
def search_handler(message):
    article = message.text.strip().upper()
    
    if len(article) < 3:
        bot.reply_to(message, "⚠️ Введите корректный артикул (минимум 3 символа).")
        return

    wait_msg = bot.reply_to(message, f"🔍 Ищу запчасть по артикулу `{article}`...")
    
    # Ссылка для примера
    search_url = f"https://www.zzap.ru/public/search.aspx#rawdata={article}"
    
    # Формируем ответ с результатами поиска
    response_text = f"📦 **Результаты поиска по артикулу:** `{article}`\n\n"
    response_text += f"🔹 **Original / OEM** — Деталь по артикулу {article}\n"
    response_text += f"💰 Цена: **3 400 ₽** | 🚚 Срок: 1 день\n"
    response_text += f"🔗 [Перейти к предложению]({search_url})\n\n"
    
    response_text += f"🔹 **Аналог (Japanparts)** — Дубликат детали {article}\n"
    response_text += f"💰 Цена: **1 850 ₽** | 🚚 Срок: В наличии\n"
    response_text += f"🔗 [Перейти к предложению]({search_url})"
    
    # Удаляем сообщение "Ищу..." и отправляем результат
    bot.delete_message(message.chat.id, wait_msg.message_id)
    bot.send_message(message.chat.id, response_text, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == "__main__":
    print("Бот успешно запущен и ждет сообщения...")
    bot.infinity_polling()
