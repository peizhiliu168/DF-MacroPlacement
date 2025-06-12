

class Macro:
    def __init__(self, name: str, width: float, height: float, rotation: str = "0", fixed: bool = False):
        """
        Initialize a Macro object.
        :param name: Name of the macro.
        :param width: Width of the macro.
        :param height: Height of the macro.
        :param rotation: Rotation of the macro (default is "0").
        :param fixed: Whether the macro is fixed (default is False).
        """
        self.name = name
        self.width = width
        self.height = height
        self.rotation = rotation
        self.fixed = fixed

        # Position of the macro in the layout - top-left corner
        self.x = 0.0
        self.y = 0.0

        # Input and output ports
        self.in_ports: dict[tuple[float, float], str] = {} 
        self.out_ports: dict[tuple[float, float], str] = {}
        self.external_ports: dict[tuple[float, float], str] = {} 

    def set_position(self, x: float, y: float):
        """Set the position of the macro in the layout."""
        self.x = x
        self.y = y

    def set_rotation(self, rotation: str):
        """Set the rotation of the macro."""
        if rotation not in ["0", "90", "180", "270"]:
            raise ValueError(f"Invalid rotation value: {rotation}. Expected '0', '90', '180', or '270'.")
        self.rotation = rotation
    
    def add_in_port(self, net_name: str, x_loc: float, y_loc: float):
        """Add an input port to the macro."""
        if net_name in self.in_ports:
            raise ValueError(f"Input port for net '{net_name}' already exists.")
        self.in_ports[(x_loc, y_loc)] = net_name

    def add_out_port(self, net_name: str, x_loc: float, y_loc: float):
        """Add an output port to the macro."""
        if net_name in self.out_ports:
            raise ValueError(f"Output port for net '{net_name}' already exists.")
        self.out_ports[(x_loc, y_loc)] = net_name
    
    def add_external_port(self, net_name: str, x_loc: float, y_loc: float):
        """Add an external port to the macro."""
        if net_name in self.external_ports:
            raise ValueError(f"External port for net '{net_name}' already exists.")
        self.external_ports[(x_loc, y_loc)] = net_name

    def get_position(self) -> tuple:
        """Get the position of the macro in the layout."""
        return self.x, self.y
    
    def get_dimensions(self) -> tuple:
        """Get the dimensions of the macro."""
        
        if self.rotation in ["0", "180"]:
            return self.width, self.height

        if self.rotation in ["90", "270"]:
            return self.height, self.width

        raise ValueError(f"Invalid rotation value: {self.rotation}. Expected '0', '90', '180', or '270'.")
    
    def get_in_ports(self) -> dict[str, tuple[float, float]]:
        """Get the input ports of the macro."""
        return self.in_ports
    
    def get_out_ports(self) -> dict[str, tuple[float, float]]:
        """Get the output ports of the macro."""
        return self.out_ports
    
    def get_external_ports(self) -> dict[str, tuple[float, float]]:
        """Get the external ports of the macro."""
        return self.external_ports
    

