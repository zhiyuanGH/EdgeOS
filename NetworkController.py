import json
import requests

config = {"IP": ["192.168.1.101", "192.168.1.105", "192.168.1.107", "192.168.1.102", "192.168.1.116"],
"bw": [["inf", "4969kbps", "2096kbps", "3326kbps", "inf"],
["3656kbps", "inf", "4091kbps", "None", "3971kbps"],
["2996kbps", "3368kbps", "inf", "2683kbps", "None"],
["3195kbps", "None", "4131kbps", "inf", "2295kbps"],
["2395kbps", "4280kbps", "None", "3648kbps", "inf"]]}

config_json = json.dumps(config)

def configure_bandwidth():
	tc_json = json.loads(config_json)
	node_ip = tc_json["IP"]
	for ip in node_ip:
		url = "http://" + ip + ":5000/tcConf"
		respone = requests.post(url=url, json=tc_json)
		break

#configure_bandwidth()

routing_list = {"IP_table": ["192.168.1.104", "192.168.1.101", "192.168.1.105"]}

def customize_routing(routing_list):
	config_json = json.dumps(routing_list)
	routing_list_json = json.loads(config_json)
	print(routing_list_json)
	node_ip = routing_list_json["IP_table"]
	for ip in node_ip:
		url = "http://" + ip + ":5000/route"
		respone = requests.post(url=url, json=routing_list_json)


customize_routing(routing_list)


#listen and receive the data from the previous hop
def dataListener(previous_hop):
	pass


#transfer the out_data to next hop
def dataTransfer(next_hop, output_data):
	pass




