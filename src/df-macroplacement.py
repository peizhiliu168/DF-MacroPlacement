from parser import parse_nodes, parse_pl, parse_nets, parse_scl
from sa_engine import SAEngine
from utils import output_macros


def main(bench):
    # Find the .node file in the benchmark directory

    import os
    node_file = None
    pl_file = None
    net_file = None
    scl_file = None
    for file in os.listdir(bench):
        if file.endswith(".nodes"):
            node_file = os.path.join(bench, file)
        elif file.endswith(".pl"):
            pl_file = os.path.join(bench, file)
        elif file.endswith(".nets"):
            net_file = os.path.join(bench, file)
        elif file.endswith(".scl"):
            scl_file = os.path.join(bench, file)

    if not node_file:
        print(f"No .node file found in {bench}")
        return
    
    # Parse the nodes from the .node file
    macros = parse_nodes(node_file)
    
    if not pl_file:
        print(f"No .pl file found in {bench}, skipping placement.")
        return
    
    # Parse the placement from the .pl file
    parse_pl(pl_file, macros)
    
    if not net_file:
        print(f"No .nets file found: {net_file}.")
        return
    
    # Parse the nets from the .nets file
    nets = parse_nets(net_file, macros)
    print(f"Parsed {len(nets)} nets from {net_file}")

    if not scl_file:
        print(f"No .scl file found: {scl_file}.")
        return
    
    # Parse the scale from the .scl file
    x_min = y_min = 0.0
    x_max, y_max = parse_scl(scl_file)

    # Run the simulated annealing engine
    sa_engine = SAEngine(macros, nets, (x_min, x_max), (y_min, y_max))
    sa_engine.run()
    sa_engine.update_macro_positions()

    # Output the final macro positions
    output_file = os.path.join(bench, "final_placement.pl")
    out_macros = [macro for macro in macros.values()]
    output_macros(out_macros, output_file)
    print(f"Final placement written to {output_file}")

    return


    


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python df-macroplacement.py <benchmark_directory>")
        sys.exit(1)

    benchmark_directory = sys.argv[1]
    main(benchmark_directory)