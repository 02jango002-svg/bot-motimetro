import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Configuración de Flask para mantener vivo el bot en Render ---
app = Flask('')


@app.route('/')
def home():
  return '¡El bot de Motimetro está activo!'


def run():
  app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)


def keep_alive():
  t = threading.Thread(target=run)
  t.daemon = True
  t.start()


# --- Comando /start del bot de Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      '¡Hola! Bienvenido al bot de tarifas de mototaxi.\n'
      'Tarifa mínima: S/ 4.00 | Costo por km: S/ 1.50'
  )


def main():
  # Token de Telegram
  token = os.environ.get(
      'TELEGRAM_BOT_TOKEN', '8978065603:AAFv2y1rw0sG9QnFJ2h1ZemuUoea33ERh9g'
  )

  # Iniciar servidor web en segundo plano
  keep_alive()

  # Iniciar bot de Telegram
  application = ApplicationBuilder().token(token).build()
  application.add_handler(CommandHandler('start', start))

  print('Iniciando bot de Telegram...')
  application.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
  main()
