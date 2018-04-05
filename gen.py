import random as rand
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

def check(G):
    if not nx.is_connected(G):
        print('Your graph is not connected')
    if not s_utils.is_metric(G):
        print('Your graph is not metric')

