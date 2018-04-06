import networkx as nx

def value_neg_weight(G):
    def value_fn(n):
        return -G.nodes[n]['weight']
    return value_fn

def value_deg_per_weight(G):
    def value_fn(n):
        return G.degree[n] / G.nodes[n]['weight']
    return value_fn

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
    value_edge_vertex_bc
]
