import scipy
import numpy as np
import scipy.optimize
from tqdm import tqdm

from macro import Macro
from net import Net

class OrientEngine():
    def __init__(self, macros: dict[str:Macro], nets: dict[str:Net]):
        self.macros = macros
        self.nets = nets
        self.macro2index = {name: i for i, name in enumerate(macros.keys())}
        self.index2macro = {i: name for i, name in enumerate(macros.keys())}

        self.rot_vec = np.array([0.0 for _ in range(len(macros))])
        
    def run(self):

        def f(x):
            tau_vec = np.zeros(len(self.macros))

            # Set the rotation for each macro
            for idx, m_name in self.index2macro.items():
                macro: Macro = self.macros[m_name]

                # Update macro rotation
                rot_deg = x[idx]
                macro.set_rotation(rot_deg)

            # Compute torque balance for each macro
            for idx, m_name in tqdm(self.index2macro.items(), desc="Computing torque", total=len(self.index2macro)):
                macro: Macro = self.macros[m_name]

                tau = np.zeros(3)

                ports = {}
                ports.update(macro.get_in_ports())
                ports.update(macro.get_out_ports())

                # For each port, iterate over all the ports
                for port_idx, port in ports.items():
                    r_vec = macro.compute_port_r(port_idx)
                    r_vec = np.concatenate([r_vec, [0.0]])  # Add z-component

                    macro_loc = macro.compute_port_loc(port_idx)
                    net: Net = self.nets[port["net"]]

                    connected_ports = net.get_in_macro() + net.get_out_macro()
                    
                    # For each port, all nodes in the net applies some force to the port,
                    # inducing some amount of torque. Only force from other macros is considered.
                    for connected_macro, connected_port_idx in connected_ports:
                        if connected_macro.name == macro.name:
                            continue

                        connected_macro_loc = connected_macro.compute_port_loc(connected_port_idx)
                        f_vec = connected_macro_loc - macro_loc

                        f_vec = np.concatenate([f_vec, [0.0]])  # Add z-component

                        tau += np.cross(r_vec, f_vec)
                        
                tau_vec[idx] = tau[-1]

            print("Torque vector:", tau_vec)
            return tau_vec
        
        
        opt_rot_vec = scipy.optimize.newton(f, self.rot_vec)
        self.rot_vec = opt_rot_vec



if __name__ == "__main__":
    import os
    from parser import parse_nodes, parse_pl, parse_nets

    # bench = "/home/peizhi/Documents/2025_Spring_Classes/DFMP/test/simple"
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
    print(f"Parsing nodes from {node_file}")
    macros = parse_nodes(node_file)
    print(macros)
    
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
    print(nets)
    print(f"Parsed {len(nets)} nets from {net_file}")

    # Create the orient engine
    orient_engine = OrientEngine(macros, nets)
    # Run the orient engine
    orient_engine.run()
    print("Rotation vector:", orient_engine.rot_vec)