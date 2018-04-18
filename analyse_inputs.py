import os

import networkx as nx
from functional import seq

import writer


# G, start = writer.readInFile('skeleton/inputs/373')
# print(len(G) + len(G.edges))

if __name__ == '__main__':
    path = 'skeleton/inputs/'

    complete = []
    tsp = []
    too_big = []
    biggest_size = 0
    biggest = ''

    sizes = [ [] for _ in range(30) ]

    files = os.listdir(path)
    # print(files)
    for fn in files:
        if not fn.endswith('.in'):
            continue
        # print(fn)
        fn = path + fn[:-3]
        G, start = writer.readInFile(fn)
        
        degrees = seq(G.degree()) \
            .map(lambda t: t[1]) \
            .count_by_value() \
            .to_list()

        size = len(G) + len(G.edges)

        if len(degrees) == 1:
            complete.append(fn)
        elif len(degrees) == 2:
            if degrees[0][1] == degrees[1][1]:
                print(degrees, fn)
                tsp.append(fn)
        elif size > 1500:
            too_big.append(fn)
            if size > biggest_size:
                biggest_size = size
                biggest = fn
        
        index = size // 100
        index = min(index, len(sizes) - 1)
        sizes[index].append(fn)
        
    print('complete: {}\n{}'.format(len(complete), complete))
    print('tsp: {}\n{}'.format(len(tsp), tsp))
    print('too_big: {}\n{}'.format(len(too_big), too_big))
    print('biggest: {} {}'.format(biggest_size, biggest))
    print(sizes[15])
