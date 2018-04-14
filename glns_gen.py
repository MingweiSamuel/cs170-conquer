import itertools
import argparse
import random as rand

import networkx as nx

import gen
import gtsp
import graph_utils as g_utils
import writer

def gtspify_graph(G):

    dist = dict(nx.floyd_warshall(G))

    N = len(G)
    G_gtsp = nx.Graph()
    G_gtsp.add_nodes_from(range(N))
    for u, v in itertools.product(range(N), range(N)):
        G_gtsp.add_edge(u, v, weight=dist[u][v])
    
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

    return G_gtsp, clusters

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('type', type=str, help='gen or path')
    args = parser.parse_args()
    
    print(args.type)

    if 'gen' == args.type:
        from datetime import datetime
        rand.seed(datetime.now())

        G = gen.random_connected_graph(25, 10, 0.8)
        for _, _, data in G.edges(data=True):
            data['weight'] = int(data['weight']) + 1
        for _, data in G.nodes(data=True):
            data['weight'] = int(data['weight'])

        G_gtsp, clusters = gtspify_graph(G)
        with open('glns_gen.txt', 'w+') as output_file:
            gtsp.output_gtsp(output_file, G_gtsp, clusters, name='glns_gen')
        writer.writeGraphFile('glns_oggraph.txt', 0, G)
    elif 'path' == args.type:
        G, start = writer.readGraphFile('glns_oggraph.txt')
        tour_gtsp = [2, 21, 5, 23, 22, 12, 18, 19, 16, 3, 6, 24, 7]
        # CONVERT STEP
        _, dist, path = g_utils.floyd_warshall_all(G)
    else:
        print('Unknown: ' + args.type)

    # writer.writeGraphFile(name, start, G)


    
    