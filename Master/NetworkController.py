import json
import requests

import pickle
import socket
import struct
import threading

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

routing_list = {"IP_table": ["192.168.1.104", "192.168.1.101", "192.168.1.105"]}

def customize_routing(routing_list):
	config_json = json.dumps(routing_list)
	routing_list_json = json.loads(config_json)
	print(routing_list_json)
	node_ip = routing_list_json["IP_table"]
	for ip in node_ip:
		url = "http://" + ip + ":5000/route"
		respone = requests.post(url=url, json=routing_list_json)


#customize_routing(routing_list)


#transfer the out_data to next hop
def offload_to_peer(next_task_num, next_task_args, client_socket):
	send_data = b''
	next_arg_data = []

	if next_task_args is not None:
		if type(next_task_args) is tuple:
			for arg in next_task_args:
				next_arg_data.append(arg)
		else:
			next_arg_data.append(next_task_args)

	# Send number of args
	send_data += struct.pack("L", len(next_arg_data))

	# Send the next task's number
	send_data += struct.pack("L", next_task_num)

	if len(next_arg_data) > 0:
		for next_arg in next_arg_data:
			data = pickle.dumps(next_arg)
			arg_size = struct.pack("L", len(data))
			send_data += arg_size
			send_data += data

	client_socket.sendall(send_data)



#listen and receive the data from the previous hop
def server_socket(s,next_client,task_id_list):

	while True:
		print('Waiting for client to connect')

		# Receive connection from client
		client_socket, (client_ip, client_port) = s.accept()
		print('Received connection from:', client_ip, client_port)

		# Start a new thread for the client. Use daemon threads to make exiting the server easier
		# Set a unique name to display all images
		t = threading.Thread(target=server_task, args=[client_socket, next_client, task_id_list], daemon=True)
		t.setName(str(client_ip) + ':' + str(client_port))
		t.start()
		print('Started thread with name:', t.getName())


def server_task(conn,next_client, task_id_list):
	data = b''
	payload_size = struct.calcsize("L")

	try:
		while True:
			# Reset args list every loop
			next_task_args_list = []

			# Retrieve number of args for next task
			while len(data) < payload_size:
				data += conn.recv(4096)

			packed_num_next_task_args = data[:payload_size]
			data = data[payload_size:]
			num_next_task_args = struct.unpack("L", packed_num_next_task_args)[0]

			# Retrieve the next task index
			while len(data) < payload_size:
				data += conn.recv(4096)

			packed_next_task_num = data[:payload_size]
			data = data[payload_size:]
			next_task_num = struct.unpack("L", packed_next_task_num)[0]

			# Retrieve all args per task
			for i in range(num_next_task_args):
				# Retrieve each argument size
				while len(data) < payload_size:
					data += conn.recv(4096)
				packed_argsize = data[:payload_size]
				data = data[payload_size:]
				argsize = struct.unpack("L", packed_argsize)[0]

				# Retrieve data based on arg size
				while len(data) < argsize:
					data += conn.recv(4096)

				next_arg_data = data[:argsize]
				data = data[argsize:]
				# Extract next arg
				next_arg = pickle.loads(next_arg_data)

				next_task_args_list.append(next_arg)

			# Set variables and args for running tasks
			next_task_run_index = next_task_num
			if len(next_task_args_list) == 0:
				# No args to pass
				next_task_args = None
			elif len(next_task_args_list) == 1:
				next_task_args = next_task_args_list[0]
			else:
				next_task_args = tuple(next_task_args_list)

			
			while next_task_run_index <= task_id_list[-1]:
				task = tasks[next_task_run_index]
				to_continue, next_task_args = run_task(task_func=task,
													   args=next_task_args)

				if to_continue is False or next_task_run_index == (len(tasks) - 1):
					# Done with this message, get next message by breaking out of loop
					break

				# Still working on this message, increment task num
				next_task_run_index += 1

			if to_continue is not False and next_client:
				offload_to_peer(next_task_num=next_task_run_index,
								next_task_args=next_task_args,
								client_socket=next_client)


	except ConnectionResetError:
		# Client disconnected
		print('Client disconnected')
		conn.close()




#limit the bandwidth of data transfering
bandwidth = {
			"task_id": "0 1 2", 
			"source_ip": "192.168.1.104", 
			"source_ip_port": 8089, 
			"next_hop": "192.168.1.104", 
			"next_hop_port": 8089, 
			"bandwidth": "", 
			"routing": ""
			}

def limit_bandwidth(bandwidth):
	bandwidth_json = json.dumps(bandwidth)
	limit_bandwidth_json = json.loads(bandwidth_json)
	print(limit_bandwidth_json)

	node_ip = limit_bandwidth_json["source_ip"]
	url = "http://" + node_ip + ":5000/bandwidth"
	respone = requests.post(url=url, json=limit_bandwidth_json)

