from macro import Macro

class Net:
    def __init__(self, name: str):
        """
        Initialize a Net object.
        :param name: Name of the net.
        """
        self.name = name
        self.degree = 0
        self.in_nodes: list[tuple[Macro, int]] = []
        self.out_nodes: list[tuple[Macro, int]] = []
        self.external_nodes: list[tuple[Macro, int]] = []

    def add_in_macro(self, macro: Macro, idx: int):
        """Add an input port to the net."""
        self.in_nodes.append((macro, idx))
        self.degree += 1
    
    def add_out_macro(self, macro: Macro, idx: int):
        """Add an output port to the net."""
        self.out_nodes.append((macro, idx))
        self.degree += 1

    def add_external_macro(self, macro: Macro, idx: int):
        """Add an external port to the net."""
        self.external_nodes.append((macro, idx))
        self.degree += 1
    
    def get_in_macro(self) -> list[Macro]:
        """Get the input ports of the net."""
        return self.in_nodes
    
    def get_out_macro(self) -> list[Macro]:
        """Get the output ports of the net."""
        return self.out_nodes
    
    def get_external_macro(self) -> list[Macro]:
        """Get the external ports of the net."""
        return self.external_nodes

    def get_degree(self) -> int:
        """Get the degree of the net."""
        return self.degree