import os
from math import atan2, cos, radians, sin, sqrt
import threading
from flask import Flask
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

# --- Configuración de Flask para mantener vivo el bot en Render ---
app = Flask('')


@app.route('/')
def home():
  return '¡El bot de Motimetro está activo!'


def run():
  app.run(host='0.0.0.0', port=10000)


def keep_alive():
  t = threading.Thread(target=run)
  t.daemon = True
  t.start()


# Estados de la conversación para pedir origen y destino
GET_ORIGIN, GET_DESTINATION = range(2)


# Fórmula matemática para calcular la distancia en kilómetros entre 2 coordenadas
def calcular_distancia(lat1, lon1, lat2, lon2):
  R = 6371.0  # Radio de la Tierra en km
  dlat = radians(lat2 - lat1)
  dlon = radians(lon2 - lon1)
  a = (
      sin(dlat / 2) ** 2
      + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
  )
  c = 2 * atan2(sqrt(a), sqrt(1 - a))
  return R * c


# Paso 1: Comando /start (Pide ubicación de partida)
def start(update, context):
  keyboard = [[KeyboardButton('📍 Compartir ubicación actual', request_location=True)]]
  reply_markup = ReplyKeyboardMarkup(
      keyboard, one_time_keyboard=True, resize_keyboard=True
  )
  update.message.reply_text(
      '¡Hola! Bienvenido al bot de tarifas de mototaxi 🛺.\n\n'
      'Para calcular tu viaje, por favor comparte tu **ubicación de partida** presionando el botón de abajo:',
      reply_markup=reply_markup,
      parse_mode='Markdown',
  )
  return GET_ORIGIN


# Paso 2: Recibe el origen y pide el destino
def recibir_origen(update, context):
  user_location = update.message.location
  context.user_data['orig_lat'] = user_location.latitude
  context.user_data['orig_lon'] = user_location.longitude

  keyboard = [[KeyboardButton('📍 Compartir ubicación de destino', request_location=True)]]
  reply_markup = ReplyKeyboardMarkup(
      keyboard, one_time_keyboard=True, resize_keyboard=True
  )
  update.message.reply_text(
      '¡Perfecto! Ahora comparte tu **ubicación de destino** presionando el siguiente botón:',
      reply_markup=reply_markup,
      parse_mode='Markdown',
  )
  return GET_DESTINATION


# Paso 3: Recibe el destino, calcula la distancia y la tarifa
def recibir_destino(update, context):
  dest_location = update.message.location
  lat1 = context.user_data['orig_lat']
  lon1 = context.user_data['orig_lon']
  lat2 = dest_location.latitude
  lon2 = dest_location.longitude

  # Calcular distancia en km
  distancia = calcular_distancia(lat1, lon1, lat2, lon2)

  # Calcular tarifa (S/ 1.50 por km, con tarifa mínima de S/ 4.00)
  tarifa = distancia * 1.50
  if tarifa < 4.00:
    tarifa = 4.00

  mensaje = (
      f'📊 **Resultado de tu viaje:**\n\n'
      f'📏 **Distancia estimada:** {distancia:.2f} km\n'
      f'💰 **Tarifa total:** S/ {tarifa:.2f}\n\n'
      f'*(Tarifa mínima: S/ 4.00 | Costo por km: S/ 1.50)*\n\n'
      f'Escribe /start si deseas calcular otro viaje.'
  )

  update.message.reply_text(
      mensaje, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown'
  )
  return ConversationHandler.END


def cancelar(update, context):
  update.message.reply_text(
      'Operación cancelada. Escribe /start para empezar de nuevo.',
      reply_markup=ReplyKeyboardRemove(),
  )
  return ConversationHandler.END


def main():
  token = os.environ.get(
      'TELEGRAM_BOT_TOKEN', '8978065603:AAFv2y1rw0sG9QnFJ2h1ZemuUoea33ERh9g'
  )

  keep_alive()

  updater = Updater(token, use_context=True)
  dp = updater.dispatcher

  # Administrador de pasos conversacionales
  conv_handler = ConversationHandler(
      entry_points=[CommandHandler('start', start)],
      states={
          GET_ORIGIN: [MessageHandler(Filters.location, recibir_origen)],
          GET_DESTINATION: [MessageHandler(Filters.location, recibir_destino)],
      },
      fallbacks=[CommandHandler('cancel', cancelar)],
  )

  dp.add_handler(conv_handler)

  print('Iniciando bot de Telegram con cálculo de distancias...')
  updater.start_polling()
  updater.idle()


if __name__ == '__main__':
  main()
