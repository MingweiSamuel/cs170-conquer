import networkx as nx
import gen
import random
from networkx.utils import pairwise

def writeGraphFile(name, start, G): #name : String, start : String, G : networkx
    f = open( name + ".in","w+")
    f.write(str(G.number_of_nodes()) + "\n")
    nodes = G.nodes()
    for n in nodes:
        f.write(str(n) + " ")
    f.write("\n")
    f.write(str(start) + "\n")
    for n in nodes:
        for nn in nodes:
            if nn in G[n]:
                f.write(str(G[n][nn]["weight"]) + " ")
            else:
                f.write("x ")
        f.write("\n")
    f.close()

random.seed();
G = gen.random_connected_graph(10, 5, 0.1)
writeGraphFile("test", 1, G)
print(nx.is_connected(G))
print(G.nodes())
print(G.edges())
