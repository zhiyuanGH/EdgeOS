import json

#parse the input json

#profile the application (latency, energy consumption, .etc), can be done offline

#get network topology and bandwidth

#get edge nodes CPU, Memory, GPU status

#user customized algorithms

#dynamically generate the execution file and policies
#execution configuration
conf = 	{
			"sub_task_1": {
				"task_id": "0", 
				"source_ip": "192.168.1.104", 
				"source_ip_port": 8089, 
				"next_hop": "192.168.1.104", 
				"next_hop_port": 8089, 
				"bandwidth": "", 
				"routing": ""},

			"sub_task_2": {
				"task_id": "1", 
				"source_ip": "192.168.1.104", 
				"source_ip_port": 8089, 
				"next_hop": "192.168.1.102", 
				"next_hop_port": 8089, 
				"bandwidth": "", 
				"routing": ""},

			"sub_task_3": {
				"task_id": "2 3", 
				"source_ip": "192.168.1.104", 
				"source_ip_port": 8089, 
				"next_hop": "192.168.1.104", 
				"next_hop_port": 8089, 
				"bandwidth": "", 
				"routing": ""},

			"sub_task_4": {
				"task_id": "4", 
				"source_ip": "192.168.1.104", 
				"source_ip_port": 8089, 
				"next_hop": "192.168.1.104", 
				"next_hop_port": 8089, 
				"bandwidth": "", 
				"routing": ""}
		}



def scheduling():
	'''
	input: node resources, network topology and bandwidth, task progile
	output: the execution configuration
	'''

	return json.loads(conf)