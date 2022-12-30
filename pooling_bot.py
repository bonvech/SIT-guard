import telebot
from telebot import types
import guard
import config
from guard import SIT_guard
from guard import send_text

bot = telebot.TeleBot(config.token) #, parse_mode=None)

@bot.message_handler(commands = ['start'])
def any_msg(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width=3)
    btn1 = types.KeyboardButton(text="Status")
    btn2 = types.KeyboardButton(text="Params") 
    btn3 = types.KeyboardButton(text="5sec")
    btn4 = types.KeyboardButton(text="Refresh")
    keyboard.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "Switch action from keyboard", reply_markup=keyboard)


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
        text = "Switch next action"
    else:
        text = "Switch action"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width=3)
    btn1 = types.KeyboardButton(text="Status")
    btn2 = types.KeyboardButton(text="Params") 
    btn3 = types.KeyboardButton(text="5sec")
    btn4 = types.KeyboardButton(text="Refresh")
    keyboard.add(btn1, btn2, btn3, btn4)    
    bot.send_message(message.chat.id, text, reply_markup=keyboard)
    #print(message.chat.id, text)


if __name__ == '__main__': 
    #guard = SIT_guard(testing_mode=True)
    guard = SIT_guard()

    bot.infinity_polling() 