import subprocess
import ast

import gtsp

def run(G_gtsp, clusters, timeout=10):
    """
    G: gtsp graph (complete).
    """
    path = 'GLNS/inputs/temp_interface.txt'
    with open(path, 'w+') as output_file:
        gtsp.output_gtsp(output_file, G_gtsp, clusters, name='temp_interface')
    stdoutdata = subprocess.getoutput('julia GLNS/GLNScmd.jl ' + path + ' -max_time=' + str(timeout) + ' -trials=100000')
    lines = stdoutdata.split('\n')
    for line in lines:
        if line.startswith('Cost'):
            print(line)
        if line.startswith('Tour Ordering'):
            print(line)
            tour_str = line[line.index('['):].strip()
            tour = list(map(lambda n: n - 1, ast.literal_eval(tour_str)))
            print(tour)
            return tour
    