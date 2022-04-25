#!/usr/bin/env python3
import requests
from pprint import pprint
import re

class GetPorts:
    def __init__ (self, url):
        self.url = url
        self.done_result = dict ()
    
    def get_scan_result (self):
        response = requests.get (self.url)
        if response:
            pared_result = (response.text).replace ("%2b", "+")
            pared_result = list (filter (None, re.split ("\,+\s+", pared_result)))
            return pared_result
    
    def build_done_result (self, result_list):
        for build_dict in result_list:
            local_ip_str,local_port_status = re.split ("\:\s*", build_dict)
            local_port_status = re.findall (r"[\-\+]{1}\ \d{1,5}\/\w+\s{1}\w+\s{1}[\w\-\_]+", local_port_status)
            for local_port_str in local_port_status:
                state, port, status, service = local_port_str.split (" ", 3)
                if not self.done_result.get (local_ip_str): self.done_result[local_ip_str] = {port: {}}
                if not self.done_result[local_ip_str].get (port): self.done_result[local_ip_str][port] = {"port": port, "state": state, "status": status, "service": service}

def main ():
    get_result = GetPorts ("")
    result = get_result.get_scan_result ()
    get_result.build_done_result (result)
    for listing_ip in get_result.done_result:
        for listing_port in get_result.done_result[listing_ip]:
            ip = listing_ip
            port = listing_port
            state = get_result.done_result[listing_ip][listing_port]['state']
            status = get_result.done_result[listing_ip][listing_port]['status']
            service = get_result.done_result[listing_ip][listing_port]['service']
    pprint (get_result.done_result)

if __name__ == "__main__":
    main ()