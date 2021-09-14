# import json
# import os
# import subprocess as sp
# import time
# import socket

# import requests
# from flask import Flask, request


# config = {"IP": ["192.168.1.103", "192.168.1.105", "192.168.1.107", "192.168.1.102", "192.168.1.116"],
# "bw": [["inf", "4969kbps", "2096kbps", "3326kbps", "inf"],
# ["3656kbps", "inf", "4091kbps", "None", "3971kbps"],
# ["2996kbps", "3368kbps", "inf", "2683kbps", "None"],
# ["3195kbps", "None", "4131kbps", "inf", "2295kbps"],
# ["2395kbps", "4280kbps", "None", "3648kbps", "inf"]]}

# config_json = json.dumps(config)
# print(config_json)

# def get_host_ip():
#     """
#     查询本机ip地址
#     :return: ip
#     """
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(('8.8.8.8', 80))
#         ip = s.getsockname()[0]
#     finally:
#         s.close()

#     return ip

# def configure(cmd):
# 	for c in cmd:
# 		p = sp.Popen (c, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
# 		print (p.communicate () [0].decode ())
# 		print ('if no error printed, then successfully limited the bw to device')



# def test():
# 	tc_json = json.loads(config_json)
# 	tc_ip = tc_json["IP"]
# 	tc_bw = tc_json["bw"]
# 	print(tc_ip)
# 	print(tc_bw[0][0])

# 	local_ip = get_host_ip()
# 	order = tc_ip.index(local_ip)
# 	conf = tc_bw[order]
# 	cmd = []
# 	cmd.append('sudo tc qdisc add dev enp4s0 root handle 1: htb default 1')
# 	for i in range(len(conf)):
# 		ip = tc_ip[i]
# 		bw = conf[i]
# 		if bw != 'inf':
# 			cmd.append('sudo tc class add dev enp4s0 parent 1:1 classid ' + '1:%d htb rate %s ceil %s burst 15k' % (i+10, bw, bw))
# 			cmd.append('sudo tc filter add dev enp4s0 protocol ip parent 1: prio 2 u32 match ip dst ' + '%s/32 flowid 1:%d' % (ip, i+10))
# 	print(cmd)
# 	configure(cmd)


# test()
# def device_conf_listener():
# 	app = Flask (__name__)

# 	@app.route ('/tcConf', methods=['POST'])
# 	def route_tc_conf ():
# 		data = request.form


# def open_cam_rtsp(uri, width, height, latency):
# 	gst_str = ('rtspsrc location={} latency={} ! '
# 			   'rtph264depay ! h264parse ! omxh264dec ! '
# 			   'nvvidconv ! '
# 			   'video/x-raw, width=(int){}, height=(int){}, '
# 			   'format=(string)BGRx ! '
# 			   'videoconvert ! appsink').format(uri, latency, width, height)
# 	return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)


# def test_bandwidth():
# 	uri = "rtsp://admin:edge1234@192.168.1.106:554/cam/realmonitor?channel=1&subtype=0"
# 	t1 = time.time()
# 	cap = open_cam_rtsp(uri, 640, 480, 200)
# 	t2 = time.time()
# 	print ("capture video consumes", t2-t1)


# 	if not cap.isOpened():
# 		sys.exit('Failed to open camera!')

# 	counter=0

# 	while (cap.isOpened()):
# 		counter+=1
		
# 		if counter % 5 != 0:
# 			t1 = time.time()
# 			ret, frame = cap.read()
# 			t2 = time.time()
# 			print ("read one frame consumes", t2-t1)
# 			continue

# 		if counter == 200:
# 			break

# test_bandwidth()

A到B，B到C，C到D，并且跟踪路由 
at A, set the route destination (D) and gateway (B) sudo route add -host 192.168.1.114 gw 192.168.1.102
at B, set the route destination (D) and gateway (C) enable the ip_forward echo "1" > /proc/sys/net/ipv4/ip_forward sudo route add -host 192.168.1.114 gw 192.168.1.107
at C, enable the ip_forward   echo "1" > /proc/sys/net/ipv4/ip_forward


def customize_routing(routing_path_list):
	'''
	input: the routing path consists of ip address of edge devices
	to configure the routing path among edge devices
	'''
	local_ip = get_host_ip()
	order = routing_path_list.index(local_ip)

	if order == 0:
		cmd = 'sudo route add -host ' + routing_path_list[-1] + ' gw ' + routing_path_list[order+1]
		p = sp.Popen (cmd, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
		print (p.communicate () [0].decode ())
		print ('if no error printed, then successfully configure next hop')
		return 0
	if order == len(routing_path_list) - 1:
		return 0
	if order == len(routing_path_list) - 2:
		#ip_forwarding
		cmd = 'echo "1" > /proc/sys/net/ipv4/ip_forward'
		p = sp.Popen (cmd, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
		print (p.communicate () [0].decode ())
		print ('if no error printed, then successfully configure ip_forward')
		return 0

	cmd1 = 'echo "1" > /proc/sys/net/ipv4/ip_forward'
	cmd2 = 'sudo route add -host ' + routing_path_list[-1] + ' gw ' + routing_path_list[order+1]
	cmd = cmd1 + ' && ' + cmd2
	p = sp.Popen (cmd, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)

	return 0








