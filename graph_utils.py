import math
from functional import seq
import networkx as nx
from networkx.utils.union_find import UnionFind

def floyd_warshall_all(G):
    pred, dist = nx.floyd_warshall_predecessor_and_distance(G)
    def path(u, v): # doesn't include v
        while u != v:
            yield u
            u = pred[v][u]
    return pred, dist, path

def subgraph(G, nodes):
    G_new = nx.Graph()
    G_new.add_nodes_from(nodes)
    G_new.add_edges_from(seq(G.edges(data=True)) \
        .filter(lambda e: G_new.has_node(e[0]) and G_new.has_node(e[1])))
    return G_new

def is_connected_subset(G, nodes): 
    return nx.is_connected(subgraph(G, nodes))

def minimum_subset_spanning_tree(G, nodes, **kwargs):
    return nx.minimum_spanning_tree(subgraph(G, nodes), **kwargs)


# https://networkx.github.io/documentation/stable/_modules/networkx/algorithms/shortest_paths/dense.html#floyd_warshall_predecessor_and_distance
def floyd_warshall_all_predecessors_and_distance(G, weight='weight'):
    """Find all-pairs shortest path lengths using Floyd's algorithm.

    Parameters
    ----------
    G : NetworkX graph

    weight: string, optional (default= 'weight')
       Edge data key corresponding to the edge weight.

    Returns
    -------
    predecessor,distance : dictionaries
       Dictionaries, keyed by source and target, of predecessors and distances
       in the shortest path.

    Notes
    ------
    Floyd's algorithm is appropriate for finding shortest paths
    in dense graphs or graphs with negative weights when Dijkstra's algorithm
    fails.  This algorithm can still fail if there are negative cycles.
    It has running time $O(n^3)$ with running space of $O(n^2)$.

    See Also
    --------
    floyd_warshall
    floyd_warshall_numpy
    all_pairs_shortest_path
    all_pairs_shortest_path_length
    """
    from collections import defaultdict
    # dictionary-of-dictionaries representation for dist and pred
    # use some defaultdict magick here
    # for dist the default is the floating point inf value
    dist = defaultdict(lambda: defaultdict(lambda: float('inf')))
    for u in G:
        dist[u][u] = 0
    pred = defaultdict(dict)
    # initialize path distance dictionary to be the adjacency matrix
    # also set the distance to self to 0 (zero diagonal)
    undirected = not G.is_directed()
    for u, v, d in G.edges(data=True):
        e_weight = d.get(weight, 1.0)
        dist[u][v] = min(e_weight, dist[u][v])
        pred[u][v] = set([ u ])
        if undirected:
            dist[v][u] = min(e_weight, dist[v][u])
            pred[v][u] = set([ v ])
    for w in G:
        for u in G:
            for v in G:
                if dist[u][v] > dist[u][w] + dist[w][v]:
                    dist[u][v] = dist[u][w] + dist[w][v]
                    pred[u][v] = pred[w][v]
                elif w == u or w == v or u == v or math.isinf(dist[u][v]):
                    continue
                elif dist[u][v] == dist[u][w] + dist[w][v]:
                    pred[u][v] = pred[u][v].union(pred[w][v])
    return dict(pred), dict(dist)