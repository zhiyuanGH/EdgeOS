import networkx
import networkx as nx;
from networkx.readwrite import json_graph
from matplotlib import pyplot as plt
import json
import sys


class Parser:

    def __init__(self,location):
        self.file_location=location
        self.flow_list=[]
        self.node_red_profile=[]
        self.DiGraph=nx.DiGraph()

    def get_node_red_profile(self):
        file=open(self.file_location)
        profile_str=file.read()
        file.close()
        profile_json=json.loads(profile_str)
        self.node_red_profile=profile_json


    def get_graph_node(self):
        for node in self.node_red_profile:
            if(node['type']=='tab'):
                self.DiGraph.add_node(node['label'])

    def sava_digraph(self):
        graph_data=json_graph.node_link_data(self.DiGraph)
        graph_data_json=json.dumps(graph_data)
        file=open('./digraph.json','w+')
        file.write(graph_data_json)

    def parse(self):
        self.get_node_red_profile()
        self.get_graph_node()
        for flow in self.node_red_profile:
            if flow['type'] == 'tab':
                next_flow_list=json.loads(flow['info'])
                for next_flow in next_flow_list:
                    if len(next_flow['next'])>0:
                        self.DiGraph.add_edges_from([(flow['label'], next_flow['next'])])
        nx.draw_networkx(self.DiGraph)
        plt.show()
        self.sava_digraph()




if __name__=="__main__":
    node_red_parser=Parser('./hellodemo.json')
    node_red_parser.parse()

