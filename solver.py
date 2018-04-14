import random as rand
from functional import seq
import networkx as nx
from networkx.utils import pairwise
import gen
import re
import gtsp
import writer
import graph_utils as g_utils
import skeleton.student_utils_sp18 as s_utils
import kingdom_utils as k_utils
from value_fns import value_fns


def greedy_additive_dominating_set(G):
    covered = set()
    ds = set()
    def value(node):
        new_covered = set(G.neighbors(node))
        new_covered.add(node)
        return len(new_covered - covered) / G.nodes[node]['weight']

    while len(covered) < len(G):
        node = seq(G.nodes()) \
                .filter(lambda n: not n in ds) \
                .max_by(value)
        covered.add(node)
        covered.update(G.neighbors(node))
        ds.add(node)

    return ds

def make_greedy_sub_ds_fn(value_fn):
    def greedy_sub_ds_fn(G):
        ds = set(G.nodes())
        prio = seq(G.nodes()).order_by(value_fn(G))
        for node in prio:
            ds.remove(node)
            if not nx.is_dominating_set(G, ds):
                ds.add(node)
        return ds
    greedy_sub_ds_fn.__name__ += '({})'.format(value_fn.__name__)
    return greedy_sub_ds_fn


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


# cds heuristics:
# - degree / weight
# - betweenness centrality from edge-weighted paths
# - betweenness centrality from edge and vertex-weighted paths
# - ?

# pruning heuristics:
# - max cost
# - min degree / cost

# connected dominating set + christofides

def make_greedy_sub_cds_fn(value_fn):
    def greedy_sub_cds_fn(G):
        cds = set(G.nodes())
        prio = seq(G.nodes()).order_by(value_fn(G))
        for node in prio:
            cds.remove(node)
            if not nx.is_dominating_set(G, cds) or \
                    not g_utils.is_connected_subset(G, cds):
                cds.add(node)
        return cds
    greedy_sub_cds_fn.__name__ += '({})'.format(value_fn.__name__)
    return greedy_sub_cds_fn




def solve_cds_christofides(G, cds_fn):
    cds = cds_fn(G)
    if not nx.is_dominating_set(G, cds) or \
            not g_utils.is_connected_subset(G, cds):
        raise Exception('CDS fn did not return a valid CDS')

    # christofides
    # all pairs shortest dist graph (of original)
    pred, dist, path = g_utils.floyd_warshall_all(G)

    # construct CDS tree
    G_tree = g_utils.minimum_connected_subset_spanning_tree(G, cds)

    # get odd degree nodes in trees
    odd = seq(G_tree.nodes()) \
            .filter(lambda n: G_tree.degree(n) % 2 == 1) \
            .to_list()

    G_matching = nx.Graph()
    G_matching.add_nodes_from(odd)
    max_dist = 0
    for a in odd:
        for b in odd:
            max_dist = max(max_dist, dist[a][b])
    for a in odd:
        for b in odd:
            # invert weights to find *minimal* matching (+1 for nonzero)
            G_matching.add_edge(a, b, weight=1 + max_dist - dist[a][b])
    match_edges = nx.max_weight_matching(G_matching)

    # eulerian multigraph
    G_euler = nx.MultiGraph(G_tree)
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
    stops = g_utils.remove_dupes(stops)

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
                        + dist[stops[stops.index(n) - 1]][n] + dist[n][stops[(stops.index(n) + 1) % len(stops)]] \
                        - dist[stops[stops.index(n) - 1]][stops[(stops.index(n) + 1) % len(stops)]])
                        # )
        # print('removing ' + str(to_remove))
        ds.remove(to_remove)
        stops.remove(to_remove)


    tour = seq(pairwise(stops + [ stops[0] ])) \
            .flat_map(lambda e: path(e[0], e[1])) \
            .to_list()

    return tour, ds



def print_solution_info(G, tour, ds):
    k_utils.check(G, tour, ds)
    cost_tour, cost_ds = k_utils.cost(G, tour, ds)
    cost_total = cost_tour + cost_ds
    print('Cost: {:,.2f}, Tour: {:,.2f} ({:.2f}%), DS: {:,.2f} ({:.2f}%).' \
            .format(cost_total, cost_tour, 100 * cost_tour / cost_total, cost_ds, 100 * cost_ds / cost_total))
    print('Tour Len: {}, DS Len: {}'.format(len(tour), len(ds)))
    print(tour, ds)
    print()
    return cost_total

###

rand.seed(0)


###
###

# file = open("att48_xy.txt","r")
# filelines = file.readlines()
# print(filelines)
# pos = [map(lambda x: int(x), re.split("\s+", line[:-1].strip())) for line in filelines]
# print(pos)
# G = nx.Graph()
# file.close()
# file = open("att48_s.txt","r")
# filelines = file.readlines()
# prev = None
# weight = 0.0
# file.close()
# for i in range(0, len(pos) - 1):
#     for j in range(i + 1, len(pos)):
#         w = ((pos[i][0] - pos[j][0])*(pos[i][0] - pos[j][0]) + \
#         (pos[i][1] - pos[j][1])*(pos[i][1] - pos[j][1]))**0.5
#         G.add_edge(i, j, weight = w)



# for line in filelines:
#     curr = int(line)
#     if curr and prev:
#         w = ((pos[curr - 1][0] - pos[prev - 1][0])*(pos[curr - 1][0] - pos[prev - 1][0]) + \
#         (pos[curr - 1][1] - pos[prev - 1][1])*(pos[curr - 1][1] - pos[prev - 1][1]))**0.5
#         weight += w
#         print(w)
#         G.add_edge(curr, prev, weight = w)
#     prev = curr
# clusters = [[i] for i in range(0, len(pos))]
#G = gtsp.gtsp_to_conquer(G, clusters)



#G = gen.random_graph_trick_nodes(200, 2, 0.02)
# G = gen.trapezoid_1()

# with open('gtsp/11eil51.txt') as f:
#     G, clusters = gtsp.read_text_gtsp(f)
# G = gtsp.gtsp_to_conquer(G, clusters)



# with open('gtsp/11eil51.solution.txt') as f:
#     _, tour = gtsp.read_solution_gtsp(f)
# print('known solution')
# tour, ds = gtsp.gtsp_to_conquer_solution(clusters, tour)
# print_solution_info(G, tour, ds)






if __name__ == '__main__':
    from baf14st70 import G, clusters, tour

    G = gtsp.gtsp_to_conquer(G, clusters)
    print(len(G))
    writer.scale(G)
    for _, _, data in G.edges(data=True):
        data['weight'] += 0.00004

    print('known solution')
    tour, ds = gtsp.gtsp_to_conquer_solution(clusters, tour)
    print_solution_info(G, tour, ds)

    writer.writeInFile("set200", tour[0], G)
    writer.writeOutFile("set200", tour, ds)

    gen.check(G)


    #
    run_everything(G)


def run_everything(G):
    count = 0
    costs = []
    cds_fns = [
        make_greedy_sub_cds_fn(value_fn) for value_fn in value_fns
    ]
    for cds_fn in cds_fns:
        count += 1
        s = '{} {} {}'.format(count, solve_cds_christofides.__name__, cds_fn.__name__)
        print(s)
        tour, ds = solve_cds_christofides(G, cds_fn)
        c = print_solution_info(G, tour, ds)
        costs.append((c, s))



    dominating_set_fns = [
        greedy_additive_dominating_set
    ]
    dominating_set_fns.extend([ make_greedy_sub_ds_fn(value_fn) for value_fn in value_fns ])

    tour_fns = [
        greedy_tour,
        g_utils.christofides_tour,
        g_utils.nearest_detour_tour,
    ]

    for dominating_set_fn in dominating_set_fns:
        for tour_fn in tour_fns:
            count += 1
            s = '{} {} {} {}'.format(count, solve_dominating_set_then_tsp.__name__, dominating_set_fn.__name__, tour_fn.__name__)
            print(s)
            tour, ds = solve_dominating_set_then_tsp(G, dominating_set_fn, tour_fn)
            c = print_solution_info(G, tour, ds)
            costs.append((c, s))

    costs.sort(key=lambda t: t[0])
    print('\n'.join(map(str, costs)))
    
