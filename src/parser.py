from macro import Macro
from net import Net


def parse_nodes(file_path: str) -> dict[str:Macro]:
    """
    Parse the .nodes file to extract macro information.
    :param file_path: Path to the .nodes file.
    :return: Dictionary of macros with their names as keys.
    """
    
    if not file_path.endswith(".nodes"):
        raise ValueError(f"Invalid file type: {file_path}. Expected a .nodes file.")
    
    num_nodes = 0
    num_terminals = 0
    nodes_flag = False
    terminals_flag = False
    macros = {}

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("NumNodes"):
                num_nodes = int(line.split(":")[1])
                nodes_flag = True
                continue
            elif line.startswith("NumTerminals"):
                num_terminals = int(line.split(":")[1])
                terminals_flag = True
                continue
            
            if not nodes_flag or not terminals_flag:
                continue

            macro_info = line.split()

            name = macro_info[0]
            width = float(macro_info[1])
            height = float(macro_info[2])
            rotation = "0"

            fixed = False
            if len(macro_info) > 3 and macro_info[3].lower() == "terminal":
                fixed = True

            macro = Macro(name, width, height, rotation, fixed)

            macros[name] = macro
    
    return macros



def parse_pl(file_path: str, macros: dict[str, Macro]) -> None:
    """
    Parse the .pl file to set the positions of macros.
    :param file_path: Path to the .scl file.
    :param macros: Dictionary of macros with their names as keys.
    """
    if not macros:
        print("No macros to set positions for.")
        return
    
    if not file_path.endswith(".pl"):
        raise ValueError(f"Invalid file type: {file_path}. Expected a .scl file.")

    with open(file_path, 'r') as file:
        start_flag = False
        for line in file:
            if line.strip() == "":
                start_flag = True
                continue

            if not start_flag:
                continue

            pos = line.split()
            
            name = pos[0]
            x = float(pos[1])
            y = float(pos[2])

            macro = macros[name]
            macro.set_position(x,y)

    return


def parse_nets(file_path: str, macros: dict[str, Macro]) -> dict[str, Net]:
    """
    Parse the .net file to extract net information.
    :param file_path: Path to the .net file.
    :param macros: Dictionary of macros with their names as keys.
    :return: Dictionary of nets with their names as keys.
    """
    
    if not file_path.endswith(".nets"):
        raise ValueError(f"Invalid file type: {file_path}. Expected a .net file.")
    
    nets = {}
    start = False

    with open(file_path, 'r') as file:
        net_name = ""
        for line in file:
            if line.startswith("NetDegree"):
                start = True
                net_name = line.split(":")[1].split()[1]
                if net_name not in nets:
                    nets[net_name] = Net(net_name)
                continue

            if not start:
                continue

            split_line = line.split(":")
            info = split_line[0]
            loc = split_line[1]
            info_split = info.split()
            loc_split = loc.split()

            macro_name = info_split[0]
            port_type = info_split[1]
            x_loc = float(loc_split[0])
            y_loc = float(loc_split[1])

            if macro_name not in macros:
                raise ValueError(f"Macro '{macro_name}' not found in macros dictionary.")
            
            net: Net = nets[net_name]
            macro: Macro = macros[macro_name]

            if port_type == "I":
                idx = macro.add_in_port(net_name, x_loc, y_loc)
                net.add_in_macro(macro, idx)
            elif port_type == "O":
                idx = macro.add_out_port(net_name, x_loc, y_loc)
                net.add_out_macro(macro, idx)
            elif port_type == "B":
                idx = macro.add_external_port(net_name, x_loc, y_loc)
                net.add_external_macro(macro, idx)
            else:
                raise ValueError(f"Invalid port type '{port_type}' for macro '{macro_name}' in net '{net_name}'.")

    return nets


    
    
