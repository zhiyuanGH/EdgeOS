'''
input
 -task definition, which tasks the container should run
 -the offloading device

To run the task with the input configuration
'''
import pickle
import socket
import struct
import threading
import sys

from ball_tracking_example.tasktest import tasks
from multiprocessing import Pool
#from NetworkController import offload_to_peer, server_socket, run_task


def run_task(task_func, args):
	#emulate_iot_device()

	# Call task
	if args is None:
		# No args to pass
		return task_func()
	elif type(args) is tuple:
		# Unzip tuple into args
		return task_func(*args)
	else:
		# Single arg
		return task_func(args)

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


def offload_to_peers(next_task_num, next_task_args, client_sockets):
	#use multiple process to transmit the args
	p = Pool(3)
	for client_socket in client_sockets:
		p.apply_async(offload_to_peer, args=(next_task_num, num_next_task_args, client_socket))
	print("all sending subprocess starts")
	p.close()
	p.join()
	



#listen and receive the data from the previous hop
def server_socket(s,previous_hops,next_clients,lock, task_id_list):

	while True:
		print('Waiting for client to connect')

		# Receive connection from client
		client_socket, (client_ip, client_port) = s.accept()
		print('Received connection from:', client_ip, client_port)

		# Start a new thread for the client. Use daemon threads to make exiting the server easier
		# Set a unique name to display all images
		t = threading.Thread(target=server_task, args=[client_port, client_socket, previous_hops, next_clients, lock, task_id_list], daemon=True)
		t.setName(str(client_ip) + ':' + str(client_port))
		t.start()
		print('Started thread with name:', t.getName())


def server_task(client_port, conn, previous_hops, next_clients, lock, task_id_list):
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

			#aggregate the args from the clients
			if len(previous_hops) == 1:
				#no need to aggregate			
				while next_task_run_index <= task_id_list[-1]:
					task = tasks[next_task_run_index]
					to_continue, next_task_args = run_task(task_func=task,
														   args=next_task_args)

					if to_continue is False or next_task_run_index == (len(tasks) - 1):
						# Done with this message, get next message by breaking out of loop
						break

					# Still working on this message, increment task num
					next_task_run_index += 1

				if to_continue is not False and next_clients:
					#transmit to one or multiple clients
					offload_to_peers(next_task_num=next_task_run_index,
									next_task_args=next_task_args,
									client_socket=next_clients)
			else:
				#multiple clients send the parameters, aggregate the parameters
				lock.acquire()
				global args_dict

				if client_port in previous_hops:
					args_dict[client_port].append(next_task_args)

				count = 0
				arg_group = ()
				for key, value in args_dict.items():
					if value:
						arg_group += value[0]
						count += 1

				if count == len(previous_hops):
					#pop the first element 
					for key, value in args_dict.items():
						del value[0]

					lock.release()

					next_task_args = arg_group
					#send the parameters

					while next_task_run_index <= task_id_list[-1]:
						task = tasks[next_task_run_index]
						to_continue, next_task_args = run_task(task_func=task,
															   args=next_task_args)

						if to_continue is False or next_task_run_index == (len(tasks) - 1):
							# Done with this message, get next message by breaking out of loop
							break

						# Still working on this message, increment task num
						next_task_run_index += 1

					if to_continue is not False and next_clients:
						#transmit to one or multiple clients
						offload_to_peers(next_task_num=next_task_run_index,
										next_task_args=next_task_args,
										client_socket=next_clients)




	except ConnectionResetError:
		# Client disconnected
		print('Client disconnected')
		conn.close()



def main(previous_hops, HOST_PORT, next_hops, next_hop_ports, task_id_list):
	#previous_hops, HOST_PORT, next_hops, next_hop_ports, task_id_list

	if next_hops:
		#establish next hop connection
		client_sockets = []
		for (next_hop, next_hop_port) in (next_hops, next_hop_ports):
			client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client_socket.connect((next_hop, next_hop_port))

			client_sockets.append(client_socket)

	else:
		client_sockets = None

	if previous_hops:
		for ip in previous_hops:
			args_dict[ip] = []

		lock = threading.Lock()

		#establish previous hop connection and listen, run the assigned task and offload the task to next_hop
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print('Socket created')

		server.bind((HOST, HOST_PORT))
		print('Socket bind complete')
		server.listen(10)
		print('Socket now listening on port', HOST_PORT)

		server_socket(s=server, previous_hops=previous_hops, next_client=client_sockets, lock=lock, task_id_list=task_id_list)

	else:
		# Variables for task state
		task_index = 0
		# Init tasks args
		next_task_args = None

		# Keep running tasks in sequential order
		while True:

			# Determine which task to run
			task = tasks[task_index]

			# Run task
			to_continue, next_task_args = run_task(task_func=task,
												   args=next_task_args)

			# No need to continue running tasks, end of stream
			if to_continue is False and task_index == 0:
				for client_socket in client_sockets:
					client_socket.close()
				break

			# Increment index (cyclical)
			task_index += 1

			# Reset to first frame if more function calls are not needed
			# or reached end of sequence
			if to_continue is False or task_index >= len(task_id_list):

				if to_continue is not False and client_sockets is not None:
					# Send frame to peer server
					offload_to_peer(next_task_num=task_index,
									next_task_args=next_task_args,
									client_socket=client_sockets)

				# Reset vars
				task_index = 0
				next_task_args = None
				continue


	
def parse_args():

	# Parse previous hop 1/0
	para_1 = str(sys.argv[1])
	print(para_1)
	if para_1 == ' ':
		previous_hops = False
	else:
		#previous_hops = para_1.split()
		previous_hops = list(map(int, para_1.split()))

	#parse localhost port
	para_2 = str(sys.argv[2])
	if para_2 == ' ':
		HOST_PORT = False
	else:
		HOST_PORT = int(para_2)

	# Parse next hop ip_address
	para_3 = str(sys.argv[3])
	if para_3 == ' ':
		next_hop = False
	else:
		next_hop = para_3.split()

	#parse next hop port
	para_4 = str(sys.argv[4])
	if para_4 == ' ':
		next_hop_port = False
	else:
		next_hop_port = list(map(int, para_4.split()))

	# Parse task_id_list  '0 1 2 3' -- [0 1 2 3]
	para_5 = str(sys.argv[5])
	list1=list(para_5.split())
	task_id_list=list(map(int,list1))

	return previous_hops, HOST_PORT, next_hops, next_hop_ports, task_id_list


args_dict = {}

HOST = 'localhost'
#HOST_PORT = 8089

#previous_hop = False
#next_hop = 'localhost'
#next_hop_port = 8089
#task_id_list = [0,1,2]

if __name__ == '__main__':
	previous_hops, HOST_PORT, next_hops, next_hop_ports, task_id_list = parse_args()
	print(previous_hops, HOST_PORT, next_hops, next_hop_ports, task_id_list)
	main(previous_hops, HOST_PORT, next_hops, next_hop_ports, task_id_list)





