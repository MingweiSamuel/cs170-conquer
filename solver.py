import random as rand
from functional import seq
import networkx as nx
from networkx.utils import pairwise
import gen
import graph_utils as g_utils
import skeleton.student_utils_sp18 as s_utils
import munkres
import kingdom_utils as k_utils

def greedy_subtractive_dominating_set(G, value_fn):
    ds = set(G.nodes())
    prio = seq(G.nodes()).order_by(value_fn)
    for node in prio:
        ds.remove(node)
        if not nx.is_dominating_set(G, ds):
            ds.add(node)
    return ds

def greedy_weight_subtractive_dominating_set(G):
    return greedy_subtractive_dominating_set(G, lambda n: -G.nodes[n]['weight'])

def greedy_degree_per_weight_subtractive_dominating_set(G):
    return greedy_subtractive_dominating_set(G, lambda n: G.degree[n] / G.nodes[n]['weight'])

def greedy_additive_dominating_set(G):
    covered = set()
    ds = set()
    def value(node):
        new_covered = set(G.neighbors(node))
        new_covered.add(node)
        return len(new_covered - covered)

    while len(covered) < len(G):
        node = seq(G.nodes()) \
                .filter(lambda n: not n in ds) \
                .max_by(value)
        covered.add(node)
        covered.update(G.neighbors(node))
        ds.add(node)
    
    return ds

def greedy_tour(G, ds):
    # first get shortest paths
    pred, dist, path = g_utils.floyd_warshall_all(G)

    tour = []
    unreached = set(ds)
    curr = rand.choice(list(ds))
    while True:
        unreached.remove(curr)
        if not unreached:
            break
        # find next
        nex = seq(unreached) \
            .min_by(lambda n: dist[curr][n])
        tour.extend(path(curr, nex))
        curr = nex
    tour.extend(path(curr, tour[0]))

    return tour

def solve_dominating_set_then_tsp(G, dominating_set_fn, tour_fn):
    ds = dominating_set_fn(G)
    if not nx.is_dominating_set(G, ds):
        raise Exception('fn failed to make dominating set')
    tour = tour_fn(G, ds)
    k_utils.check(G, tour, ds)

    return tour, ds


# bcop heuristics:
# - degree / weight
# - betweenness centrality from edge-weighted paths
# - betweenness centrality from edge and vertex-weighted paths
# - ?

# pruning heuristics:
# - max cost
# - min degree / cost

def solve_degree_per_weight_bcop_christofides(G):
    cds = set(G.nodes())
    prio = list(G.nodes(data=True))
    prio.sort(key=lambda x: G.degree(x[0]) / x[1]['weight'])
    # greedily remove nodes by lowest degree / weight, maintaining connectedness
    for node, _ in prio:
        cds.remove(node)
        if not nx.is_dominating_set(G, cds) or \
                not g_utils.is_connected_subset(G, cds):
            cds.add(node) # add it back

    # chritofides algorithm

    # all pairs shortest dist graph (of original)
    pred, dist, path = g_utils.floyd_warshall_all(G)
    
    # construct CDS tree
    G_tree = g_utils.minimum_subset_spanning_tree(G, cds)

    # get odd degree nodes in trees
    odd = seq(G_tree.nodes()) \
            .filter(lambda n: G_tree.degree(n) % 2 == 1) \
            .to_list()

    G_matching = nx.Graph()
    G_matching.add_nodes_from(odd)
    # print(odd)
    for a in odd:
        for b in odd:
            # invert weights to find minimal matching
            G_matching.add_edge(a, b, weight=1 / (1 + dist[a][b]))
    match_edges = nx.max_weight_matching(G_matching)
    # print(match_edges)


    # # all-pairs cost matrix of odd vertices
    # matrix = [ [ dist[a][b] if a != b else munkres.DISALLOWED for b in odd ] for a in odd ]
    # # O(n^3) Munkres (Hungarian) algorithm for min-weight perfect pairing
    # # http://software.clapper.org/munkres/api/index.html
    # m = munkres.Munkres()
    # # (a, b) or (b, a) pairs
    # indices = m.compute(matrix)

    # eulerian multigraph
    G_euler = nx.MultiGraph(G_tree)
    # print('deg:', G_tree.degree())
    # # print(indices)
    # for i, j in indices:
    #     if j >= i: # prevent dupes
    #         continue
    #     G_euler.add_edge(odd[i], odd[j], weight=matrix[i][j])
    
    for a, b in match_edges:
        G_euler.add_edge(a, b, weight=dist[a][b])
    if not nx.is_eulerian(G_euler):
        raise Exception('New G_euler not eulerian')

    # All vertices now have even degree. We construct a eulerian tour.
    # This doesn't contain all the "bridge" vertices we need for the
    # added "indices". Hence it is called "stops" as in "tour stops"
    # rather than "tour".
    stops = seq(nx.eulerian_circuit(G_euler)) \
            .map(lambda e: e[0]) \
            .to_list()

    # TODO smart cutting short
    stops = remove_dupes(stops)

    # remove extra from cds (connected dominating set) to make ds (dominating set)
    ds = set(cds)
    while True:
        can_remove = seq(ds) \
                .filter(lambda n: nx.is_dominating_set(G, ds - set([ n ]))) \
                .to_list()
        if not can_remove:
            break
        to_remove = seq(can_remove) \
                .max_by(lambda n: G.nodes[n]['weight'] \
                        + dist[stops.index(n) - 1][n] + dist[n][(stops.index(n) + 1) % len(dist)] \
                        - dist[stops.index(n) - 1][stops.index(n) + 1])
                        # )
        # print('removing ' + str(to_remove))
        ds.remove(to_remove)
        stops.remove(to_remove)

    
    tour = seq(pairwise(stops + [ stops[0] ])) \
            .flat_map(lambda e: path(e[0], e[1])) \
            .to_list()

    return tour, ds

def remove_dupes(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def print_solution_info(G, tour, ds):
    k_utils.check(G, tour, ds)
    cost_tour, cost_ds = k_utils.cost(G, tour, ds)
    cost_total = cost_tour + cost_ds
    print('Cost: {:,.2f}, Tour: {:,.2f} ({:.2f}%), DS: {:,.2f} ({:.2f}%).' \
            .format(cost_total, cost_tour, 100 * cost_tour / cost_total, cost_ds, 100 * cost_ds / cost_total))
    print('Tour Len: {}, DS Len: {}'.format(len(tour), len(ds)))
    print()

rand.seed(0)

G = gen.random_graph(200, 2, 0.02)
gen.check(G)


tour, ds = solve_degree_per_weight_bcop_christofides(G)
print('smart')
print_solution_info(G, tour, ds)


dominating_set_fns = [
    greedy_additive_dominating_set,
    greedy_weight_subtractive_dominating_set,
    greedy_degree_per_weight_subtractive_dominating_set
]
tour_fns = [ greedy_tour ]
for dominating_set_fn in dominating_set_fns:
    for tour_fn in tour_fns:
        print('{} {} {}'.format(solve_dominating_set_then_tsp.__name__, dominating_set_fn.__name__, tour_fn.__name__))
        tour, ds = solve_dominating_set_then_tsp(G, dominating_set_fn, tour_fn)
        print_solution_info(G, tour, ds)

