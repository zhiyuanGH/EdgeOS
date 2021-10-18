import json
import os
import subprocess as sp
import time
import socket

import requests
from flask import Flask, request


# config = {"IP": ["192.168.1.103", "192.168.1.105", "192.168.1.107", "192.168.1.102", "192.168.1.116"],
# "bw": [["inf", "4969kbps", "2096kbps", "3326kbps", "inf"],
# ["3656kbps", "inf", "4091kbps", "None", "3971kbps"],
# ["2996kbps", "3368kbps", "inf", "2683kbps", "None"],
# ["3195kbps", "None", "4131kbps", "inf", "2295kbps"],
# ["2395kbps", "4280kbps", "None", "3648kbps", "inf"]]}

# config_json = json.dumps(config)
#print(config_json)

def get_host_ip():
    """
    look for the local ip
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

def configure(cmd):
	for c in cmd:
		p = sp.Popen (c, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True).communicate (input=b'edgeimcl\n')
		#print (p.communicate (input=b'edgeimcl\n') [0].decode ())
		print ('if no error printed, then successfully configure the network bandwidth')



def test(config_json):
	#tc_json = json.loads(config_json)
	tc_json = config_json
	tc_ip = tc_json["IP"]
	tc_bw = tc_json["bw"]
	print(tc_ip)
	print(tc_bw[0][0])

	local_ip = get_host_ip()
	order = tc_ip.index(local_ip)
	conf = tc_bw[order]
	cmd = []
	cmd.append('sudo tc qdisc add dev wlan0 root handle 1: htb default 1')
	for i in range(len(conf)):
		ip = tc_ip[i]
		bw = conf[i]
		if bw != 'inf':
			cmd.append('sudo tc class add dev wlan0 parent 1:1 classid ' + '1:%d htb rate %s ceil %s burst 15k' % (i+10, bw, bw))
			cmd.append('sudo tc filter add dev wlan0 protocol ip parent 1: prio 2 u32 match ip dst ' + '%s/32 flowid 1:%d' % (ip, i+10))
	print(cmd)
	configure(cmd)




'''
From A -- B -- C -- D
at A, set the route destination (D) and gateway (B) sudo route add -host 192.168.1.114 gw 192.168.1.102
at B, set the route destination (D) and gateway (C) enable the ip_forward echo "1" > /proc/sys/net/ipv4/ip_forward sudo route add -host 192.168.1.114 gw 192.168.1.107
at C, enable the ip_forward   echo "1" > /proc/sys/net/ipv4/ip_forward
'''

def customize_routing(routing_path_list):
	'''
	input: the routing path consists of ip address of edge devices
	to configure the routing path among edge devices
	'''
	local_ip = get_host_ip()
	order = routing_path_list.index(local_ip)

	if order == 0:
		cmd = 'sudo route add -host ' + routing_path_list[-1] + ' gw ' + routing_path_list[order+1]
		print(cmd)
		p = sp.Popen (cmd, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
		print (p.communicate () [0].decode ())
		print ('if no error printed, then successfully configure next hop')
		return 0

	if order == len(routing_path_list) - 1:
		print("received")
		return 0

	if order == len(routing_path_list) - 2:
		#ip_forwarding, already set permenently
		# cmd = 'echo "1" > /proc/sys/net/ipv4/ip_forward'
		# p = sp.Popen (cmd, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
		# print (p.communicate () [0].decode ())
		# print ('if no error printed, then successfully configure ip_forward')
		print("received")
		return 0

	#cmd1 = 'echo "1" > /proc/sys/net/ipv4/ip_forward'
	cmd2 = 'sudo route add -host ' + routing_path_list[-1] + ' gw ' + routing_path_list[order+1]
	#cmd = cmd1 + ' && ' + cmd2
	# p = sp.Popen (cmd2, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
	# print (p.communicate () [0].decode ())
	# print ('if no error printed, then successfully configure next hop')
	configure(cmd2)

	return 0


def limit_bandwidth(limit_bandwidth_json):
	'''
	limit the bandwidth of data tranfer from a specific port
	input: the json of the bandwidth related parameters
	'''
	cmd = []
	cmd.append('sudo tc qdisc add dev wlan0 root handle 1:2 htb default 1')
	cmd.append('sudo tc class add dev wlan0 parent 1:2 classid 1:1 htb rate %s burst 15k' % (limit_bandwidth_json["bandwidth"]))
	cmd.append('sudo tc class add dev wlan0 parent 1:1 classid 1:10 htb rate %s ceil %s burst 15k' % (limit_bandwidth_json["bandwidth"], limit_bandwidth_json["bandwidth"]))
	cmd.append('sudo tc filter add dev wlan0 protocol ip parent 1:0 prio 1 u32 match ip sport %d 0xffff flowid 1:10' % (limit_bandwidth_json["source_ip_port"]))

	print(cmd)
	configure(cmd)
	



#listen the confiuration and configure the network
def device_conf_listener():
	app = Flask(__name__)

	@app.route('/tcConf', methods=['POST'])
	def route_tc_conf ():
		config_json = request.get_json()
		print(config_json)

		test(config_json)

		return "OK"

	@app.route('/route', methods=['POST'])
	def configure_route():
		routing_list_json = request.get_json()
		print(routing_list_json)
		routing_path_list = routing_list_json["IP_table"]

		customize_routing(routing_path_list)

		return "OK"

	@app.route('/bandwidth', methods=['POST'])
	def configure_bandwidth():
		limit_bandwidth_json = request.get_json()
		print(limit_bandwidth_json)

		limit_bandwidth(limit_bandwidth_json)

		return "OK"

	app.run (host='0.0.0.0', port=5009)

device_conf_listener()








