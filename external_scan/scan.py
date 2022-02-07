#!/usr/bin/python3
from datetime import datetime
import os
import subprocess
import logging
BOT_TOKEN="871783617:AAFcIkJ-Yytvq7IVxQkBbKAKPdDGoarve7U"
CHAT_ID="300576657"
OPTIONS="-T4 -p3306"
DATE=datetime.now ().strftime ('%Y-%m-%d %H:%M')
TARGET_FILE="targets"
LOG_FILE="response.log"
os.system ("apt install ndiff -y")
# FILE="scan-current"
# COMPARE_FILE="compare-file"
FOR_SED=["/Nmap/d", "/Not shown/d", "/SERVICE/d", "s/^+/%2b\ /g", "s/^-/\-\ \ /g"]
logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def MAKE_SYS_CMD (CMD):
    os.system (CMD)
TARGET_IPS = list ()
with open (TARGET_FILE) as f:
    TARGET_IPS = [line.rstrip('\n') for line in f]
for TARGET_IP in TARGET_IPS:
    print (f'START SCANNING {TARGET_IP}')
    ROOT_PATH = f"./scan_res/{TARGET_IP}/"
    if not os.path.isdir (ROOT_PATH):
        os.makedirs (ROOT_PATH)
    FILE=f"{ROOT_PATH}/scan-current"
    COMPARE_FILE=f"{ROOT_PATH}/compare-file"

    MAKE_SYS_CMD (f"nmap {OPTIONS} {TARGET_IP} -oA {FILE} > /dev/null")
    if os.path.isfile (f"{COMPARE_FILE}.xml"):
        MAKE_SYS_CMD (f"ndiff {COMPARE_FILE}.xml {FILE}.xml > {ROOT_PATH}diff")
        for sed in FOR_SED:
            MAKE_SYS_CMD (f"sed -i '{sed}' {ROOT_PATH}diff")
        with open (f'{ROOT_PATH}diff', 'r') as f:
            TEXT  = f.read ()
        if TEXT:
            RESP_CODE = str (subprocess.check_output (["curl","-d",f"text={TEXT}&chat_id={CHAT_ID}","--silent","-i","-o","-","-X","POST",f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"]))
            logging.info (f"Status code of send to telegram is {' '.join (RESP_CODE.split (' ')[0:2])}")
        pass
    else:
        logging.info ("FILE WAS CREATE")
        MAKE_SYS_CMD (f"cp {FILE}.xml {COMPARE_FILE}.xml")