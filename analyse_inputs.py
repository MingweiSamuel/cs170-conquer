import os

import networkx as nx
from functional import seq

import solver
import writer
import graph_utils as g_utils
import kingdom_utils as k_utils

# 415
# 300 sec
#
# GLNS
# Cost: 2,167.00, Tour: 1,842.00 (85.00%), DS: 325.00 (15.00%).
# Tour Len: 25, DS Len: 23
# [116, 115, 188, 189, 190, 63, 64, 183, 163, 51, 169, 170, 148, 79, 78, 165, 146, 147, 108, 109, 110, 180, 196, 199, 0] {146, 147, 148, 163, 165, 169, 170, 51, 183, 188, 189, 190, 63, 64, 196, 199, 78, 79, 108, 109, 110, 115, 116}
# 
# greedy
# Cost: 2,904.00, Tour: 2,618.00 (90.15%), DS: 286.00 (9.85%).
# Tour Len: 32, DS Len: 24
# [0, 1, 30, 85, 93, 94, 43, 133, 41, 78, 79, 148, 60, 61, 62, 109, 96, 188, 82, 183, 82, 66, 49, 59, 16, 188, 115, 173, 143, 57, 196, 199] {1, 66, 196, 133, 79, 16, 143, 82, 148, 85, 30, 94, 96, 41, 43, 109, 173, 49, 188, 115, 183, 57, 60, 62}


# 180: 1867
# 800 sec
# GLNS
# Cost: 2,653.00, Tour: 1,358.00 (51.19%), DS: 1,295.00 (48.81%).
# Tour Len: 19, DS Len: 13
# [0, 43, 28, 88, 35, 89, 6, 79, 47, 48, 63, 4, 3, 56, 14, 97, 40, 11, 10] {0, 3, 35, 4, 6, 40, 10, 43, 11, 14, 47, 48, 28}
# 
# greedy
# Cost: 2,687.00, Tour: 1,534.00 (57.09%), DS: 1,153.00 (42.91%).
# Tour Len: 22, DS Len: 13
# [0, 10, 11, 40, 97, 47, 48, 81, 30, 79, 6, 75, 32, 88, 35, 88, 28, 97, 14, 56, 3, 66] {0, 3, 6, 10, 11, 14, 28, 30, 32, 35, 40, 47, 48}

G, names, start = writer.readInFile('skeleton/inputs/114')
# print(G.nodes[8])
print(len(G) + len(G.edges))
print(k_utils.is_transformed_tsp(G))
print(g_utils.is_complete(G))

if __name__ == '__main__':
    path = 'skeleton/inputs/'

    complete = []
    tsp = []
    too_big = []
    biggest_size = 0
    biggest = ''
    time_est = 0
    time_glns = 0
    size_1000_2250 = []
    size_3000_plus = []

    sizes = [ [] for _ in range(30) ]

    files = os.listdir(path)
    # print(files)
    for fn in files:
        if not fn.endswith('.in'):
            continue
        # print(fn)
        fn = path + fn[:-3]
        G, names, start = writer.readInFile(fn)
        
        degrees = seq(G.degree()) \
            .map(lambda t: t[1]) \
            .count_by_value() \
            .to_list()

        size = len(G) + len(G.edges)

        if 1000 <= size <= 2250:
            size_1000_2250.append(fn.split('/')[-1])
        elif 3000 <= size:
            size_3000_plus.append(fn.split('/')[-1])

        if len(degrees) == 1:
            time_est += 30
            complete.append(fn)

        elif k_utils.is_transformed_tsp(G):
            time_est += 15 + len(G)
            tsp.append(fn)

        elif size > solver.MAX_SIZE:
            time_est += 100 # Without GLNS

            too_big.append(fn)

        else: # Normal, with GLNS
            time_est += 100 + size
            time_glns += 5 + size

        if size > biggest_size and not g_utils.is_complete(G) and not k_utils.is_transformed_tsp(G):
            biggest_size = size
            biggest = fn
        
        index = size // 100
        index = min(index, len(sizes) - 1)
        sizes[index].append(fn)
        
    print('complete: {}\n{}'.format(len(complete), complete))
    print('tsp: {}\n{}'.format(len(tsp), tsp))
    print('too_big: {}\n{}'.format(len(too_big), too_big))
    print('biggest: {} {}'.format(biggest_size, biggest))
    print('time_est: {}'.format(time_est))
    print('time_glns: {}'.format(time_glns))
    print('size_1000_2250: {}'.format(','.join(size_1000_2250)))
    print('size_3000_plus: {}'.format(','.join(size_3000_plus)))
    # behind in: 102,108,160,177,18,180,189,205,211,241,306,322,351,360,366,373,387,415,427,429,438,453,460,478,480,487,52,53,534,537,564,568,574,583,603,610,613,658,664,667,678,685,693,722,93,99
    #print(sizes[18])
    
