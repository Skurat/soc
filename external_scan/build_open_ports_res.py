#!/usr/bin/env python3
from os import listdir
import re
from pprint import pprint
import json

res_dir = "/var/www/external_scan/scan_results"
ls_dirs = listdir (res_dir)

ips_list = list ()
for ls_dir in ls_dirs:
	ips_dict = dict ()
	port_state = list ()
	dir_with_file = f"{res_dir}/{ls_dir}"
	file = f"{dir_with_file}/1-scan-current.nmap"
	with open (file, "r") as f:
		tmp_value = f.read ()
#		comp_value = re.findall ("^Nmap.*for\s([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*)|\(([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*)\)|(\d+\/\w+.*open.*)", tmp_value)
		comp_value = re.findall ("(\d+\/\w+.*open.*)", tmp_value)
		if comp_value:
			ip = ls_dir
			port_state = list ()
			for index, port_res in enumerate (comp_value):
				port, state, service = port_res.split()
				port_state.append({'port': port,'state': state,'service': service})
			
	ips_dict[ls_dir] = port_state
	ips_list.append (ips_dict)
pprint (type (ips_list))
temp_var = json.dumps (ips_list)
pprint (type (temp_var))
with open ("/var/www/external_scan/web/all_info.txt", "w") as f:
#    f.write (temp_var)
	json.dump (ips_list, f)
