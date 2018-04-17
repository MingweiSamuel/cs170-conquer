import os

from functional import seq

import writer

if __name__ == '__main__':
    path = 'skeleton/inputs/'

    complete = []
    tsp = []
    too_big = []

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

        if len(degrees) == 1:
            complete.append(fn)
        elif len(degrees) == 2:
            if degrees[0][1] == degrees[1][1]:
                tsp.append(fn)
        elif len(G) + len(G.edges) > 1500:
            too_big.append(fn)
        
    print('complete: {}\n{}'.format(len(complete), complete))
    print('tsp: {}\n{}'.format(len(tsp), tsp))
    print('too_big: {}\n{}'.format(len(too_big), too_big))
