import argparse

import networkx as nx
from networkx.algorithms import approximation as nx_apx

import gtsp
import gen

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parsing arguments')
    # parser.add_argument('--all', action='store_true', help='If specified, the input validator is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('output', type=str, help='The path to the output file')
    # parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()

    G = gen.random_connected_graph(200, 2, 0.01)
    iset, cliques = nx_apx.clique_removal(G)
    print(iset)
    print(cliques)

    # for c in nx.enumerate_all_cliques(G):
    #     print(c)
    # G_gtsp, clusters = gtsp.conquer_to_gtsp(G)
    # with open(args.output, 'w+') as output_file:
    #     gtsp.output_gtsp(output_file, G_gtsp, clusters, name=args.output)
