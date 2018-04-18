import argparse

import networkx as nx
from networkx.algorithms import approximation as nx_apx
from functional import seq

import gtsp
import writer
import gen
import glns_interface
import solver
import graph_utils as g_utils
import kingdom_utils as k_utils

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parsing arguments')
    # parser.add_argument('--all', action='store_true', help='If specified, the input validator is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('input', nargs='?', type=str, help='The path to the input file')
    # parser.add_argument('--glns_timeout', help='Timeout for GLNS', type=int)
    # parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()
    timeout = 30
    # if args.glns_timeout:
    #     timeout = args.glns_timeout

    if args.input:
        print('loading {}.in ...'.format(args.input))
        G, names, start = writer.readInFile(args.input)
    else:
        print('making random input...')
        G = gen.random_connected_graph(200, 50, 0.1)
        names = list(range(len(G)))
        start = 0

    print('start: {}'.format(start))

    tour, ds = solver.solve(G, start=start, debug=False)
    tour = k_utils.rotate_start(tour, start)

    out_tour = seq(tour).map(lambda i: names[i]).to_list()
    if len(out_tour) > 1:
        out_tour.append(out_tour[0])
    out_ds = seq(ds).map(lambda i: names[i]).to_set()

    if args.input:
        writer.writeOutFile('outputs/asdf', out_tour, out_ds)
