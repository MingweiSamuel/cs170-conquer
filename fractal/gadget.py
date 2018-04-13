class Gadget:
    low_cost = 0.0001
    high_cost = 1e8

    """
    G: Graph of Gadget.
    cost: Cost of Gadget in current state. May be useful to scale this price.
    start: Starting node name.
    end: Ending node name.
    """
    def __init__(self, G, cost, start, end):
        self.G = G
        self.cost = cost
        self.start = start
        self.end = end
    
    """
    name: Name to make this sub-gadget unique.
    cost: Target cost to scale this sub-gadget to.
    returns: Graph instance.
    """
    def spawn(self, name, cost):
        scale = cost / self.cost

        G = self.G.copy()
        for _, _, data in G.edges(data=True):
            data['weight'] *= scale
        for _, data in G.nodes(data=True):
            data['weight'] *= scale
        # todo: rename
        return G

