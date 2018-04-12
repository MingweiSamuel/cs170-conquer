import networkx as nx
import gen
from networkx.utils import pairwise

def writeGraphFile(name, start, G): #name : String, start : String, G : networkx
    f = open(name + ".in","w+")
    f.write(str(G.number_of_nodes()) + "\n")
    nodes = g.nodes()
    for n in nodes:
        f.write(str(n) + " ")
    f.write("\n")
    f.write(start + "\n")
    for n in nodes:
        for nn in nodes:
            if nn in G[n]:
                f.write(G[n][nn]["weight"] + " ")
            else:
                f.write("x ")
        f.write("\n")
    f.close()

def main():
    G = gen.random_connected_graph(5, 3, 0.01)
    print(nx.is_connected(G))
