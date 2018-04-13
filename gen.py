import random as rand
from functional import seq
import networkx as nx
import skeleton.student_utils_sp18 as s_utils
import graph_utils as g_utils
import names

def trapezoid_1():
    G = nx.Graph()

    G.add_node('A', weight=100)
    G.add_node('B', weight=100)
    G.add_node('C', weight=100)
    G.add_node('D', weight=100)
    G.add_node('Z', weight=100)

    G.add_edge('Z', 'A', weight=70)
    G.add_edge('Z', 'B', weight=70)
    G.add_edge('Z', 'C', weight=70)
    G.add_edge('Z', 'D', weight=70)

    G.add_edge('A', 'B', weight=10)
    G.add_edge('B', 'C', weight=10)
    G.add_edge('C', 'D', weight=10)

    # extra junk

    G.add_node('START', weight=0.001)
    G.add_node('IS', weight=1e8)
    G.add_node('IE', weight=1e8)
    G.add_edge('START', 'IS', weight=0.001)
    G.add_edge('START', 'IE', weight=0.001)
    G.add_edge('IS', 'A', weight=0.001)
    G.add_edge('IE', 'D', weight=0.001)

    return G

def diamond():
    G = nx.Graph()

    G.add_node('A1', weight=5)
    G.add_node('B0', weight=5)
    G.add_node('B1', weight=5)
    G.add_node('B2', weight=5)
    G.add_node('C0', weight=5)
    G.add_node('C1', weight=5)
    G.add_node('C2', weight=5)
    G.add_node('D0', weight=5)
    G.add_node('D1', weight=5)
    G.add_node('D2', weight=5)
    G.add_node('E1', weight=5)

    G.add_edge('A1', 'B0', weight=1)
    G.add_edge('A1', 'B1', weight=1)
    G.add_edge('A1', 'B2', weight=1)
    
    G.add_edge('B0', 'C0', weight=1)
    G.add_edge('B1', 'C1', weight=1)
    G.add_edge('B2', 'C2', weight=1)

    G.add_edge('D0', 'C0', weight=1)
    G.add_edge('D1', 'C1', weight=1)
    G.add_edge('D2', 'C2', weight=1)

    G.add_edge('E1', 'D0', weight=1)
    G.add_edge('E1', 'D1', weight=1)
    G.add_edge('E1', 'D2', weight=1)

    return G

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

<<<<<<< HEAD
=======
def genU5():
    pass

>>>>>>> f1cf52f5992a868a6f9b9ccec9bc029f5de55544
def getUnit():
    units = [genU1, genU2, genU3, genU4]
    return units[random.randrange(0,len(units))]()
