import requests
import logging
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


updater = Updater(token='TELEGRAM_API_TOKEN', use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    update.message.reply_text("Привет! У меня ты можешь узнать погоду! Введи название города после команды /weather \n"
                              "Чтобы попросить у меня совет о том что сегодня надеть, набери команду /clothes и укажи название "
                              "твоего города.")


def weather(update, context):
    user_text = context.args
    if len(user_text) == 0:
        update.message.reply_text("Вы забыли ввести название города!")
    city = user_text[0]
    res = _response_to_weather_api(city)
    data = json.loads(res)
    if data['status'] == False:
        update.message.reply_text('Либо ты ввел название города с ошибкой, либо это вообще какая-то белеберда')
    else:
        update.message.reply_text('Общее состояние погоды в этом городе: {0}, температура: {1}°C, ощущается как {2}°C,'
                                  'максимальная температура на сегодня: {3}°C, минимальная: {4}°C'
                                  ' скорость ветра:  {5} м/с'.format(data['main_condition'], data['real_temp'],
                                                                     data['feels_like_temp'], data['max_temp'],
                                                                     data['min_temp'], data['wind_speed']))
    

def clothes(update, context):
    user_text = context.args
    if len(user_text) == 0:
        update.message.reply_text("Вы забыли ввести название города!")
    city = user_text[0]
    res = _response_to_weather_api(city)
    data = json.loads(res)
    
    if data['status'] == False:
        update.message.reply_text('Либо ты ввел название города с ошибкой, либо это вообще какая-то белеберда')
    else:
        text_for_answer = ''.join('Общее состояние погоды в этом городе: {0}, температура: {1}°C, ощущается как {2}°C,'
                                  'максимальная температура на сегодня: {3}°C, минимальная: {4}°C'
                                  ' скорость ветра:  {5} м/с'.format(data['main_condition'], data['real_temp'],
                                                                     data['feels_like_temp'], data['max_temp'],
                                                                     data['min_temp'], data['wind_speed']))
        text_for_answer = text_for_answer + '\n'                                                        
        if("дождь" in data['main_condition']):
            text_for_answer = text_for_answer + "Пожалуй вам стоит взять зонт."
        temp = int(data['feels_like_temp'])
        if temp > 5 and temp < 15:
            text_for_answer = text_for_answer + "Советуем надеть осеннюю куртку или пальто"
        elif temp < 5 and temp > -10:
            text_for_answer = text_for_answer +  "Прохладно. Надевайте зимнюю куртку!"
        elif temp < -10:
            text_for_answer = text_for_answer + "Что-то сегодня очень холодно. Надевайте зимнюю куртку и теплую кофту."
        elif temp > 15:
            text_for_answer = text_for_answer + "Сегодня тепло! Одевайся как вам нравится под такую погоду!"

        update.message.reply_text(text_for_answer)



def _response_to_weather_api(city):
    params = {'q': city, 'APPID': 'WEATHER_API_TOKEN'}
    req_weather = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
    if req_weather.status_code != 200:
        return json.dumps({'status': False})
    else:
        data = json.loads(req_weather.text)
        weather = data['weather']
        main_condition_to_translate = weather[0]['description']
        main_condition = _response_to_translate_api(main_condition_to_translate)
        temp_arr = data['main']
        real_temp = int(temp_arr['temp']) - 273
        feels_like_temp = int(temp_arr['feels_like']) - 273
        max_temp = int(temp_arr['temp_max']) - 273
        min_temp = int(temp_arr['temp_min']) - 273
        wind_arr = data['wind']
        wind_speed = wind_arr['speed']
        return json.dumps({'status': True, 'main_condition': main_condition, 'real_temp': real_temp,
                           'feels_like_temp': feels_like_temp, 'max_temp': max_temp,
                           'min_temp': min_temp, 'wind_speed': wind_speed})


def _response_to_translate_api(text):
    params_translate = {'key': 'TRANSLATE_API_TOKEN',
                        'text': text, 'lang': 'ru'}
    req_translate = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate', params_translate)
    data_translate = json.loads(req_translate.text)
    description_parameter_translated = data_translate['text'][0]
    return description_parameter_translated


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


start_handler = CommandHandler('start', start)
weather_handler = CommandHandler('weather', weather)
clothes_handler = CommandHandler('clothes', clothes)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(clothes_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(weather_handler)
dispatcher.add_handler(unknown_handler)
def main():
    updater.start_polling()


if __name__ == "__main__":
    main()
