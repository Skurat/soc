from pprint import pprint
import json
import time

class LoggingHack:
    def write_to_log (data_to_log):
        data = ''
        with open ("logs/honeypot.json") as f:
            data = json.load (f)
        data.append(data_to_log)
        with open ("logs/honeypot.json", "w") as f:
            json.dump (data, f)
        time.sleep (1)