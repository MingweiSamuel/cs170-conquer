from functional import seq
import networkx as nx
from networkx.utils import pairwise
import skeleton.student_utils_sp18 as s_utils

def check(G, tour, ds):
    edges = pairwise(tour + [ tour[0] ])
    for edge in edges:
        if edge not in G.edges:
            raise Exception('Bad tour, graph missing edge: ' + str(edge))
    if not nx.is_dominating_set(G, ds):
        raise Exception('bad dominating set.')
    missing = ds - set(tour)
    if missing:
        raise Exception('failed to visit in ds: ' + str(missing))

def cost(G, tour, ds):
    return cost_tour(G, tour), cost_ds(G, ds)

def cost_tour(G, tour):
    edges = pairwise(tour + [ tour[0] ])
    return seq(edges) \
            .map(lambda e: G.edges[e]['weight']) \
            .sum()
def cost_ds(G, ds):
    return seq(ds) \
            .map(lambda n: G.nodes[n]['weight']) \
            .sum()
