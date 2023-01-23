import telebot
from telebot import types
import guard
import config
from guard import SIT_guard
from guard import send_text
from pyowm import OWM
# pip install pyowm==3.3.0


bot = telebot.TeleBot(config.token) #, parse_mode=None)

#  open weather
owm = OWM(config.owm_token)
mgr = owm.weather_manager()


def get_weather():
    clouds = []
    for city in ['Zhemchug', 'Slyudyanka']:
        observation = mgr.weather_at_place(city)  # the observation object is a box containing a weather object
        weather = observation.weather
        temp = weather.temperature('celsius')
        t1 = round(temp['temp'], 1)
        hum = weather.humidity
        wind = weather.wind()['speed']
        #print(t1, t2, hum, wind)
        clouds.append(f"{city:10s}: {t1:4.1f}°C,  {wind} m/s,  {weather.detailed_status}")
    return "\n".join(clouds)



@bot.message_handler(commands = ['start'])
def any_msg(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width=3)
    btn1 = types.KeyboardButton(text="Status")
    btn2 = types.KeyboardButton(text="Params") 
    btn3 = types.KeyboardButton(text="5sec")
    btn4 = types.KeyboardButton(text="Refresh")
    btn5 = types.KeyboardButton(text="Weather")
    keyboard.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, "Choose action from keyboard", reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def answer_to_messages(message): 
    if message.text == "Status":
        guard.read_enable_status()
        guard.read_status()
        guard.parse_status()
        text = guard.tuzik_short_status + '\n' + guard.current_enable_status
    elif message.text == "Params":
        guard.read_1m_data()
        text = guard.m1_data
    elif message.text == "5sec":
        guard.read_5s_data()
        text = guard.s5_data
    elif message.text == "Refresh":
        guard.get_period_data()
        text = "Choose next action"
    elif message.text == "Weather":
        text = get_weather()
    else:
        text = "Choose action"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width=3)
    btn1 = types.KeyboardButton(text="Status")
    btn2 = types.KeyboardButton(text="Params") 
    btn3 = types.KeyboardButton(text="5sec")
    btn4 = types.KeyboardButton(text="Refresh")
    btn5 = types.KeyboardButton(text="Weather")
    keyboard.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)
    #print(message.chat.id, text)


if __name__ == '__main__': 
    #guard = SIT_guard(testing_mode=True)
    guard = SIT_guard()
    guard.set_log_file_name("guard_bot_log.txt")

    bot.infinity_polling() 
