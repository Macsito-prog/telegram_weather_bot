import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
from dotenv import load_dotenv
import os

load_dotenv()

telegram_token = os.getenv("BOT_TOKEN")

print(f"Telegram token loaded: {telegram_token.split(':')[0]}")

# logging (following the echobot example)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# command handler. 2 arguments: update and context
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """send a message when the command /start is issued"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",  #añadir acá la respuesta de open weather?
        reply_markup=ForceReply(selective=True),
    )

async def clima(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ask for city when the command /ciudad is issued"""
    user = update.message.from_user
    await update.message.reply_text(
        "Por favor, ingresa el nombre de la ciudad la cual quieres consultar el clima: "
    )

def main() -> None:
    """Start the bot"""
    #start the app and pass the token
    application = Application.builder().token(telegram_token).build()

    # answer in telegram
    application.add_handler(CommandHandler("start", start))

    #calling /clima (?)
    application.add_handler(CommandHandler("clima"), clima)

    #on non-commands return the same text 
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    #run the app until closure
    application.run_polling(allowed_updates=Update.ALL_TYPES)


async def echo(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo user message"""
    await update.message.reply_text(update.message.text)



def get_coord(city_name):
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=10&language=en&format=json"
    req = requests.get(geocoding_url)
    respuesta = req.json()
    stgo_latitude = respuesta["results"][0]["latitude"]
    stgo_longitude = respuesta["results"][0]["longitude"]
    print(f"Latitud de santiago: {stgo_latitude}")
    print(f"Longitud de santiago: {stgo_longitude}")
    return stgo_latitude, stgo_longitude

def get_weather_by_coords(latitude, longitude):
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m"
    req = requests.get(weather_url)
    respuesta = req.json()
    print(respuesta)
    return respuesta


if __name__ == "__main__":
    main()