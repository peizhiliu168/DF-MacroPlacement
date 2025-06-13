import os

from macro import Macro
from net import Net
from parser import parse_nodes, parse_pl, parse_nets

def get_subset_nets(macros: dict[str, Macro], nets: dict[str, Net]):
    macro_subset = set()
    net_subset = set()
    max_nets = 500
    for i, (net_name, net) in enumerate(nets.items()):
        if i >= max_nets:
            break

        net_macros = net.get_in_macro() + net.get_out_macro() + net.get_external_macro()
        macro_subset.update([macro.name for macro, _ in net_macros])
        net_subset.add(net_name)

    return macro_subset, net_subset

def generate_nodes_file(macros: list[Macro], file_path: str):
    with open(file_path, 'w') as f:
        f.write(f"NumNodes :  {len(macros)}\n")
        f.write(f"NumTerminals :  {sum(1 for macro in macros if macro.fixed)}\n")
        for macro in macros:
            f.write(f"{macro.name} {macro.dim[0]} {macro.dim[1]} ")
            if macro.fixed:
                f.write("terminal")
            f.write("\n")

def generate_pl_file(macros: list[Macro], file_path: str):
    with open(file_path, 'w') as f:
        f.write("\n")
        for macro in macros:
            f.write(f"{macro.name} {macro.pos[0]} {macro.pos[1]} : N ")
            if macro.fixed:
                f.write("/FIXED")
            f.write("\n")


def generate_nets_file(nets: list[Net], file_path: str):
    with open(file_path, 'w') as f:
        f.write(f"NumNets :  {len(nets)}\n")
        f.write(f"NumPins :  {sum(net.get_degree() for net in nets)}\n")

        for net in nets:
            f.write(f"NetDegree : {net.get_degree()} {net.name}\n")
            for macro, idx in net.get_in_macro():
                r = macro.get_port(idx)['r']
                f.write(f"\t{macro.name} I : {r[0]} {r[1]}\n")
            for macro, idx in net.get_out_macro():
                r = macro.get_port(idx)['r']
                f.write(f"\t{macro.name} O : {r[0]} {r[1]}\n")
            for macro, idx in net.get_external_macro():
                r = macro.get_port(idx)['r']
                f.write(f"\t{macro.name} B : {r[0]} {r[1]}\n")

if __name__ == "__main__":
    bench = "/home/peizhi/Documents/2025_Spring_Classes/DFMP/bench/adaptec1"
    node_file = None
    pl_file = None
    net_file = None
    for file in os.listdir(bench):
        if file.endswith(".nodes"):
            node_file = os.path.join(bench, file)
        elif file.endswith(".pl"):
            pl_file = os.path.join(bench, file)
        elif file.endswith(".nets"):
            net_file = os.path.join(bench, file)

    if not node_file:
        print(f"No .node file found in {bench}")
        exit(1)
    
    # Parse the nodes from the .node file
    # print(f"Parsing nodes from {node_file}")
    macros = parse_nodes(node_file)
    print(f"Parsed {len(macros)} macros from {node_file}")
    # print(macros)
    
    if not pl_file:
        print(f"No .pl file found in {bench}, skipping placement.")
        exit(1)
    
    # Parse the placement from the .pl file
    parse_pl(pl_file, macros)
    
    if not net_file:
        print(f"No .nets file found: {net_file}.")
        exit(1)
    
    # Parse the nets from the .nets file
    nets = parse_nets(net_file, macros)
    # print(nets)
    print(f"Parsed {len(nets)} nets from {net_file}")

    # Get a subset of nets and macros
    subset_macros, subset_nets = get_subset_nets(macros, nets)

    macro_list = [macros[name] for name in subset_macros]
    net_list = [nets[name] for name in subset_nets]

    out_dir = "/home/peizhi/Documents/2025_Spring_Classes/DFMP/bench/adaptec1_500"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    basename = os.path.basename(out_dir)
    generate_nodes_file(macro_list, os.path.join(out_dir, f"{basename}.nodes"))
    generate_pl_file(macro_list, os.path.join(out_dir, f"{basename}.pl"))
    generate_nets_file(net_list, os.path.join(out_dir, f"{basename}.nets"))

