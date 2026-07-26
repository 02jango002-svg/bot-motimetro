import os
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Servidor web para mantener activo el servicio en Render
app = Flask('')

@app.route('/')
def home():
    return "Bot de Mototaxis Activo 24/7"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Comando /start del bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Bienvenido al bot de tarifas de mototaxi.\n"
        "Tarifa mínima: S/ 4.00 | Costo por km: S/ 1.50"
    )

def main():
    # Token configurado directamente para asegurar funcionamiento inmediato
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "8978065603:AAFv2y1rw0sG9QnFJ2h1ZemuUoea33ERh9g")

    # Iniciar servidor web en segundo plano
    keep_alive()

    # Iniciar bot de Telegram
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    
    print("Iniciando bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
