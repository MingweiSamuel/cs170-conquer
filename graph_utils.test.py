import networkx as nx
import graph_utils as g_utils

G = nx.Graph()
G.add_nodes_from([ 0, 1, 2, 3, 4, 5 ])

G.add_edge(0, 1, weight=1)
G.add_edge(0, 2, weight=1)

G.add_edge(1, 3, weight=1)
G.add_edge(1, 4, weight=1)
G.add_edge(2, 3, weight=1)
G.add_edge(2, 4, weight=1)

G.add_edge(3, 5, weight=1)
G.add_edge(4, 5, weight=1)

#
G.add_edge(1, 5, weight=2)
G.add_edge(0, 4, weight=2)
G.add_edge(0, 5, weight=3)

dist, prev, all_paths = g_utils.floyd_warshall_all_multi(G)

print(dist, prev)
print(all_paths(0, 5))