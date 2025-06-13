import numpy as np

class Macro:
    def __init__(self, name: str, width: float, height: float, rotation: float = 0.0, fixed: bool = False):
        """
        Initialize a Macro object.
        :param name: Name of the macro.
        :param width: Width of the macro.
        :param height: Height of the macro.
        :param rotation: Rotation in degrees of the macro (default is "0").
        :param fixed: Whether the macro is fixed (default is False).
        """
        self.name = name
        self.dim = np.array([width, height], dtype=float)
        self.rotation = rotation
        self.fixed = fixed

        # Position of the macro in the layout - top-left corner
        self.pos = np.array([0.0, 0.0], dtype=float)
        self.com = self.dim / 2.0

        # Ports ports
        self.port_idx = 0
        self.in_ports: dict[int:dict] = {} 
        self.out_ports: dict[int:dict] = {}
        self.external_ports: dict[int:dict] = {} 
        self.pos2idx: dict[tuple[float, float]:int] = {}


    def set_position(self, x: float, y: float):
        """Set the position of the macro in the layout."""
        self.pos = np.array([x, y], dtype=float)


    def set_rotation(self, rotation: float):
        """Set the rotation of the macro."""
        self.rotation = rotation


    def _add_port(self, ports: dict, net_name: str, x_loc: float, y_loc: float, port_type: str):
        r = np.array([x_loc, y_loc], dtype=float)
        port_dict = {
            "net": net_name,
            "r": r,
            "type": port_type
        }
        ports[self.port_idx] = port_dict
        self.pos2idx[(x_loc, y_loc)] = self.port_idx
        self.port_idx += 1
        return self.port_idx - 1

    
    def add_in_port(self, net_name: str, x_loc: float, y_loc: float):
        """Add an input port to the macro."""
        if net_name in self.in_ports:
            raise ValueError(f"Input port for net '{net_name}' already exists.")
        
        return self._add_port(self.in_ports, net_name, x_loc, y_loc, "I")


    def add_out_port(self, net_name: str, x_loc: float, y_loc: float):
        """Add an output port to the macro."""
        if net_name in self.out_ports:
            raise ValueError(f"Output port for net '{net_name}' already exists.")
        
        return self._add_port(self.out_ports, net_name, x_loc, y_loc, "O")
    

    def add_external_port(self, net_name: str, x_loc: float, y_loc: float):
        """Add an external port to the macro."""
        if net_name in self.external_ports:
            raise ValueError(f"External port for net '{net_name}' already exists.")
        
        return self._add_port(self.external_ports, net_name, x_loc, y_loc, "E")


    def get_position(self) -> np.ndarray:
        """Get the position of the macro in the layout."""
        return self.pos
    

    def get_dimensions(self) -> np.ndarray:
        """Get the dimensions of the macro."""
        return self.dim
    
    def compute_dimensions(self) -> np.ndarray:
        """Compute the dimensions of the macro considering rotation."""
        if self.rotation % 180 == 0:
            return self.dim
        else:
            return np.array([self.dim[1], self.dim[0]], dtype=float)
    

    def get_in_ports(self) -> dict[tuple[float, float], str]:
        """Get the input ports of the macro."""
        return self.in_ports
    
    def get_out_ports(self) -> dict[tuple[float, float], str]:
        """Get the output ports of the macro."""
        return self.out_ports
    

    def get_external_ports(self) -> dict[tuple[float, float], str]:
        """Get the external ports of the macro."""
        return self.external_ports
    

    def get_port(self, idx: int):
        if idx in self.in_ports:
            return self.in_ports[idx]
        elif idx in self.out_ports:
            return self.out_ports[idx]
        elif idx in self.external_ports:
            return self.external_ports[idx]
        else:
            raise ValueError(f"Port index {idx} does not exist in macro '{self.name}'.")
    
    def get_port_type(self, idx: int) -> str:
        """
        Get the type of the port (input, output, or external) based on its index.
        :param idx: Index of the port.
        :return: Type of the port as a string.
        """
        if idx in self.in_ports:
            return "I"
        elif idx in self.out_ports:
            return "O"
        elif idx in self.external_ports:
            return "E"
        else:
            raise ValueError(f"Port index {idx} does not exist in macro '{self.name}'.")

    def get_port_with_pos(self, pos: tuple[float, float]):
        if pos in self.pos2idx:
            idx = self.pos2idx[pos]
            return self.get_port(idx)
        else:
            raise ValueError(f"Position {pos} does not exist in macro '{self.name}'.")


    def compute_port_r(self, idx: int) -> np.ndarray:
        """
        Compute the position of the port in the macro's coordinate system.
        :param idx: Index of the port.
        :return: Torque r vector of the port in the macro
        """
        if idx not in self.in_ports and idx not in self.out_ports and idx not in self.external_ports:
            raise ValueError(f"Port index {idx} does not exist in macro '{self.name}'.")

        port = self.get_port(idx)
        r_vec = port["r"]

        # Apply rotation if the macro is rotated
        if self.rotation != 0:
            angle_rad = np.radians(self.rotation)
            rotation_matrix = np.array([[np.cos(angle_rad), -np.sin(angle_rad)],
                                        [np.sin(angle_rad), np.cos(angle_rad)]])
            r_vec = rotation_matrix @ r_vec
        return r_vec
    
    
    def compute_port_r_with_pos(self, pos: tuple[float, float]) -> np.ndarray:
        """
        Compute the position of the port in the macro's coordinate system.
        :param pos: Position of the port.
        :return: Torque r vector of the port in the macro
        """
        idx = self.pos2idx.get(pos)
        if idx is None:
            raise ValueError(f"Position {pos} does not exist in macro '{self.name}'.")
        
        return self.compute_port_r(idx)
    

    def compute_port_loc(self, idx: int) -> np.ndarray:
        """
        Compute the location of the port in the layout coordinate system.
        :param idx: Index of the port.
        :return: Location vector of the port in the layout
        """
        if idx not in self.in_ports and idx not in self.out_ports and idx not in self.external_ports:
            raise ValueError(f"Port index {idx} does not exist in macro '{self.name}'.")

        r_vec = self.compute_port_r(idx)
        return self.pos - self.com + r_vec
    
    def compute_port_loc_with_pos(self, pos: tuple[float, float]) -> np.ndarray:
        """
        Compute the location of the port in the layout coordinate system.
        :param pos: Position of the port.
        :return: Location vector of the port in the layout
        """
        idx = self.pos2idx.get(pos)
        if idx is None:
            raise ValueError(f"Position {pos} does not exist in macro '{self.name}'.")

        return self.compute_port_loc(idx)