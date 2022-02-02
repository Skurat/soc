import socketserver
import time
import json
from multiprocessing.dummy import Pool as ThreadPool
import re
import socket
import requests
from subprocess import call
from threading import Thread
#######################################################################
### Показывает начало работы сканера   ################################
#######################################################################
print ("Pot is runnig:")
#######################################################################
### Описание наличия обязательных полей в заголовках запросов		###
### которые считаются нормальными ( при подключении по ssh или вход	###
### вход на сайт через браузер )									###
#######################################################################
port_rule = {
'80': ['http'],
'443': ['http'],
'10022': ['ssh'],
'22': ['ssh']
}
########################################################################
#####################    Блок с переменными      #######################
########################################################################
#### 1 - Путь к лог файлу ( для дальнейшей работы с логами )
#### 2 - Токен бота
#### 3 - ID чата
#### 4 - Список, в который будут попадать IP , которые не попадают под правила в словаре ~ port_rule
#### 5 - Счетчик количества подключений на порты
#### 6 - Флаг для счетчика
########################################################################
_log_file_path = "./logs/honeypot.log"
_log_name = "honeypot.log"
_log_path = "./logs/"
bot_token = "1152814326:AAGogWDwfYrFn2Dper28FlXrUJ2edgHQBjg"
chat_id = -1001346651043
_wait_second = 5
ip_connect = {}
all_ports = {'80': 'http', '443': 'http', '22':'ssh', '10022': 'ssh'}
bad_connect = {}
bad_connect = { port: {
    'port_num': str (port),
    'counter': int (0),
    'rule': all_ports[port],
    'ip': {},
    'waiting': bool (False)
} for port in all_ports}
conn_counter = {'80': int (0), '443': int (0), '22': int (0), '10022': int (0)}
waiting = {'80': bool (False), '443': bool (False), '22': bool (False), '10022': bool (False)}
########################################################################
class LoggingHack:
    def write_to_log (data_to_log):
        data = ''
        with open (_log_file_path) as f:
            data = json.load (f)
        data.append(data_to_log)
        with open (_log_file_path, "w") as f:
            json.dump (data, f)
        time.sleep (1)
        
def getNameViaIp (ip):
    import pyodbc
    server = 'tcp:rishi-jangoha.pup.local' 
    database = 'posipaki' 
    username = ''
    password = ''
    driver = 'ODBC Driver 17 for SQL Server'
    cnxn = pyodbc.connect('DRIVER={' + driver + '};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    query = "SELECT [name_PC] FROM [posipaki].[dbo].[ip_computers] WHERE [ip_PC]='{}'".format (ip)
    try:
        res = cursor.execute (query).fetchone ()[0]
    except:
        res = False
    return res

def sendMessage (message, bot_token, chat_id):
    text=message
    url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage'
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "html"
    }
    requests.get (url=url, data=data)

def sendMail (message):
    import smtplib
    from email.mime.text import MIMEText
    me = 'alert_security@rozetka.com.ua'
    you = 'alert_security@rozetka.com.ua'
    smtp_server = 'mail.rozetka.com.ua'
    msg = MIMEText(str (message))
    msg['Subject'] = 'Scanner\'s alert!'
    msg['From'] = me
    msg['To'] = you
    s = smtplib.SMTP(smtp_server)
    s.sendmail(me, [you], msg.as_string())
    s.quit()
########################################################################
class MyTCPHandler(socketserver.BaseRequestHandler):
########################################################################
################    Метод записи в лог файл      #######################
########################################################################
    def write_to_log (self, log):
        from datetime import datetime
        import os
        _today_log_name = "{}{}-{}".format(_log_path, _log_name, datetime.now ().strftime ("%d-%b-%Y"))
        if not os.path.exists (_log_path):
            os.makedirs (_log_path)
            with open (_today_log_name ,"w") as f:
               f.write ("")
        now = datetime.now ().strftime ("%d/%b/%Y:%H:%M:%S")
        log = "[{}] \"action: {}\" \n".format (now, log)
        with open (_today_log_name, "a") as f:
            f.write (log)
###########################################################################################################################
#############################    Метод который ожидает N секунд, и считает    #############################################
#############################    кол-во подключений на сокет                  #############################################
###########################################################################################################################
    def conn_timer (self, **arg):
        message = ''
        global conn_counter
        global waiting
        global ip_connect
        global bad_connect
        port = arg['port']
        dest_ip = arg['dest_ip']
        src_ip = arg['src_ip']
        data = arg['data']
        print ('START counter on port {}'.format (port))
        time.sleep (_wait_second)
        if bad_connect[port]['counter'] >= 1:
            message = "{} requests without right header to {}:{} (name: {}) in {} seconds\nDetails:\n {}\n".format (
                bad_connect[port]['counter'],
                dest_ip,
                port,
                getNameViaIp (dest_ip) if getNameViaIp (dest_ip) else 'None',
                _wait_second,
                ["{} name: {} {} times".format (ip_count, getNameViaIp(ip_count) if getNameViaIp(ip_count) else 'None', bad_connect[port]['ip'][ip_count]) for ip_count in bad_connect[port]['ip']]
            )
            self.write_to_log (message)
            sendMessage (message, bot_token, chat_id)
            sendMail (message)
            print (message)

        bad_connect[str (port)]['waiting'] = False
        bad_connect[str (port)]['counter'] = int (0)
        bad_connect[str (port)]['ip'] = {}
        waiting[str (port)] = False
        ip_connect = {}
        conn_counter[str (port)] = int (0)
        print ('END counter on port {}'.format (port))
###########################################################################################################################
####################    Метод который строит понятное сообщение для отправки в канал(ы) связи     #########################
###########################################################################################################################
### Флаг, для проверки нужно ли записывать запрос в список "нелегальных" подключений
### Преобразует строку с данными
### 	в переменную DEST_PORT куда идет подключение
### 		в переменную DEST_IP куда идет подключение
### 			и переменную SRC_IP откуда идет подключение
### Выводит понятную строку какой IP куда пытался подключиться
###########################################################################################################################
    def struct_data(self, request, data = '', exeption = 0):
        flag = 0
        dest_data = re.search ("laddr\=\('(([0-9]{1,3}\.){3}[0-9]{1,3})'\,\s([0-9]{1,5})\)", request, flags=re.DOTALL)
        dest_port = dest_data.group (3)
        dest_ip = dest_data.group (1)
        src_ip = self.client_address[0]
        print ('Ip {} try connect by port {} '.format (src_ip, dest_port))
###########################################################################################################################
### Словарь который потом заполняется и записывается в лог файл
        log_obj = {
            'dest_ip': dest_ip,
            'src_ip': src_ip,
            'dest_port': dest_port,
            'data': data,
            'hack_target': 0,
            'exeption': 0
        }
###########################################################################################################################
### Если порт, на который идет подключение есть в списке правил
###		проходим по списку правил
### 		проверяем есть ли текст правила в строке заголовка
### Если текст и правило совпали, ставим флаг 1
###########################################################################################################################
        if bad_connect[dest_port]:
            if bad_connect[dest_port]['rule'].lower () in data.lower ():
                flag = 1
###########################################################################################################################
### Если правила в тексте заголовка нет
### Производим инкрементную запись в щетчик по ключу SRC_IP
###	Если нету такого ключа, присваеваем ключ со значением 1
### Если счетчик подключения с указанным портом есть добавляем +1
### Если нету добавляем в счетчик  +1 (по умолчанию счетчик равен 0) в список ожидания добавляем порт и флаг TRUE
### Создает переменную, которая будет ссылкой на вызов метода который будет считать N секунд, и собирать кол-во подключений на сокет
###	Запускает отдельный процесс который будет считать N секунд, и собирать кол-во подключений на сокет
###########################################################################################################################
        if not flag:
            if not bad_connect[dest_port]['waiting']:
                bad_connect[dest_port]['waiting'] = True
                bad_connect[dest_port]['ip'][src_ip] = 0
                taimer = Thread (target=self.conn_timer,kwargs={'port': dest_port, 'dest_ip': dest_ip, 'src_ip': src_ip, 'data': data})
                taimer.start ()
            bad_connect[dest_port]['counter'] += 1
            bad_connect[dest_port]['ip'][src_ip] += 1

###########################################################################################################################
################################    			Метод вызываемый при         				###############################
################################    			запросе на указанный IP      				###############################
################################    			с заданным портом            				###############################
###########################################################################################################################
### В блоке try пытаемся присвоить в переменную data строку , если он есть
### Передаем data в метод struct_data для структурирования данных
### Если нету данных в request, передаем пустую строку в метод struct_data
###########################################################################################################################
    def handle(self):
        request = str (self.request)
        try:
            self.data = str (self.request.recv(1024).strip())
            self.struct_data (request, self.data)
        except ConnectionResetError:
            self.struct_data (request)
###########################################################################################################################
### Список портов, которые нужно прослушивать
### Количество вызываемых потоков для прослушки
### HOST=IP интерфейса, который нужно слушать
### Запуск сервера с указанным IP и портом
### Запуск метода multi с аргуменом port по количеству потоков pool
###########################################################################################################################
ports = [int (port) for port in bad_connect]
def get_ip () -> str:
    s = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
    s.connect (("10.0.3.135",53))
    ip = s.getsockname ()[0]
    return ip

pool = ThreadPool (len (ports))
def multi (port):
    HOST = get_ip ()
    socketserver.TCPServer((HOST, port), MyTCPHandler).serve_forever()
results = pool.map (multi, ports)
###########################################################################################################################
pool.close ()
pool.join ()
