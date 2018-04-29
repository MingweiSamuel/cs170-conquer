import random
import signal
import subprocess
import time
import ast
import sys
import os

import gtsp

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def write_temp_gtsp(dist, ids, clusters):
    path = 'temp/temp_interface_{}_{}.gtsp'.format(os.getpid(), random.randint(0, int(1e9)))
    with open(path, 'w+', buffering=256 * 1024 ** 2) as output_file:
        gtsp.output_gtsp(output_file, dist, ids, clusters, name='temp_interface')
    return path

DEVNULL = open(os.devnull, 'w')
def run_glkh(path, timeout=10):
    print('  Running GLKH on {} with timeout {}.'.format(path, timeout))
    par_file = path + '.par'
    tour_file = par_file + '.tour'
    with open(par_file, 'w+') as par:
        # TIME_LIMIT is for each RUNS so we do two RUNS with half the timeout each.
        # *_FILE locations are relative to GLKH folder. Added symlink to fix.
        par.write("""\
PROBLEM_FILE = {}
ASCENT_CANDIDATES = 500
MAX_CANDIDATES = 30
POPULATION_SIZE = 5
RUNS = 2
TRACE_LEVEL = 0
TIME_LIMIT = {}
TOUR_FILE = {}
SEED = {}
""".format(path, timeout / 2, tour_file, random.randint(0, int(1e8))))
    
    proc = subprocess.Popen([ './GLKH', par_file ], cwd='./GLKH', stdout=DEVNULL, stderr=DEVNULL)
    proc.wait()

    tour = []
    tour_section = False
    with open(tour_file, 'r') as tour_file:
        for line in tour_file:
            line = line.strip()
            if 'EOF' == line:
                break
            if tour_section:
                if '-1' == line:
                    tour_section = False
                    continue
                tour.append(int(line) - 1)
            elif 'TOUR_SECTION' == line:
                tour_section = True
    return tour

def run_glns(path, timeout=10):
    print('  Running GLNS on {} with timeout {}.'.format(path, timeout))
    # stdoutdata = subprocess.getoutput('julia GLNS/GLNScmd.jl ' + path + ' -max_time=' + str(timeout) + ' -trials=10000')
    proc = subprocess.Popen([ 'julia', '--depwarn=no', 'GLNS/GLNScmd.jl', path, '-max_time=' + str(timeout), '-trials=20', '-restarts=15' ],
            stdout=subprocess.PIPE)
    # proc = subprocess.Popen([ 'sleep', '100' ], stdout=subprocess.PIPE, preexec_fn=init_worker)
    tour = None
    i = 0
    while proc.poll() is None:
        err = False
        try:
            line = ''
            while True:
                char = proc.stdout.read(1)
                if not char:
                    break
                char = char.decode('utf-8')
                line += char
                if char == '\n' or char == '\r':
                    break
            if not line:
                break
            # line = line.decode('utf-8')
            i += 1
            if i % 240 == 0: # every ~2 min (0.5 sec per line)
                print('    ', line.rstrip()) # DEBUG

            if line.startswith('Cost'):
                # print(line)
                pass
            elif line.startswith('Tour Ordering'):
                # print(line)
                tour_str = line[line.index('['):].strip()
                tour = list(map(lambda n: n - 1, ast.literal_eval(tour_str)))
                # print(tour)
                break
            elif 'Exception' in line or 'ERROR' in line:
                err = True
            if err:
                print(line)
        except: # KeyboardInterrupt
            print('glns_interface exception')
            proc.terminate()
            raise
    
    #try:
    #    os.remove(path)
    #except OSError:
    #    pass
    return tour
    

"""
ASCENT_CANDIDATES = 13
BACKBONE_TRIALS = 0
BACKTRACKING = NO
# CANDIDATE_FILE =
CANDIDATE_SET_TYPE = ALPHA
EXCESS = 0.0714286
EXTRA_CANDIDATES = 0
EXTRA_CANDIDATE_SET_TYPE = QUADRANT
GAIN23 = YES
GAIN_CRITERION = YES
INITIAL_PERIOD = 1000
INITIAL_STEP_SIZE = 1
INITIAL_TOUR_ALGORITHM = WALK
# INITIAL_TOUR_FILE =
INITIAL_TOUR_FRACTION = 1.000
# INPUT_TOUR_FILE =
KICK_TYPE = 0
KICKS = 1
# MAX_BREADTH =
MAX_CANDIDATES = 13
MAX_SWAPS = 14
MAX_TRIALS = 1000
# MERGE_TOUR_FILE =
MOVE_TYPE = 5
# NONSEQUENTIAL_MOVE_TYPE = 5
# OPTIMUM =
OUTPUT_TOUR_FILE = 3burma14.$.tour
PATCHING_A = 1
PATCHING_C = 0
PI_FILE = PI_FILES/3burma14.pi
POPULATION_SIZE = 1
PRECISION = 10
PROBLEM_FILE = GTSPLIB/3burma14.gtsp
RESTRICTED_SEARCH = YES
RUNS = 1
SEED = 1
STOP_AT_OPTIMUM = YES
SUBGRADIENT = YES
# SUBPROBLEM_SIZE =
# SUBPROBLEM_TOUR_FILE =
SUBSEQUENT_MOVE_TYPE = 5
SUBSEQUENT_PATCHING = YES
# TIME_LIMIT =
# TOUR_FILE =
TRACE_LEVEL = 1
"""

