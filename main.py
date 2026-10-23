import os
from threading import Thread
import telebot
from flask import Flask
import requests
from bs4вання import BeautifulSoup  # или bs4

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


# Функция парсинга Ozon по артикулу
def search_ozon(article):
    try:
        url = f"https://www.ozon.ru/search/?text={article}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9",
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "⚠️ Не удалось подключиться к Ozon (ошибка сервера)."

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ozon часто меняет структуру классов, но базовый поиск выдает карточки товаров.
        # Ищем блоки товаров по тегам или ссылкам
        items = []
        # Ищем ссылки на товары, содержащие /product/
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/product/' in href and href not in [i['link'] for i in items]:
                title_elem = a.find(['span', 'div'], string=True)
                title = title_elem.text.strip() if title_elem else "Автозапчасть с Ozon"
                if len(title) > 10:   отсеиваем короткий мусор
                    full_link = f"https://www.ozon.ru{href.split('?')[0]}"
                    items.append({'title': title, 'link': full_link})
                    if len(items) >= 3:  # Берем первые 3 результата
                        break

        if not items:
            return f"❌ По артикулу **{article}** на Ozon ничего не найдено."

        result_text = f"🔍 Результаты поиска на Ozon для **{article}**:\n\n"
        for idx, item in enumerate(items, 1):
            result_text += f"{idx}. [{item['title']}]({item['link']})\n\n"
            
        return result_text

    except Exception as e:
        return f"⚠️ Ошибка при поиске: {str(e)}"


# Команда /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "👋 **Привет! Я бот-поисковик автозапчастей по Ozon.**\n"
        "Отправь мне **артикул (каталожный номер)**, и я найду детали.",
        parse_mode="Markdown",
    )


# Обработка текстовых сообщений (артикулов)
@bot.message_handler(func=lambda message: True)
def search_handler(message):
    article = message.text.strip()

    if len(article) < 3:
        bot.reply_to(message, "⚠️ Введите корректный артикул (минимум 3 символа).")
        return

    msg = bot.reply_to(message, f"🔍 Ищу запчасть **{article}** на Ozon...")
    
    # Запускаем парсинг
    search_result = search_ozon(article)
    
    # Отправляем результаты пользователю
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg.message_id,
        text=search_result,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    bot.infinity_polling()
