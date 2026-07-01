import logging
import asyncio
import requests
import json
import os
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()
telegram_token = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """send a message when the command /start is issued"""
    user = update.effective_user
    await update.message.reply_html(rf"Hi {user.mention_html()}!")


async def clima(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """obtains weather information using the city in config"""
    config = load_config()
    city_name = config["city"]
    if city_name == "":
        await update.message.reply_text("Por favor ingresa /ciudad NombreCiudad primero")
    else:
        await update.message.reply_text(f"Buscando el clima para {city_name}...")
        lat, lon = get_coord(city_name)
        weather = get_weather_by_coords(lat, lon)
        await update.message.reply_text(str(weather))


async def ciudad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """saves the city when the user issues /ciudad NombreCiudad"""
    if not context.args:
        await update.message.reply_text("Uso: /ciudad NombreCiudad")
        return
    city_name = context.args[0]
    save_config(city_name)
    await update.message.reply_text(f"Ciudad guardada: {city_name}")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """echo user message"""
    await update.message.reply_text(update.message.text)


def get_coord(city_name):
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=es&format=json"
    req = requests.get(geocoding_url)
    respuesta = req.json()
    latitude = respuesta["results"][0]["latitude"]
    longitude = respuesta["results"][0]["longitude"]
    return latitude, longitude


def get_weather_by_coords(latitude, longitude):
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m"
    req = requests.get(weather_url)
    respuesta = req.json()
    temperature = str(respuesta["current"]["temperature_2m"]) + '°C' 
    return temperature


def load_config():
    filename = 'config.json'
    try:
        with open(filename, "r", encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"city": ""}
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    return data


def save_config(city_name):
    filename = 'config.json'
    data = {"city": city_name}
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def main() -> None:
    asyncio.set_event_loop(asyncio.new_event_loop())
    application = Application.builder().token(telegram_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clima", clima))
    application.add_handler(CommandHandler("ciudad", ciudad))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()