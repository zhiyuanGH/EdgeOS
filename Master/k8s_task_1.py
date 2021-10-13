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
from NetworkController import offload_to_peer, server_socket



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


def main(previous_hop, HOST_PORT, next_hop, next_hop_port, task_id_list):
	#previous_hop, HOST_PORT, next_hop, next_hop_port, task_id_list

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
		next_hop = para_3

	#parse next hop port
	para_4 = str(sys.argv[4])
	if para_4 == ' ':
		next_hop_port = False
	else:
		next_hop_port = int(para_4)

	# Parse task_id_list  '0 1 2 3' -- [0 1 2 3]
	para_5 = str(sys.argv[5])
	list1=list(para_5.split())
	task_id_list=list(map(int,list1))

	return previous_hop, HOST_PORT, next_hop, next_hop_port, task_id_list

HOST = 'localhost'
#HOST_PORT = 8089

#previous_hop = False
#next_hop = 'localhost'
#next_hop_port = 8089
#task_id_list = [0,1,2]

if __name__ == '__main__':
	previous_hop, HOST_PORT, next_hop, next_hop_port, task_id_list = parse_args()
	print(previous_hop, HOST_PORT, next_hop, next_hop_port, task_id_list)
	main(previous_hop, HOST_PORT, next_hop, next_hop_port, task_id_list)





