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

from ball_tracking_example.taskified import tasks



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



def main(previous_hop, next_hop, task_id_list):
	#previous_hop, next_hop, task_id_list

	if next_hop:
		#establish next hop connection
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((next_hop, next_hop_port))

	else:
		client_socket = None

	if previous_hop:
		#establish previous hop connection and listen, run the assigned task and offload the task to next_hop
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print('Socket created')

		server.bind((HOST, HOST_PORT))
		print('Socket bind complete')
		server.listen(10)
		print('Socket now listening on port', HOST_PORT)

		server_socket(s=server, next_client=client_socket, task_id_list=task_id_list)

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
				client_socket.close()
				break

			# Increment index (cyclical)
			task_index += 1

			# Reset to first frame if more function calls are not needed
			# or reached end of sequence
			if to_continue is False or task_index >= len(task_id_list):

				if to_continue is not False and client_socket is not None:
					# Send frame to peer server
					offload_to_peer(next_task_num=task_index,
									next_task_args=next_task_args,
									client_socket=client_socket)

				# Reset vars
				task_index = 0
				next_task_args = None
				continue
		
def parse_args():

	# Parse previous hop 1/0
	para_1 = int(sys.argv[1])
	if para_1 == 1:
		previous_hop = True
	if para_1 == 0:
		previous_hop = False

	# Parse next hop ip_address
	para_2 = str(sys.argv[2])
	if para_2 == ' ':
		next_hop = False
	else:
		next_hop = para_2

	# Parse task_id_list  '0 1 2 3' -- [0 1 2 3]
	para_3 = str(sys.argv[3])
	list1=list(para_3.split())
	task_id_list=list(map(int,list1))

	return previous_hop, next_hop, task_id_list

HOST = 'localhost'
HOST_PORT = 8089

#previous_hop = True
#next_hop = False
next_hop_port = False
#task_id_list = [5,6]

if __name__ == '__main__':
	previous_hop, next_hop, task_id_list = parse_args()
	print(previous_hop, next_hop, task_id_list)
	main(previous_hop, next_hop, task_id_list)





