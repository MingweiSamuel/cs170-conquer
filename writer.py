import networkx as nx
import gen
import random
import re
from networkx.utils import pairwise

import skeleton.utils as utils
import skeleton.student_utils_sp18 as s_utils

def readGraphFile(name):
    input_data = utils.read_file(name)
    number_of_kingdoms, list_of_kingdom_names, starting_kingdom, adjacency_matrix = s_utils.data_parser(input_data)
    G = s_utils.adjacency_matrix_to_graph(adjacency_matrix)
    return G, list_of_kingdom_names.index(starting_kingdom)

def writeGraphFile(name, start, G): #name : String, start : String, G : networkx
    f = open( name + ".in","w+")
    f.write(str(G.number_of_nodes()) + "\n")
    nodes = G.nodes()
    for n in nodes:
        f.write(str(n) + " ")
    f.write("\n")
    f.write(str(start) + "\n")
    for n in nodes:
        for nn in nodes:
            if nn in G[n]:
                f.write(str(G[n][nn]["weight"]) + " ")
            else:
                f.write("x ")
        f.write("\n")
    f.close()

if __name__ == '__main__':
    file = open("att48_xy.txt","r")
    filelines = file.readlines()
    print(filelines)
    pos = [map(lambda x: int(x), re.split("\s+", line[:-1].strip())) for line in filelines]
    print(pos)
    G = nx.Graph()
    file.close()
    file = open("att48_s.txt","r")
    filelines = file.readlines()
    prev = None
    weight = 0.0
    for line in filelines:
        curr = int(line)
        if curr and prev:
            w = ((pos[curr - 1][0] - pos[prev - 1][0])*(pos[curr - 1][0] - pos[prev - 1][0]) + \
            (pos[curr - 1][1] - pos[prev - 1][1])*(pos[curr - 1][1] - pos[prev - 1][1]))**0.5
            weight += w
            print(w)
            G.add_edge(curr, prev, weight = w)
        prev = curr
    random.seed()
    file.close()
    #G = gen.random_connected_graph(10, 5, 0.1)
    writeGraphFile("att48", 1, G)
    print(nx.is_connected(G))
    print(G.nodes())
    print(G.edges())
    print(weight)
