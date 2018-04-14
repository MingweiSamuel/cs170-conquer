import argparse

import solver
import writer

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('name', type=str, help='Name of in/out file without extension')
    args = parser.parse_args()

    G, _ = writer.readInFile(args.name)

    tour, ds = writer.readOutFile(args.name)
    print('our solution')
    solver.print_solution_info(G, tour, ds)

    solver.run_everything(G)
