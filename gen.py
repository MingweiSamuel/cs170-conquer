import random as rand
from functional import seq
import networkx as nx
import skeleton.student_utils_sp18 as s_utils
import graph_utils as g_utils
import names

def random_graph(n, dim, epct):
    G = nx.Graph()
    for a in range(n):
        G.add_node(a, weight=rand.randint(0, 1000))
    pos = [[ rand.randint(0, 100) for _ in range(dim) ] for _ in range(n) ]
    for a in range(n):
        for b in range(n):
            if rand.uniform(0, 1) < epct:
                dist = sum([ (pos[a][i] - pos[b][i]) ** 2 for i in range(dim) ]) ** 0.5
                G.add_edge(a, b, weight=dist)
    return G

def random_connected_graph(n, dim, epct):
    G = nx.Graph()
    pos = [[ rand.randint(0, 100) for _ in range(dim) ] for _ in range(n) ]
    for a in range(n):
        nodes = [node for node in G.nodes()]
        G.add_node(a, weight=rand.randint(1, 100))
        if len(nodes) > 0:
            index = rand.randint(0, len(nodes) - 1)
            for m in nodes:
                if m == nodes[index] or rand.uniform(0, 1) < epct:
                    dist = sum([ (pos[a][k] - pos[m][k]) ** 2 for k in range(dim) ]) ** 0.5
                    G.add_edge(a, m, weight=dist)
    return G

def random_graph_trick_nodes(n, dim, epct):
    G = random_graph(n, dim, epct)
    for n in G.nodes:
        avg = seq(G.edges(n, data=True)) \
                .map(lambda e: e[2]['weight'] + 0.1) \
                .min()
        G.nodes[n]['weight'] = 1e3 / avg
    return G

def check(G):
    if not nx.is_connected(G):
        print('Your graph is not connected')
    if not s_utils.is_metric(G):
        print('Your graph is not metric')

def genU1(): # returns Graph, start, end, path:(node, conquer), weight of path
    G = nx.Graph()
    G.add_node(0, weight = 2)
    G.add_node(1, weight = 1)
    G.add_node(2, weight = 2)
    G.add_node(3, weight = 1)
    G.add_node(4, weight = 2)
    G.add_edge(0, 1, weight = 3)
    G.add_edge(0, 2, weight = 4)
    G.add_edge(1, 2, weight = 2)
    G.add_edge(2, 3, weight = 2)
    G.add_edge(1, 3, weight = 3)
    G.add_edge(2, 4, weight = 4)
    G.add_edge(3, 4, weight = 2)
    return G, 0, 4, ((0, False), (2, True), (4, False)), 10

def genU2():
    G = nx.Graph()
    G.add_node(0, weight = 2)
    G.add_node(1, weight = 1)
    G.add_node(2, weight = 3)
    G.add_node(3, weight = 1)
    G.add_node(4, weight = 2)
    G.add_edge(0, 1, weight = 1)
    G.add_edge(0, 2, weight = 1)
    G.add_edge(1, 2, weight = 2)
    G.add_edge(2, 3, weight = 2)
    G.add_edge(1, 3, weight = 1)
    G.add_edge(2, 4, weight = 1)
    G.add_edge(3, 4, weight = 1)
    return G, 0, 4, ((0, False), (1, True), (3, True), (4, False)), 5

def genU3():
    G = nx.Graph()
    G.add_node(0, weight = 1)
    G.add_node(1, weight = 1)
    G.add_node(2, weight = 1)
    G.add_node(3, weight = 3)
    G.add_node(4, weight = 1)
    G.add_edge(0, 1, weight = 1)
    G.add_edge(1, 2, weight = 1)
    G.add_edge(2, 3, weight = 1)
    G.add_edge(3, 4, weight = 1)
    return G, 0, 4, ((0, False),(1, True),(2, True),(3, False),(4, True)), 7

def genU4():
    G = nx.Graph()
    G.add_node(0, weight = 1)
    G.add_node(1, weight = 1)
    G.add_node(2, weight = 3)
    G.add_node(3, weight = 1)
    G.add_node(4, weight = 1)
    G.add_edge(0, 1, weight = 1)
    G.add_edge(0, 2, weight = 1)
    G.add_edge(1, 2, weight = 2)
    G.add_edge(2, 3, weight = 2)
    G.add_edge(1, 3, weight = 1)
    G.add_edge(2, 4, weight = 1)
    G.add_edge(3, 4, weight = 1)
    return G, 0, 4, ((0, True), (2, False), (4,True)), 4

def getUnit():
    units = [genU1, genU2, genU3, genU4]
    return units[random.randrange(0,len(units))]()
