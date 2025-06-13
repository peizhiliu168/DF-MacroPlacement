import scipy
import networkx as nx
import numpy as np

from macro import Macro
from net import Net
from orient_engine import OrientEngine

def overlappingArea(l1, r1, l2, r2):
    x = 0
    y = 1

    # Area of 1st Rectangle
    area1 = abs(l1[x] - r1[x]) * abs(l1[y] - r1[y])

    # Area of 2nd Rectangle
    area2 = abs(l2[x] - r2[x]) * abs(l2[y] - r2[y])

    x_dist = (min(r1[x], r2[x]) -
            max(l1[x], l2[x]))

    y_dist = (min(r1[y], r2[y]) -
            max(l1[y], l2[y]))
    areaI = 0
    if x_dist > 0 and y_dist > 0:
        areaI = x_dist * y_dist

    return (area1 + area2 - areaI)

class SAEngine:
    def __init__(self, macros: dict[str:Macro], nets: dict[str:Net], x_range: tuple[float, float], y_range: tuple[float, float]):
        self.macros = macros
        self.nets = nets
        self.macro2index = {name: i for i, name in enumerate(macros.keys())}
        self.index2macro = {i: name for i, name in enumerate(macros.keys())}

        self.min_x, self.max_x = x_range
        self.min_y, self.max_y = y_range

        self.orient_engine: OrientEngine = OrientEngine(macros, nets)

        self.pos_vec = [0.0] * len(macros) * 2  # x and y positions for each macro

    def _initialize_locations(self):
        # Randomly initialize the positions of macros within the specified bounds
        for i in range(0, len(self.macros), 2):
            x_pos = self.min_x + (self.max_x - self.min_x) * np.random.rand()
            y_pos = self.min_y + (self.max_y - self.min_y) * np.random.rand()
            self.pos_vec[i] = x_pos
            self.pos_vec[i + 1] = y_pos
        return
    
    def _compute_area(self) -> float:
        min_x = min(macro.pos[0] for macro in self.macros.values())
        max_x = max(macro.pos[0] + macro.compute_dimensions()[0] for macro in self.macros.values())
        min_y = min(macro.pos[1] - macro.compute_dimensions()[1] for macro in self.macros.values())
        max_y = max(macro.pos[1] for macro in self.macros.values())
        area = (max_x - min_x) * (max_y - min_y)
        return area

    def _compute_hpwl(self) -> float:
        return 0.0

    def _construct_dfg(self) -> nx.DiGraph:
        g = nx.DiGraph()

        # Add nodes for each macro
        for macro_name in self.macros.keys():
            g.add_node(macro_name)

        for net in self.nets.values():            
            in_macros = net.get_in_macro()
            out_macros = net.get_out_macro()

            for out_macro, out_idx in out_macros:
                for in_macro, in_idx in in_macros:
                    if out_macro.name == in_macro.name:
                        continue
                    
                    # Compute the energy based on distance
                    out_pos = out_macro.compute_port_loc(out_idx)
                    in_pos = in_macro.compute_port_loc(in_idx)
                    distance = np.linalg.norm(in_pos - out_pos)
                    energy = distance ** 2

                    # Add directed edge with energy as weight
                    g.add_edge(out_macro.name, in_macro.name, energy=energy)


        return g


    def _compute_overlap(self) -> float:
        """Compute the total overlap area between macros."""
        overlap = 0.0
        macros = list(self.macros.values())
        for i in range(len(macros)):
            for j in range(i + 1, len(macros)):
                m1 = macros[i]
                m2 = macros[j]

                m1_pos = m1.get_position()
                m1_dim = m1.compute_dimensions()
                m2_pos = m2.get_position()
                m2_dim = m2.compute_dimensions()

                l1 = [m1_pos[0], m1_pos[1] - m1_dim[1]]
                r1 = [m1_pos[0] + m1_dim[0], m1_pos[1]]
                l2 = [m2_pos[0], m2_pos[1] - m2_dim[1]]
                r2 = [m2_pos[0] + m2_dim[0], m2_pos[1]]

                overlap += overlappingArea(l1, r1, l2, r2)

        return overlap

    def _compute_overflow(self) -> float:
        """Compute the overflow area, which is the area of the bounding box minus the area of the layout."""
        overflow = 0.0
        l1 = [self.min_x, self.min_y]
        r1 = [self.max_x, self.max_y]

        for macro in self.macros.values():
            m_pos = macro.get_position()
            m_dim = macro.compute_dimensions()
            l2 = [m_pos[0], m_pos[1] - m_dim[1]]
            r2 = [m_pos[0] + m_dim[0], m_pos[1]]
            
            overlap = overlappingArea(l1, r1, l2, r2)
            overflow += (r1[0] - l1[0]) * (r1[1] - l1[1]) - overlap
            
        return overflow

    def run(self):
        print("Running simulated annealing.")
        
        # Initialize positions of macros
        self._initialize_locations()
        
        def obj_f(x):
            # Place the macros at the specified positions
            for idx, m_name in self.index2macro.items():
                macro: Macro = self.macros[m_name]
                x_pos = x[idx * 2]
                y_pos = x[idx * 2 + 1]
                macro.set_position(x_pos, y_pos)

            # Use the rotation engine to rotate the macros based on torque
            self.orient_engine.run()
            self.orient_engine.update_macro_rotation()

            # Compute area
            AREA = self._compute_area()

            # Compute HPWL 
            HPWL = self._compute_hpwl()

            # Construct the weighted dataflow graph with Energy E α d^2
            dfg: nx.DiGraph = self._construct_dfg()
            # Compute longest path 
            path = nx.dag_longest_path(dfg, weight='energy')
            ENERGY = sum(dfg[u][v]['energy'] for u, v in zip(path[:-1], path[1:]))

            # Compute overlap area
            OVERLAP = self._compute_overlap()

            # Compute overflow area
            OVERFLOW = self._compute_overflow()

            # Compute total weighted cost
            total_cost = AREA + HPWL + ENERGY + 100 * OVERLAP + 100 * OVERFLOW
            print(f"Current cost: {total_cost}, AREA: {AREA}, HPWL: {HPWL}, ENERGY: {ENERGY}, OVERLAP: {OVERLAP}, OVERFLOW: {OVERFLOW}")

            return total_cost

        res: scipy.optimize.OptimizeResult = scipy.optimize.dual_annealing(
            obj_f, 
            bounds=[(self.min_x, self.max_x), (self.min_y, self.max_y)] * len(self.macros)
        )

        self.pos_vec = res.x
        print("Optimization result:", res)

        return self.pos_vec
    

    def update_macro_positions(self):
        """Update the positions of macros based on the current position vector."""
        for idx, m_name in self.index2macro.items():
            macro: Macro = self.macros[m_name]
            x_pos = self.pos_vec[idx * 2]
            y_pos = self.pos_vec[idx * 2 + 1]
            macro.set_position(x_pos, y_pos)
        return