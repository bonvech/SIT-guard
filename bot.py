import config
import telebot
import os
import time
import datetime


def read_tuzik_status():
    global data_size_prev
    errors = 0

    ## run script on tuzik SIT computer
    cmd = 'sshpass -f tuzikey ssh root@192.168.1.200 /home/Tunka/guard/gu > ./status.dat'
    responce = os.system(cmd)
    print(responce)

    ## parse answer
    tuzik_status = open("./status.dat").read()
    #print(tuzik_status)
    if "fregat" not in tuzik_status:
        alarm_text = "Error! No fregat process found on SIT computer! Check SIT computer and start fregat programm!"
        print(alarm_text)
        bot.send_message(config.channel, alarm_text)
        errors = 1

    tuzik_status = tuzik_status.split('\n')
    print(tuzik_status[0])
    for line in tuzik_status:
        if "Status" in line:
            text = line
            print(text)
            bot.send_message(config.channel, text)
        if 'sda' in line:
            size = int(line.split()[-3])
            text = f'Free space: {size // 1024 // 1024} GB'
            print(text)
            bot.send_message(config.channel, text)
        if 'Data' in line:
            data_size = int(line.split()[0])
            text = f'Recorded: {(data_size - data_size_prev) // 1024} MB'
            print(text)
            bot.send_message(config.channel, text)
            data_size_prev = data_size
    return errors


def read_tuzik_enable_status():
    errors = 0

    ##  get 'enable' file from tuzik
    responce = os.system(". ./scpirt")
    if responce:
        alarm_text = f"Error in responce from tuzik: {responce}"
        print(alarm_text)
        bot.send_message(config.channel, alarm_text)

    ## read enable status
    current_status = open("enable.txt").read().strip()
    return errors, current_status


if __name__ == "__main__":

    enable_status = "SIT Guard starts\n"
    data_size_prev = 0

    bot = telebot.TeleBot(config.token) #, parse_mode=None)

    while True:
        ##  read enable status
        errors, current_status = read_tuzik_enable_status()
        print(datetime.datetime.today(), current_status)

        ##  if enable status changed
        if current_status != enable_status:
            text = f"{enable_status} -> {current_status}"
            print(text)
            bot.send_message(config.channel, text)
            enable_status = current_status

            ##  get tuzik status and print to bot
            read_tuzik_status()

        time.sleep(300)
