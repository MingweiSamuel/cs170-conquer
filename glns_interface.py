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


def run(dist, ids, clusters, timeout=10):
    """
    G: gtsp graph (complete).
    """
    path = 'GLNS/inputs/temp_interface_{}_{}.txt'.format(os.getpid(), random.randint(0, int(1e9)))
    with open(path, 'w+') as output_file:
        gtsp.output_gtsp(output_file, dist, ids, clusters, name='temp_interface')
    print('Done writing {}. Running GLNS with timeout {}.'.format(path, timeout))


    # stdoutdata = subprocess.getoutput('julia GLNS/GLNScmd.jl ' + path + ' -max_time=' + str(timeout) + ' -trials=10000')
    proc = subprocess.Popen([ 'julia', '--depwarn=no', 'GLNS/GLNScmd.jl', path, '-max_time=' + str(timeout), '-trials=10000'],
            stdout=subprocess.PIPE)
    # proc = subprocess.Popen([ 'sleep', '100' ], stdout=subprocess.PIPE, preexec_fn=init_worker)
    tour = None
    while proc.poll() is None:
        err = False
        try:
            line = proc.stdout.readline()
            if line is None:
                break
            line = line.decode('utf-8')
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
    
    try:
        os.remove(path)
    except OSError:
        pass
    return tour


    # lines = stdoutdata.split('\n')
    # for line in lines:
    #     if line.startswith('Cost'):
    #         # print(line)
    #         pass
    #     if line.startswith('Tour Ordering'):
    #         # print(line)
    #         tour_str = line[line.index('['):].strip()
    #         tour = list(map(lambda n: n - 1, ast.literal_eval(tour_str)))
    #         # print(tour)
    #         return tour
    # print(lines)
    
