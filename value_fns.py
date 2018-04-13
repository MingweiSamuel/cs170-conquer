import networkx as nx
from functional import seq

def value_neg_weight(G):
    def value_fn(n):
        return -G.nodes[n]['weight']
    return value_fn

def value_deg_per_weight(G):
    def value_fn(n):
        return G.degree[n] / G.nodes[n]['weight']
    return value_fn



# new   

def value_neighbor_total_per_weight(G):
    def value_fn(n):
        neighbors_total = seq(G.neighbors(n)) \
                .map(lambda m: G.nodes[m]['weight']) \
                .sum()
        return neighbors_total / G.nodes[n]['weight']
    return value_fn

def value_neighbor_total_minus_weight(G):
    def value_fn(n):
        neighbors_total = seq(G.neighbors(n)) \
                .map(lambda m: G.nodes[m]['weight']) \
                .sum()
        return neighbors_total - G.nodes[n]['weight']
    return value_fn



# betweenness connectivity

def value_edge_bc(G):
    bc = nx.betweenness_centrality(G, weight='weight')
    def value_fn(n):
        return bc[n]
    return value_fn
    
def value_edge_vertex_bc(G):
    G_t = G.copy()
    for u, v in G_t.edges():
        G_t[u][v]['weight'] += (G_t.nodes[u]['weight'] + G_t.nodes[v]['weight']) / 2
    return value_edge_bc(G_t)


value_fns = [
    value_neg_weight,
    value_deg_per_weight,
    value_edge_bc,
    value_edge_vertex_bc,
    value_neighbor_total_per_weight,
    value_neighbor_total_minus_weight
]
