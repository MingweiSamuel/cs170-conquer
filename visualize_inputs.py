import os

import networkx as nx
import numpy as np
from functional import seq
from PIL import Image

import writer


if __name__ == '__main__':
    path = 'skeleton/inputs/'

    files = os.listdir(path)
    for fn in files:
        if not fn.endswith('.in'):
            continue
        # print(fn)
        G, start = writer.readInFile(path + fn[:-3])

        a = nx.to_numpy_matrix(G)
        a = np.array(a)
        og_shape = a.shape
        
        a = a.flatten()
        # print(a)
        a[a > 0] = 1 + np.log(a[a > 0])
        if np.max(a):
            a = 255 * a / np.max(a)

        a = np.reshape(a, og_shape)

        # add nodes
        node_max = 0
        for i, vd in enumerate(G.nodes(data=True)):
            a[i][i] = vd[1]['weight']
            node_max = max(node_max, a[i][i])
        for i in range(len(G.nodes)):
            a[i][i] = 255 * a[i][i] / node_max

        im = Image.fromarray(a.astype(np.uint8), mode='L')
        # im = im.resize((140, 140))
        im.save('input_images/' + fn[:-3] + '.png')
        
        # minval = np.min(a[np.nonzero(a)])
        # maxval = np.max(a[np.nonzero(a)])
        # for i in range(a.shape[0]):
        #     for j in range(a.shape[1]):

        # break

        # w, h = 512, 512
        # data = np.zeros((h, w, 3), dtype=np.uint8)
        # data[256, 256] = [255, 0, 0]
        # img = Image.fromarray(data, 'RGB')
        # img.save('my.png')

        
     
