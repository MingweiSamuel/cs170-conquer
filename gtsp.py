import re
import itertools

import networkx as nx
from functional import seq

import skeleton.student_utils_sp18 as s_utils
import graph_utils as g_utils
import kingdom_utils as k_utils

# converting to and from GTSP problems.

def read_solution_gtsp(inp):
    """
    <Tour size M>
    <Tour weight>
    <Node 1 in the tour>
    <Node 2 in the tour>
    ...
    <Node M in the tour>

    >>> with open('gtsp/31pr152.solution.txt') as f:
    ...     read_solution_gtsp(f)
    (51576, [42, 17, 9, 6, 10, 5, 11, 4, 12, 13, 33, 35, 50, 91, 77, 71, 89, 113, 122, 120, 119, 118, 117, 109, 83, 60, 82, 86, 81, 87, 65])
    """
    M = int(next(inp))
    weight = int(next(inp))
    # Subtract 1 because input is 1-indexed.
    tour = seq(range(M)).map(lambda _: next(inp)).map(int).map(lambda n: n - 1).to_list()

    return (weight, tour)

def read_gtsp_gtsp(inp):
    """
    NODE_COORD_SECTION
    GTSP_SET_SECTION:
    """
    pass

def read_text_gtsp(inp):
    """
    N: <Number of nodes N>
    M: <Number of clusters M>
    Symmetric: <"true" or "false">
    Triangle: <"true" or "false">
    <C1> <Node 1 in Cluster 1> <Node 2 in Cluster 1> ... <Node C1 in Cluster 1>
    <C2> <Node 1 in Cluster 2> <Node 2 in Cluster 2> ... <Node C2 in Cluster 2>
    ...
    <CM> <Node 1 in Cluster M> <Node 2 in Cluster M> ... <Node CM in Cluster M>
    <w(1,1)> <w(1,2)> ... <w(1,N)>
    <w(2,1)> <w(2,2)> ... <w(2,N)>
    ...
    <w(N,1)> <w(N,2)> ... <w(N,N)>
    
    >>> with open('gtsp/31pr152.txt') as f:
    ...     G, clusters = read_text_gtsp(f)
    >>> len(G)
    152
    >>> str(G.nodes())
    '[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151]'
    >>> len(G.edges())
    11476
    >>> len(clusters)
    31
    """

    N_match = re.search(r'^N:\s*(\d+)\s*$', next(inp), re.IGNORECASE)
    N = int(N_match.group(1))
    
    M_match = re.search(r'^M:\s*(\d+)\s*$', next(inp), re.IGNORECASE)
    M = int(M_match.group(1))
    
    sym_match = re.search(r'^Symmetric:\s*(true|false)\s*$', next(inp), re.IGNORECASE)
    sym = 'true' == sym_match.group(1)

    tri_match = re.search(r'^Triangle:\s*(true|false)\s*$', next(inp), re.IGNORECASE)
    tri = 'true' == tri_match.group(1)

    # subtract 1 because input is 1-indexed.
    clusters = seq(range(M)).map(lambda _: seq(next(inp).split()).map(int).map(lambda n: n - 1).to_set()).to_list()
    
    matrix = seq(range(N)).map(lambda _: seq(next(inp).split()).map(int).to_list()).to_list()

    G = s_utils.adjacency_matrix_to_graph(matrix)        
    return (G, clusters)


def gtsp_to_conquer(G, clusters, node_weight=1e8, set_node_weight=1, set_travel_edge_weight=1, set_con_edge_weight=1e8):
    """
    Reduces this GTSP instance to a conquer instance.
    node_weight:
        The cost to conquer nodes already in G. Should be expensive.
    set_node_weight:
        The cost to conquer the new nodes which represent sets. Should be cheap.
    set_travel_edge_weight:
        The cost to travel to the representative node. Should be cheap.
    set_con_edge_weight:
        The cost of the edges that connect the set. Should be expensive.
        JK this has to be determined by shortest paths due to the metric property.

    >>> with open('gtsp/31pr152.txt') as f:
    ...     G, clusters = read_text_gtsp(f)
    >>> G = gtsp_to_conquer(G, clusters)
    >>> len(G)
    304
    """
    dist = dict(nx.floyd_warshall(G))
    G = G.copy()
    N = len(G)
    for i in range(N):
        G.nodes[i]['weight'] = node_weight
        G.add_node(N + i, weight=set_node_weight) # Node to conquer to visit this set.
        G.add_edge(i, N + i, weight=set_travel_edge_weight) # Edge to get to above.
    # print(len(G.edges())) # 11476 + 152 = 11628

    for cluster in clusters:
        for u, v in itertools.product(cluster, cluster):
            if u >= v:
                continue
            # Connecting edges which form the set.
            w = dist[u][v] + set_travel_edge_weight
            # w = 1e8
            G.add_edge(N + u, v, weight=w)
            G.add_edge(u, N + v, weight=w)
            G.add_edge(N + u, N + v, weight=w + set_travel_edge_weight)
    return G
    
def gtsp_to_conquer_solution(clusters, tour):
    """
    Convert the GTSP solution to a conquer solution (for the gtsp_to_conquer converted graph).
    At each node v in the tour, we visit and conquer all clusters v is a part of.
    clusters:
        List of Sets representing clusters.
    tour:
        Original GTSP tour.

    >>> with open('gtsp/31pr152.txt') as f:
    ...     G, clusters = read_text_gtsp(f)
    >>> len(G)
    152
    >>> with open('gtsp/31pr152.solution.txt') as f:
    ...     _, tour = read_solution_gtsp(f)
    >>> tour
    [42, 17, 9, 6, 10, 5, 11, 4, 12, 13, 33, 35, 50, 91, 77, 71, 89, 113, 122, 120, 119, 118, 117, 109, 83, 60, 82, 86, 81, 87, 65]

    >>> # Run this.
    >>> tour, ds = gtsp_to_conquer_solution(clusters, tour)
    >>> tour
    [42, 194, 42, 17, 169, 17, 9, 161, 9, 6, 158, 6, 10, 162, 10, 5, 157, 5, 11, 163, 11, 4, 156, 4, 12, 13, 165, 13, 33, 35, 187, 35, 50, 202, 50, 91, 77, 71, 223, 71, 89, 113, 122, 274, 122, 120, 272, 120, 119, 118, 270, 118, 117, 269, 117, 109, 261, 109, 83, 235, 83, 60, 212, 60, 82, 86, 238, 86, 81, 233, 81, 87, 239, 87, 65]
    >>> ds
    {261, 269, 270, 272, 274, 156, 157, 158, 161, 162, 163, 165, 169, 187, 194, 202, 212, 223, 233, 235, 238, 239}
    
    >>> # Check answer.
    >>> G = gtsp_to_conquer(G, clusters)
    >>> len(G)
    304
    >>> k_utils.check(G, tour, ds)
    >>> # No error.
    """
    N = len(set(v for c in clusters for v in c)) # Size of graph. All nodes are in at least one cluster.
    new_tour = []
    ds = set()
    for v in tour:
        new_tour.append(v) # Visit v.
        # Clusters we have not hit after visiting v.
        missed_clusters = seq(clusters).filter(lambda c: v not in c).to_list()
        # Only bother capturing the rep if we need to hit a cluster.
        if len(missed_clusters) < len(clusters):
            new_tour.append(N + v) # Visit rep.
            ds.add(N + v) # Conquer rep.
            new_tour.append(v) # Go back to main.
            clusters = missed_clusters # Update list of clusters.
    
    return new_tour, ds

# Convert conquer to GTSP
def conquer_to_gtsp(G_str, start):
    """
    Convert a str-labelled conquer graph G(V, E) to a GTSP graph G'(V', E') with |V'| = 2|V| + 2|E|.

    >>> import random
    >>> random.seed(3)
    >>> import gen
    >>> G = gen.random_connected_graph(200, 10, 0.01)
    >>> G, clusters, ids, _ = conquer_to_gtsp(G, 0)
    >>> len(G)
    1230
    >>> len(clusters) # |V| + 2
    202
    """
    start = str(start)

    G_aug = nx.Graph()
    G_aug.add_nodes_from(G_str.nodes())

    for v in G_str:
        G_aug.add_node(v + '_*')
        G_aug.add_edge(v, v + '_*', weight=G_str.nodes[v]['weight'] / 2)
    
    clusters = [ { start }, set(G_str.nodes()) - { start } ]

    for v in G_str:
        v_cluster = { v + '_*' }

        for u in G_str.neighbors(v):
            r = u + '_' + v
            v_cluster.add(r)

            G_aug.add_node(r)
            G_aug.add_edge(u + '_*', r, weight=0)

        clusters.append(v_cluster)


    _, og_dist, og_path = g_utils.floyd_warshall_all(G_str)
    # og_dist = dict(nx.floyd_warshall(G_str))
    def tran(u, v):
        us = u.split('_')
        vs = v.split('_')
        return us, us[0], vs, vs[0]
    def dist(u, v):
        us, u0, vs, v0 = tran(u, v)
        if u0 == v0:
            return 0
        d = og_dist[u0][v0]
        if len(us) > 1:
            d += G_aug[u0][u0 + '_*']['weight']
        if len(vs) > 1:
            d += G_aug[v0][v0 + '_*']['weight']
        return d

    G_full = nx.Graph()
    G_full.add_nodes_from(G_aug.nodes())

    for u, v in itertools.product(G_aug.nodes(), G_aug.nodes()):
        G_full.add_edge(u, v, weight=dist(u, v))
    
    ids = list(G_full.nodes())
    return G_full, clusters, ids, og_path

def mapped_gtsp_to_conquer_solution(tour, ids, og_path):
    tour_ids = seq(tour).map(lambda i: ids[i]).to_list()
    print(tour_ids)

    ds = set()
    stops = []
    for v in tour_ids:
        vs = v.split('_')
        v0 = vs[0]
        if len(vs) > 1:
            ds.add(v0)
        if not stops or stops[-1] != v0:
            stops.append(v0)
    
    print(stops)
    tour = g_utils.stops_to_tour(stops, og_path)

    tour = seq(tour).map(int).to_list()
    ds = seq(ds).map(int).to_set()
    
    return tour, ds


        
def output_gtsp(output, G, clusters, name='unnamed'):
    """
    NAME : rat575
    COMMENT : Rattled grid (Pulleyblank)
    TYPE : TSP
    DIMENSION : 575
    GTSP_SETS : 115
    EDGE_WEIGHT_TYPE : EUC_2D
    NODE_COORD_SECTION
    """
    output.write('NAME: ' + re.sub(r'\W', '_', str(name)) + '\n')
    output.write('COMMENT: ' + ' auto generated ' + name + '\n')
    output.write('TYPE: TSP\n')
    output.write('DIMENSION: ' + str(len(G)) + '\n')
    output.write('GTSP_SETS: ' + str(len(clusters)) + '\n')
    output.write('EDGE_WEIGHT_TYPE: EXPLICIT\n')
    output.write('EDGE_WEIGHT_FORMAT: LOWER_DIAG_ROW\n')
    output.write('EDGE_WEIGHT_SECTION:\n')
    ids = list(G.nodes())
    for u in range(len(G)):
        for v in range(u + 1):
            if u == v:
                output.write('0     ')
            else:
                s = str(G[ids[u]][ids[v]]['weight'])
                output.write(f'{s: <5}')
            output.write(' ')
        output.write('\n')
    output.write('GTSP_SET_SECTION:\n')
    for i, cluster in enumerate(clusters):
        # Add 1 to clusters because of 1-indexing.
        row = [ str(i + 1) ] + seq(cluster).map(lambda v: ids.index(v)).map(lambda n: n + 1).map(str).to_list() + [ '-1\n' ]
        output.write(' '.join(row))
    output.write('EOF\n')
