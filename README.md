# Conquer Group 119

## Usage

1. Use Python 3.6+
1. Clone GLNS into the GLNS folder (https://git.uwaterloo.ca/sl2smith/GLNS)
1. Optional: (Clone GLKH into the GLKH folder ... its a GTSP solver that doesn't work all that well)
1. Run `python solver_all.py [inputs]`

## How it works

This solver converts the conquer problem into a GTSP instance with
`2V + 2E + 1` vertices and `2E + 2` clusters. So it has some trouble
with dense graphs, but works very well given enough time.

## Code

Most of the code isn't used anymore. `solver.py` has a collection of ~27 greedy
algorithms that get run as backup, as well as special cases for complete graphs
and graphs that look like transformed TSP. The `*_utils.py` files have utils that
are still used. `gtsp.py` has utils for convert between conquer problems and
GTSP problems.
