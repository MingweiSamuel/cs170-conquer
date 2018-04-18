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
import glns_interface
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
        prio = seq(G.nodes()).order_by(value_fn(G)).to_list()
        for node in prio:
            ds.remove(node)
            if not nx.is_dominating_set(G, ds):
                ds.add(node)
        return ds
    greedy_sub_ds_fn.__name__ += '({})'.format(value_fn.__name__)
    return greedy_sub_ds_fn


def greedy_tour(G, ds, start=None, all_paths=None):
    # first get shortest paths
    if all_paths:
        pred, dist, path = all_paths
    else:
        pred, dist, path = g_utils.floyd_warshall_all(G)

    tour = []
    unreached = set(ds)
    if start is not None:
        curr = start
        unreached.add(start) # silly, just get removes first thing
    else:
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

def solve_dominating_set_then_tsp(G, dominating_set_fn, tour_fn, start=None, all_paths=None):
    ds = dominating_set_fn(G)
    if not nx.is_dominating_set(G, ds):
        raise Exception('fn failed to make dominating set')
    tour = tour_fn(G, ds, start=start, all_paths=all_paths)
    # BAD TOUR
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
        prio = seq(G.nodes()).order_by(value_fn(G)).to_list()
        for node in prio:
            cds.remove(node)
            if not nx.is_dominating_set(G, cds) or \
                    not g_utils.is_connected_subset(G, cds):
                cds.add(node)
        return cds
    greedy_sub_cds_fn.__name__ += '({})'.format(value_fn.__name__)
    return greedy_sub_cds_fn




def solve_cds_christofides(G, cds_fn, start=None, all_paths=None):
    cds = cds_fn(G)
    if not nx.is_dominating_set(G, cds) or \
            not g_utils.is_connected_subset(G, cds):
        raise Exception('CDS fn did not return a valid CDS')

    # christofides
    # all pairs shortest dist graph (of original)
    if all_paths:
        pred, dist, path = all_paths
    else:
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
    if len(cds) > 1:
        stops = seq(nx.eulerian_circuit(G_euler)) \
                .map(lambda e: e[0]) \
                .to_list()
    else:
        stops = list(cds) # singleton or empty

    # Add the starting point if it is not added already
    stops = g_utils.insert_start_into_stops(stops, dist, path, start)

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

    if len(stops) > 1:
        tour = seq(pairwise(stops + [ stops[0] ])) \
                .flat_map(lambda e: path(e[0], e[1])) \
                .to_list()
    else:
        tour = stops[:]

    return tour, ds

def solve_complete(G, start):
    if not g_utils.is_complete(G):
        raise Exception('G is not complete')
    def value(v):
        return G.nodes[v]['weight'] + 0 if v == start else (2 * G[v][start]['weight'])
    best = seq(G.nodes).min_by(value)
    if best == start:
        return [ start ], { start }
    return [ start, best ], { best }

def solve_using_glns(G, start, timeout=None):
    G_str = g_utils.string_label(G)

    dist, ids, clusters, og_path = gtsp.conquer_to_gtsp(G_str, start)

    # timeout: size / 2
    if timeout is None:
        timeout = int(15 + (len(G) + len(G.edges)) / 2)

    tour_gtsp = glns_interface.run(dist, ids, clusters, timeout)
    # print(tour_gtsp)
    tour, ds = gtsp.mapped_gtsp_to_conquer_solution(tour_gtsp, start, ids, og_path)
    return tour, ds

def solve_transformed_tsp_using_glns(G, start, timeout=None):
    G_tsp, ids, dangling_dict = k_utils.untransform_tsp(G)
    clusters = set(G_tsp.nodes())

    def dist(u, v):
        return G_tsp[u][v]['weight']

    if timeout == None:
        timeout = len(G_tsp)
    tour_tsp = glns_interface.run(dist, ids, clusters, timeout)

    def should_capture_dangling(v):
        cost_v = G.nodes[v]['weight']
        d = dangling_dict[v]
        cost_d = G[v][d]['weight'] * 2 + G.nodes[d]['weight']
        return cost_d < cost_v
    def capture_node(v):
        if should_capture_dangling(v):
            return [ v, dangling_dict[v], v ]
        return [ v ]
    
    tour = seq(tour_tsp) \
            .flat_map(capture_node) \
            .to_list()
    ds = seq(tour_tsp) \
            .map(lambda v: dangling_dict[v] if should_capture_dangling(v) else v) \
            .to_set()
    return tour, ds



def print_solution_info(G, tour, ds, debug=True):
    k_utils.check(G, tour, ds)
    cost_tour, cost_ds = k_utils.cost(G, tour, ds)
    cost_total = cost_tour + cost_ds
    if debug:
        print('Cost: {:,.2f}, Tour: {:,.2f} ({:.2f}%), DS: {:,.2f} ({:.2f}%).' \
                .format(cost_total, cost_tour, 100 * cost_tour / cost_total, cost_ds, 100 * cost_ds / cost_total))
        print('Tour Len: {}, DS Len: {}'.format(len(tour), len(ds)))
        print(tour, ds)
        print()
    return cost_total

###

# rand.seed(0)






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
    run_all_greedy(G)


def run_all_greedy(G, start=0, debug=True):

    all_paths = g_utils.floyd_warshall_all(G)

    count = 0
    costs = []
    cds_fns = [
        make_greedy_sub_cds_fn(value_fn) for value_fn in value_fns
    ]
    for cds_fn in cds_fns:
        count += 1
        s = '{} {} {}'.format(count, solve_cds_christofides.__name__, cds_fn.__name__)
        if debug:
            print(s)
        tour, ds = solve_cds_christofides(G, cds_fn, start=start, all_paths=all_paths)
        c = print_solution_info(G, tour, ds, debug=debug)
        costs.append((c, s, tour, ds))



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
            if debug:
                print(s)
            tour, ds = solve_dominating_set_then_tsp(G, dominating_set_fn, tour_fn, start=start, all_paths=all_paths)
            c = print_solution_info(G, tour, ds, debug=debug)
            costs.append((c, s, tour, ds))

    costs.sort(key=lambda t: t[0])
    if debug:
        print('\n'.join(map(str, costs)))
    tour, ds = costs[0][2:]
    return tour, ds


# Max size (V+E) to run GLNS on a graph.
MAX_SIZE = 2250
def solve(G, start, debug=False):
    size = len(G) + len(G.edges)
    best = None
    best_cost = float('inf')

    if g_utils.is_complete(G):
        tour, ds = solve_complete(G, start)
        cost = print_solution_info(G, tour, ds, debug=debug)
        if cost < best_cost:
            best = (tour, ds)
            best_cost = cost
    elif k_utils.is_transformed_tsp(G):
        tour, ds = solve_transformed_tsp_using_glns(G, start)
        cost = print_solution_info(G, tour, ds, debug=debug)
        if cost < best_cost:
            best = (tour, ds)
            best_cost = cost
    elif size <= MAX_SIZE:
        tour, ds = solve_using_glns(G, start) # default timeout
        cost = print_solution_info(G, tour, ds, debug=debug)
        if cost < best_cost:
            best = (tour, ds)
            best_cost = cost

    tour, ds = run_all_greedy(G, start=start, debug=debug)
    # print('greedy')
    cost = print_solution_info(G, tour, ds, debug=debug)
    if cost < best_cost:
        best = (tour, ds)
        best_cost = cost
    
    return best
