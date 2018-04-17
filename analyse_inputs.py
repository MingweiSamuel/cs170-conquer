import writer
import os

if __name__ == '__main__':
    path = 'skeleton/inputs/'

    complete = 0

    files = os.listdir(path)
    print(files)
    for fn in files:
        if not fn.endswith('.in'):
            continue
        print(fn)
        fn = path + fn[:-3]
        G, start = writer.readInFile(fn)
        if len(G) * (len(G) - 1) == 2 * len(G.edges):
            complete += 1
    print('complete: {}'.format(complete))
