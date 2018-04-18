import argparse

import networkx as nx
from networkx.algorithms import approximation as nx_apx

import gtsp
import writer
import gen
import glns_interface
import solver
import graph_utils as g_utils

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parsing arguments')
    # parser.add_argument('--all', action='store_true', help='If specified, the input validator is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('input', nargs='?', type=str, help='The path to the input file')
    parser.add_argument('--glns_timeout', help='Timeout for GLNS', type=int)
    # parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()
    timeout = 30
    if args.glns_timeout:
        timeout = args.glns_timeout

    if args.input:
        print('loading {}.in ...'.format(args.input))
        G, start = writer.readInFile(args.input)
    else:
        print('making random input...')
        G = gen.random_connected_graph(200, 50, 0.1)
        start = 0

    print('start: {}'.format(start))
    
    if True:
        G_str = g_utils.string_label(G)

        dist, ids, clusters, og_path = gtsp.conquer_to_gtsp(G_str, start)
        print('done transforming problem')
        # for _, _, data in G_gtsp.edges(data=True):
        #     data['weight'] = int(1e5 * data['weight']) # TODO smart scaling?
        tour_gtsp = glns_interface.run(dist, ids, clusters, timeout)
        print(tour_gtsp)
        tour, ds = gtsp.mapped_gtsp_to_conquer_solution(tour_gtsp, start, ids, og_path)
        # print(tour, ds)
        print()

        print('GLNS')
        solver.print_solution_info(G, tour, ds)
        print()

    s_tour, s_ds = solver.run_everything(G, start=start, debug=False)
    print('greedy')
    solver.print_solution_info(G, s_tour, s_ds)
