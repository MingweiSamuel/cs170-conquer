import networkx as nx
import gen
import random
import re
import gtsp
import math
from networkx.utils import pairwise

import skeleton.utils as utils
import skeleton.student_utils_sp18 as s_utils

def readInFile(name):
    input_data = utils.read_file(name + '.in')
    number_of_kingdoms, list_of_kingdom_names, starting_kingdom, adjacency_matrix = s_utils.data_parser(input_data)
    G = s_utils.adjacency_matrix_to_graph(adjacency_matrix)
    # G = nx.relabel_nodes(G, { n: int(n) for n in G.nodes }, copy=True)
    G = nx.convert_node_labels_to_integers(G)
    return G, list_of_kingdom_names, list_of_kingdom_names.index(starting_kingdom)

def readOutFile(name, names=None):
    with open(name + '.out', 'r') as f:
        fn = names.index if names else int
        tour = list(map(fn, f.readline().strip().split()))
        if len(tour) > 1:
            tour = tour[:-1]
        ds = set(map(fn, f.readline().strip().split()))
        return tour, ds

def writeInFile(name, start, G): #name : String, start : String, G : networkx
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
            elif nn == n:
                f.write(str(G.nodes[n]['weight']) + " ")
            else:
                f.write("x ")
        f.write("\n")
    f.close()

def writeOutFile(name, tour, ds):
    ds_cpy = set(ds)
    f = open(name + ".out", "w+")
    for n in tour:
        f.write(str(n) + " ")
    f.write("\n")
    for n in tour:
        if n in ds_cpy:
            ds_cpy.remove(n)
            f.write(str(n) + " ")
    f.close()

def generateAndWriteFiles(posf, sf, name):
    file = posf
    filelines = file.readlines()
    file.close()
    print(filelines)
    pos = [map(lambda x: int(x), re.split("\s+", line[:-1].strip())) for line in filelines]
    print(pos)
    G = nx.Graph()
    file = sf
    filelines = file.readlines()
    file.close()
    tour = [int(line.strip()) for line in filelines]
    minn = min(tour)
    tour = [x - minn for x in tour]
    for i in range(0, len(pos) - 1):
        for j in range(i + 1, len(pos)):
            w = ((pos[i][0] - pos[j][0])*(pos[i][0] - pos[j][0]) + \
            (pos[i][1] - pos[j][1])*(pos[i][1] - pos[j][1]))**0.5
            G.add_edge(i, j, weight = w)
    # for line in filelines:
    #     curr = int(line)
    #     if curr and prev:
    #         w = ((pos[curr - 1][0] - pos[prev - 1][0])*(pos[curr - 1][0] - pos[prev - 1][0]) + \
    #         (pos[curr - 1][1] - pos[prev - 1][1])*(pos[curr - 1][1] - pos[prev - 1][1]))**0.5
    #         weight += w
    #         print(w)
    #         G.add_edge(curr, prev, weight = w)
    #     prev = curr
    clusters = [[i] for i in range(0, len(pos))]
    G = gtsp.gtsp_to_conquer(G, clusters)
    scale(G)
    writeInFile(name, 0, G)
    tour, ds = gtsp.gtsp_to_conquer_solution(clusters, tour)
    writeOutFile(name, tour, ds)
    return G

def scale(G):
    edgesd = nx.get_edge_attributes(G, 'weight')
    nodesd = nx.get_node_attributes(G, 'weight')
    ev = [edgesd[k] for k in edgesd]
    nv = [nodesd[k] for k in nodesd]
    maxx = max(ev + nv)
    scalar = math.floor(2000000000 / maxx)
    for k in edgesd:
        G.edges[k]['weight'] = round(edgesd[k] * scalar, 5)
    for k in nodesd:
        G.nodes[k]['weight'] = round(nodesd[k] * scalar, 5)

if __name__ == '__main__':
    random.seed()
    file1 = open("att48_xy.txt","r")
    file2 = open("att48_s.txt","r")
    #G = gen.random_connected_graph(10, 5, 0.1)
    G = generateAndWriteFiles(file1, file2, "set100")
    print(nx.is_connected(G))
    print(G.nodes())
    print(G.edges())
