import config
import telebot
import os
import time
import datetime


def send_text(channel, message, testing_mode=False):
    #print(message)
    if not testing_mode:
        bot = telebot.TeleBot(config.token, parse_mode=None)
        bot.send_message(channel, message)
    else:
        print(f"Print text:\n{message} \n to channel: {channel}")


def text_sender(channel, testing_mode):
    def sender(message):
        return send_text(channel, message, testing_mode)
    return sender



class SIT_guard():
    def __init__(self, testing_mode=False):
        self.testing_mode  = testing_mode
        self.data_size_prev = 0
        self.free_space    = -1000
        self.logfile       = "guard_log.txt"
        #self.enable_status = "SIT guard starts\n"
        self.previous_enable_status = "SIT guard starts\n"
        self.current_enable_status  = "SIT guard starts\n"
        self.previous_operation_status = "Dummy previous operation status"
        self.current_operation_status  = "Dummy current operation status"
        self.tuzik_status  = "No ./status.dat file read yet"
        self.tuzik_short_status  = "No ./status.dat file read yet"
        self.m1_data       = "No ./1m.data file read yet"
        self.s5_data       = "No ./5s.data file read yet"
        self.text_date, self.text_free, self.text_recorded, self.text_status = ['dummy status'] * 4


        ## decorators for functions sending to bot 
        self.send_alarm = text_sender(config.channel_alarm, self.testing_mode)
        self.send_info  = text_sender(config.channel, self.testing_mode) 



#    def send_info(self, message, testing_mode=True):
#        print(message)
#        if not testing_mode:
#            bot.send_message(config.channel, message)


    def get_info_from_tuzik(self, cmd):
        if testing_mode:
            print(f"Test get_info_from_tuzik() \n{cmd}")
            return -1
        responce = os.system(cmd)
        #print(responce)
        if responce:
            alarm_message = f"Error in responce from tuzik: {responce} in command " + cmd
            self.send_alarm(alarm_message)
            return 1
        return 0


    def get_status(self):
        ## run script on tuzik SIT computer
        cmd = 'sshpass -f tuzikey ssh root@192.168.1.200 /home/Tunka/guard/gu > ./status.dat'
        self.get_info_from_tuzik(cmd)


    def get_enable_status(self):
        ##  get 'enable' file from tuzik
        cmd = "sshpass -f tuzikey ssh root@192.168.1.200 cat /var/www/htdocs/enable.txt > ./enable.txt"
        self.get_info_from_tuzik(cmd)


    def get_period_data(self):
        ##  get 1m and 5s files from tuzik
        cmd = "sshpass -f tuzikey ssh root@192.168.1.200 cat /var/www/htdocs/1m.data > ./1m.data"
        self.get_info_from_tuzik(cmd)
        cmd = "sshpass -f tuzikey ssh root@192.168.1.200 cat /var/www/htdocs/5s.data > ./5s.data"
        self.get_info_from_tuzik(cmd)


    def print_to_log_file(self, text):
        text = str(datetime.datetime.today())[:19] + "    " + text
        print(text)
        f = open(self.logfile, "a")
        f.write(text + '\n')
        f.close()


    def read_enable_status(self):
        ## read enable status
        self.previous_enable_status = self.current_enable_status
        self.current_enable_status = open("enable.txt").read().strip()

        ## print to logfile
        self.print_to_log_file(self.current_enable_status)


    def read_status(self):
        self.tuzik_status = open("./status.dat").read()
        self.print_to_log_file(self.tuzik_status)


    def send_status(self):
        self.parse_status()
        self.send_info(self.tuzik_short_status)


    def read_5s_data(self):
        self.s5_data = open("./5s.data").read().rstrip()
        self.print_to_log_file(self.s5_data)
        #print([self.s5_data])
        #self.send_info(self.s5_data)


    def read_1m_data(self):
        self.m1_data = open("./1m.data").read().rstrip()
        self.print_to_log_file(self.m1_data)
        #print([self.m1_data])
        #self.send_info(self.m1_data)


    def read_period_data(self):
        self.read_5s_data()
        self.read_1m_data()


    def parse_status(self):
        ## parse status
        tuzik_status = self.tuzik_status
        if "fregat" not in tuzik_status:
            alarm_text = "Error! No fregat process found on SIT computer! Check SIT computer and start fregat programm!"
            self.send_alarm(alarm_text)
            errors = 1

        tuzik_status = tuzik_status.split('\n')
        self.text_date = tuzik_status[0]
        for line in tuzik_status:
            ##  get status line
            if "Status" in line:
                self.text_status = line
                self.current_operation_status = line

            ##  available space on HDD
            if 'sda' in line:
                size = int(line.split()[-3])
                self.free_space = size
                self.text_free = f'Free space: {size // 1024 // 1024} GB'
                ##  if space < 2 Gb
                if size // 1024 // 1024  < 2:
                    alarm_text = "Error! Available space less than 2 GB. " + self.text_free
                    self.send_alarm(alarm_text)
                    errors = 1

            ##  size of Tunka/Data directory
            if 'Data' in line:
                data_size = int(line.split()[0])
                #self.text_recorded = f'Recorded: {(data_size) // 1024} MB'
                self.text_recorded = f'Recorded: {(data_size - self.data_size_prev) // 1024} MB'
                self.data_size_prev = data_size

        self.tuzik_short_status = "\n".join([self.text_date, self.text_free, self.text_recorded, self.text_status])
        #self.send_info(text)


    def operation_status_changed(self):
        ##  get file with operation status 
        self.get_period_data()
        self.read_5s_data()

        ##  read operation status from file
        self.previous_operation_status = self.current_operation_status
        status = self.s5_data.split('\n')
        for line in status:
            if "Status" in line:
                self.current_operation_status = line
                break

        ##  check changes
        if self.current_operation_status != self.previous_operation_status:
            return True
        return False


    def enable_status_changed(self):
        ##  read enable status
        self.get_enable_status()
        self.read_enable_status()
        #print(datetime.datetime.today(), guard.current_enable_status)

        if self.current_enable_status != self.previous_enable_status:
            return True
        return False




if __name__ == "__main__":

    testing_mode = False
    sleep_time = 600

    bot = telebot.TeleBot(config.token) #, parse_mode=None)
    guard = SIT_guard(testing_mode=testing_mode)

    while True:
        ##  if enable status changed
        if guard.enable_status_changed():
            text = f"{guard.previous_enable_status} -> {guard.current_enable_status}"
            guard.send_info(text)

            ##  get tuzik status and print to bot
            guard.get_status()
            guard.read_status()
            guard.send_status()

        ##  if current operation status changed, print it
        if guard.operation_status_changed():
            text = f"{guard.current_operation_status}"
            guard.send_info(text)

        ##  in Enable mode sleep time is
        if "nable" in guard.current_enable_status: ## Enable
            sleep_time = 120  ## Enable
        else:
            sleep_time = 600  ## Disable

        time.sleep(sleep_time)
