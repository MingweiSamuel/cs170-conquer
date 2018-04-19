import math
import random as rand
from functional import seq
import networkx as nx
from networkx.utils import pairwise
from networkx.utils.union_find import UnionFind

def is_complete(G):
    return len(G) * (len(G) - 1) == 2 * len(G.edges)

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

def minimum_connected_subset_spanning_tree(G, nodes, **kwargs):
    return nx.minimum_spanning_tree(subgraph(G, nodes), **kwargs)

def nearest_detour_tour(G, nodes, start=None, all_paths=None):
    nodes = list(nodes)

    if all_paths:
        pred, dist, path = all_paths
    else:
        pred, dist, path = floyd_warshall_all(G)

    nodes_left = set(nodes)
    if start is None:
        stops = [ rand.choice(nodes) ]
        nodes_left.remove(stops[0])
    else:
        stops = [ start ]

    # best = lambda n: seq(range(len(stops))) \
    #         .map(lambda i: (i, dist[stops[i - 1]][n])) \
    #         .min_by(lambda p: p[1])
    best = lambda n: seq(range(len(stops))) \
            .map(lambda i: (i, dist[stops[i - 1]][n] + dist[n][stops[i]])) \
            .min_by(lambda p: p[1])
    while nodes_left:
        nex = seq(nodes_left) \
                .map(lambda n: (n,) + tuple(best(n))) \
                .min_by(lambda p: p[2])
        node, i, _ = nex
        stops.insert(i, node)
        nodes_left.remove(node)

    if len(set(stops)) == 1:
        return list(set(stops))
    #print(stops)
    tour = stops_to_tour(stops, path)
    #print(tour)
    return tour

def christofides_tour(G, nodes, start=None, all_paths=None):
    # christofides
    # all pairs shortest dist graph (of original)

    if all_paths:
        pred, dist, path = all_paths
    else:
        pred, dist, path = floyd_warshall_all(G)
    
    G_full = nx.Graph()
    G_full.add_nodes_from(nodes)
    for a in nodes:
        for b in nodes:
            G_full.add_edge(a, b, weight=dist[a][b])
            
    G_tree = nx.minimum_spanning_tree(G_full)

    # get odd degree nodes in trees
    odd = seq(G_tree.nodes()) \
            .filter(lambda n: G_tree.degree(n) % 2 == 1) \
            .to_list()

    G_matching = nx.Graph()
    G_matching.add_nodes_from(odd)
    max_dist = 0
    for a in odd:
        for b in odd:
            max_dist = max(max_dist, dist[a][b])
    for a in odd:
        for b in odd:
            # invert weights to find *minimal* matching (+1 for nonzero)
            G_matching.add_edge(a, b, weight=1 + max_dist - dist[a][b])
    match_edges = nx.max_weight_matching(G_matching)

    # eulerian multigraph
    G_euler = nx.MultiGraph(G_tree)
    for a, b in match_edges:
        G_euler.add_edge(a, b, weight=dist[a][b])
    if not nx.is_eulerian(G_euler):
        raise Exception('New G_euler not eulerian')

    # All vertices now have even degree. We construct a eulerian tour.
    # This doesn't contain all the "bridge" vertices we need for the
    # added "indices". Hence it is called "stops" as in "tour stops"
    # rather than "tour".
    stops = seq(nx.eulerian_circuit(G_euler)) \
            .map(lambda e: e[0]) \
            .to_list()

    if len(stops) < 1:
        stops = list(nodes) # singleton

    # TODO smart cutting short
    stops = remove_dupes(stops)

    stops = insert_start_into_stops(stops, dist, path, start)
    if len(stops) == 1:
        return list(stops)

    tour = stops_to_tour(stops, path)
    return tour

def insert_start_into_stops(stops, dist, path, start):
    if 0 == len(stops):
        return [ start ]
    stops = stops[:]
    if start in stops:
        return stops
    i, e = seq(pairwise([ stops[0] ] + stops)) \
            .enumerate() \
            .min_by(lambda p: dist[p[1][0]][start] + dist[start][p[1][1]])
    stops.insert(i, start)
    return stops

def stops_to_tour(stops, path):
    return seq(pairwise(stops + [ stops[0] ])) \
            .flat_map(lambda e: path(e[0], e[1])) \
            .to_list()

def remove_dupes(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


# https://networkx.github.io/documentation/stable/_modules/networkx/algorithms/shortest_paths/dense.html#floyd_warshall_predecessor_and_distance
def floyd_warshall_all_multi(G, weight='weight'):
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

    # return a list of paths
    # could be sped up with DP
    def all_paths(u, v):
        if u == v:
            return [[]]
        return seq(pred[v][u]) \
                .flat_map(lambda nu: all_paths(nu, v)) \
                .map(lambda path: [ u ] + path)
    return dict(pred), dict(dist), all_paths

def string_label(G):
    G_str = nx.relabel_nodes(G, { v: str(v) for v in G }, copy=True)
    return G_str
