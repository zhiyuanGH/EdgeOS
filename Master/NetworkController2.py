import json
import requests

import pickle
import socket
import struct
import threading
import sys
from ball_tracking_example.taskified import tasks

'''
config = {"IP": ["192.168.1.104", "192.168.1.101", "192.168.1.105", "192.168.1.102"],
"bw": [["inf", "4969kbps", "inf", "inf"],
["4969kbps", "inf", "4091kbps", "1024kbps"],
["2996kbps", "3368kbps", "inf", "4969bps"],
["3195kbps", "inf", "4131kbps", "inf"]]}

config_json = json.dumps(config)

def configure_bandwidth():
	tc_json = json.loads(config_json)
	node_ip = tc_json["IP"]
	for ip in node_ip:
		url = "http://" + ip + ":5009/tcConf"
		respone = requests.post(url=url, json=tc_json)
		break


configure_bandwidth()

routing_list = {"IP_table": ["192.168.1.101", "192.168.1.105", "192.168.1.102"]}

def customize_routing(routing_list):
	config_json = json.dumps(routing_list)
	routing_list_json = json.loads(config_json)
	print(routing_list_json)
	node_ip = routing_list_json["IP_table"]
	for ip in node_ip:
		url = "http://" + ip + ":5009/route"
		respone = requests.post(url=url, json=routing_list_json)


#customize_routing(routing_list)

'''



'''
#limit the bandwidth of data transfering
bandwidth = {
			"task_id": "0 1 2", 
			"source_ip": "192.168.1.104", 
			"source_ip_port": 8089, 
			"next_hop": "192.168.1.105", 
			"next_hop_port": 8089, 
			"bandwidth": "10Mbit", 
			"routing": ""
			}

def limit_bandwidth(bandwidth):
	bandwidth_json = json.dumps(bandwidth)
	limit_bandwidth_json = json.loads(bandwidth_json)
	print(limit_bandwidth_json)

	node_ip = limit_bandwidth_json["source_ip"]
	url = "http://" + node_ip + ":5009/bandwidth"
	respone = requests.post(url=url, json=limit_bandwidth_json)

#limit_bandwidth(bandwidth)
'''

