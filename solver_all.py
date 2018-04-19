import argparse
import os
import sys
import signal
import time
import random as rand
import multiprocessing as mp

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

# print('making random input...')
# G = gen.random_connected_graph(200, 50, 0.1)
# names = list(range(len(G)))
# start = 0
        
INPUT_PATH = 'skeleton/inputs/'
OUTPUT_PATH = 'outputs/'
def solve_file(tup):
    fname, complexity = tup
    rand.seed()
    time_start = time.time()

    try:
        G, names, start = writer.readInFile(INPUT_PATH + fname)
        print('Solving {}, V={}, E={}, start={}'.format(fname, len(G), len(G.edges), start))

        tour, ds = solver.solve(G, start=start, debug=False, complexity=complexity)
        tour = k_utils.rotate_start(tour, start)

        out_tour = seq(tour).map(lambda i: names[i]).to_list()
        if len(out_tour) > 1:
            out_tour.append(out_tour[0])
        out_ds = seq(ds).map(lambda i: names[i]).to_set()

        print('SOLVED {}, writing output.'.format(fname))
        writer.writeOutFile(OUTPUT_PATH + fname, out_tour, out_ds)
        print('WROTE {}. Elapsed minutes: {:.2f}.'.format(fname, (time.time() - time_start) / 60))
    except Exception as e:
        print('  ~!~!~!~!~!~!~!~!~  EXCEPTION ON INPUT {}. Elapsed minutes: {:.2f}'.format(fname, (time.time() - time_start) / 60), file=sys.stderr)
        print(e, file=sys.stderr)
        raise

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('input', nargs='?', type=str, help='The path to the input file')
    parser.add_argument('--complexity', type=float, help='Multiplier for timeout')
    
    args = parser.parse_args()

    complexity = args.complexity if isinstance(args.complexity, float) else 1
    print('Complexity: {}.'.format(complexity))

    if args.input:
        solve_file((args.input, complexity))
    else:
        all_files = seq(os.listdir(INPUT_PATH)) \
                .map(lambda f: f[:-3]) \
                .to_list()
        # all_files = all_files[0:2]

        inputs = zip(all_files, [ complexity ] * len(all_files))

        # https://stackoverflow.com/a/35134329/2398020
        # dangerous line...don't kill your machine
        workers = 2 * mp.cpu_count()
        
        print('Starting pool with {} workers.'.format(workers))
        # original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = mp.Pool(workers, init_worker)
        # signal.signal(signal.SIGINT, original_sigint_handler)

        time_start = time.time()
        try:
            print('Solving {} inputs.'.format(len(all_files)))
            res = pool.map_async(solve_file, inputs)
            print('Waiting for results...')
            while not res.ready():
                time.sleep(5)
            out = res.get()
        except KeyboardInterrupt:
            print('Caught KeyboardInterrupt, terminating workers.')
            pool.terminate()
        else:
            print('Normal termination.')
            pool.close()
        print('DONE. Elapsed minutes: {:.2f}.'.format((time.time() - time_start) / 60))
