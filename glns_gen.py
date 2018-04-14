import itertools
import argparse
import random as rand

import networkx as nx

import gen
import gtsp
import graph_utils as g_utils
import writer

def make_clusters(G):

    dist = dict(nx.floyd_warshall(G))

    N = len(G)
    # G_gtsp = nx.Graph()
    # G_gtsp.add_nodes_from(range(N))
    # for u, v in itertools.product(range(N), range(N)):
    #     G_gtsp.add_edge(u, v, weight=dist[u][v])
    
    clusters = []
    nodes = list(range(N))
    rand.shuffle(nodes)

    # i = 0
    # while i < len(G):
    #     j = i + int(rand.uniform(1, 2) + len(G) * rand.random() * rand.random() * rand.random() * rand.random())
    #     print(j - i)
    #     clusters.append(nodes[i:min(N, j)])
    #     i = j
    # print(clusters)

    n_clusters = int(rand.uniform(4, len(G) / 2) + (len(G) / 2) * rand.random() * rand.random())
    rep_nodes = nodes[:n_clusters]
    hit = set(rep_nodes)
    clusters = [ [ r ] for r in rep_nodes ]

    for v in range(N):
        if v in hit:
            continue
        rep_nodes.sort(key=lambda u: dist[u][v])
        i = int(len(rep_nodes) * rand.random() * rand.uniform(0.5, 1) * rand.uniform(0.5, 1) * rand.uniform(0.5, 1) * rand.uniform(0.5, 1))
        print(i)
        clusters[i].append(v)
        hit.add(v)
    
    print([ len(c) for c in clusters ])

    return clusters

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('type', type=str, help='gen or path')
    args = parser.parse_args()
    
    print(args.type)

    if 'gen' == args.type:
        from datetime import datetime
        rand.seed(datetime.now())

        N = 25
        G = gen.random_connected_graph(N, 10, 1)

        for u, v in itertools.product(range(N), range(N)):
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=int(1e7))

        for _, _, data in G.edges(data=True):
            data['weight'] = int(data['weight']) + 1
        for _, data in G.nodes(data=True):
            data['weight'] = int(data['weight'])
            
        clusters = make_clusters(G)
        print(repr(clusters))

        dist = dict(nx.floyd_warshall(G))


        G_metric = G.copy()
        for u, v, data in G_metric.edges(data=True):
            data['weight'] = dist[u][v]
        with open('glns_gen.txt', 'w+') as output_file:
            gtsp.output_gtsp(output_file, G_metric, clusters, name='glns_gen')

        writer.writeInFile('glns_oggraph', 0, G)


    elif 'path' == args.type:
        G, _ = writer.readInFile('glns_oggraph')

        # CHANGE THIS LINE
        clusters = \
            [[18, 7, 8, 9, 23], [6, 11, 17], [14, 1], [21, 13, 16], [5, 2], [15], [12], [24], [22], [4], [0], [20], [3], [19], [10]]
        clusters = [ set(c) for c in clusters ]

        # RUN
        # julia GLNS/GLNScmd.jl glns_gen.txt -max_time=10 -trials=500

        # CHANGE THIS LINE
        tour_gtsp = [5, 20, 2, 11, 1, 3, 4, 25, 23, 21, 9, 16, 13, 17, 18]
        tour_gtsp = [ n - 1 for n in tour_gtsp ]


        # CONVERT STEP
        _, dist, path = g_utils.floyd_warshall_all(G)

        G = gtsp.gtsp_to_conquer(G, clusters)
        tour, ds = gtsp.gtsp_to_conquer_solution(clusters, tour_gtsp)


        G_fix = G.copy()
        to_remove = []
        for u, v, data in G_fix.edges(data=True):
            if data['weight'] >= 1e7:
                print('removing ' + str((u, v)))
                to_remove.append((u, v))
        G_fix.remove_edges_from(to_remove)


        # FIX
        pred, dist, path = g_utils.floyd_warshall_all(G_fix)
        tour = g_utils.stops_to_tour(tour, path)

        gen.check(G_fix)
        writer.writeInFile('glns_newg_graph', tour[0], G_fix)
        writer.writeOutFile('glns_newg_graph', tour + [ tour[0] ], ds)

        print(tour, ds)

        # VALIDATE: python skeleton/output_validator.py glns_newg_graph.in glns_newg_graph.out

    else:
        print('Unknown: ' + args.type)

    # writer.writeGraphFile(name, start, G)


    
    