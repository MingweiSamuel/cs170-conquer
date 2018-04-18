from functional import seq
import networkx as nx
from networkx.utils import pairwise

import skeleton.student_utils_sp18 as s_utils
import graph_utils as g_utils

def check(G, tour, ds):
    if len(tour) > 1:
        edges = pairwise(tour + [ tour[0] ])
        for edge in edges:
            if edge not in G.edges:
                raise Exception('Bad tour, graph missing edge: ' + str(edge))
    if not nx.is_dominating_set(G, ds):
        raise Exception('bad dominating set.')
    missing = ds - set(tour)
    if missing:
        raise Exception('failed to visit in ds: ' + str(missing))

def rotate_start(tour, start):
    """
    Rotates tour so it starts/ends with START.
    """
    i = tour.index(start)
    return tour[i:] + tour[:i]

def cost(G, tour, ds):
    return cost_tour(G, tour), cost_ds(G, ds)

def cost_tour(G, tour):
    if len(tour) == 1:
        return 0
    edges = pairwise(tour + [ tour[0] ])
    return seq(edges) \
            .map(lambda e: G.edges[e]['weight']) \
            .sum()
def cost_ds(G, ds):
    return seq(ds) \
            .map(lambda n: G.nodes[n]['weight']) \
            .sum()

def is_transformed_tsp(G):
    degrees = seq(G.degree()) \
            .map(lambda t: t[1]) \
            .count_by_value() \
            .to_dict()
    if 2 != len(degrees):
        return False
    half = len(G) / 2
    if 1 not in degrees or half not in degrees:
        return False
    return half == degrees[1] == degrees[half]

def untransform_tsp(G):
    half = len(G) / 2
    groups = seq(G.degree()) \
            .map(lambda t: t[::-1]) \
            .group_by_key() \
            .to_dict()
    path_nodes = groups[half]
    dangling_nodes = groups[1]

    G_tsp = g_utils.subgraph(G, path_nodes)
    ids = list(G_tsp.nodes())
    G_tsp = nx.convert_node_labels_to_integers(G_tsp)
    
    dangling_dict = seq(dangling_nodes) \
            .map(lambda v: (next(G.neighbors(v)), v)) \
            .to_dict()

    return G_tsp, ids, dangling_dict
    
