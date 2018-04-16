import argparse

import networkx as nx
from networkx.algorithms import approximation as nx_apx

import gtsp
import gen
import glns_interface
import solver
import graph_utils as g_utils

if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Parsing arguments')
    # parser.add_argument('--all', action='store_true', help='If specified, the input validator is run on all files in the input directory. Else, it is run on just the given input file')
    # parser.add_argument('output', type=str, help='The path to the output file')
    # parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    # args = parser.parse_args()

    G = gen.random_connected_graph(200, 50, 0.2)
    G_str = g_utils.string_label(G)

    G_gtsp, clusters, ids, og_path = gtsp.conquer_to_gtsp(G_str, 0)
    for _, _, data in G_gtsp.edges(data=True):
        data['weight'] = int(100 * data['weight'])
    tour_gtsp = glns_interface.run(G_gtsp, clusters, timeout=120)
    tour, ds = gtsp.mapped_gtsp_to_conquer_solution(tour_gtsp, ids, og_path)
    # print(tour, ds)
    print()

    print('GLNS')
    solver.print_solution_info(G, tour, ds)

    solver.run_everything(G)
