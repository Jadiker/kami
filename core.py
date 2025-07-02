
import warnings
from enum import Enum, auto, StrEnum
from typing import TYPE_CHECKING, cast

import networkx as nx

# graph representation of a puzzle that is unique up to isomorphism
IsomorphicPuzzleGraph = nx.DiGraph
NodeID = int
# a short hash that may have collisions
# if graphs are isomorphic, they have the same hash
# ...but the converse is not true
# (the same hash may correspond to multiple non-isomorphic graphs)
QuickHash = str
# a longer hash that is unique with respect to isomorphism
FullHash = str

class WarningActionKind(StrEnum):
    IGNORE = "ignore"

class Color(Enum):
    ORANGE = auto()
    DARK_BLUE = auto()
    CREAM = auto()
    TURQUOISE = auto()

class NodeAttributeName(StrEnum):
    COLOR = 'color'

class HashTracker:
    def __init__(self):
        self.hashes: dict[QuickHash, list[IsomorphicPuzzleGraph]] = {}

    @classmethod
    def _merge(cls, hash, index) -> FullHash:
        '''Take a quick hash and the index of the puzzle in the list corresponding to that hash and return the full hash.'''
        return f'{hash}_{index}'

    def go(self, puzzle: "Puzzle") -> FullHash:
        '''
        Add the puzzle to the tracker and return its full hash.
        '''
        puzzle = puzzle.copy()
        puzzle.collapse()
        iso_graph = puzzle.to_colored_digraph()
        with warnings.catch_warnings():
            warnings.simplefilter(cast("warnings._ActionKind", WarningActionKind.IGNORE), category=UserWarning)
            quick_hash: QuickHash = nx.weisfeiler_lehman_graph_hash(iso_graph)
        if quick_hash not in self.hashes:
            self.hashes[quick_hash] = [iso_graph]
            return self._merge(quick_hash, 0)
        else:
            for index, existing_graph in enumerate(self.hashes[quick_hash]):
                if nx.is_isomorphic(iso_graph, existing_graph):
                    return self._merge(quick_hash, index)
            # not isomorphic to any existing graph with this quick hash
            self.hashes[quick_hash].append(iso_graph)
            return self._merge(quick_hash, len(self.hashes[quick_hash]) - 1)


class Puzzle:
    @staticmethod
    def modifies(method):
        def wrapper(self, *args, **kwargs):
            self.modified = True
            return method(self, *args, **kwargs)
        return wrapper
    
    def __init__(self, hasher: HashTracker | None = None):
        self.graph = nx.Graph()
        self.hasher = hasher if hasher is not None else HashTracker()
        # whether the puzzle has been modified since last hash computation
        self.modified = True

    @property
    def full_hash(self) -> FullHash:
        if self.modified:
            self._full_hash = self.hasher.go(self)
            self.modified = False
        return self._full_hash
    
    # doesn't modify the structure, but may modify the final hash
    @modifies
    def set_hasher(self, hasher: HashTracker):
        self.hasher = hasher
    
    @modifies
    def add_node(self, node_id: NodeID, color: Color):
        self.graph.add_node(node_id, **{NodeAttributeName.COLOR: color})
    
    @modifies
    def add_edge(self, node1: NodeID, node2: NodeID):
        self.graph.add_edge(node1, node2)
    
    def get_color(self, node_id: NodeID) -> Color:
        return self.graph.nodes[node_id][NodeAttributeName.COLOR]
    
    def get_neighbors(self, node_id: NodeID):
        return list(self.graph.neighbors(node_id))
    
    def get_same_color_neighbors(self, node_id: NodeID):
        color = self.get_color(node_id)
        return [n for n in self.get_neighbors(node_id) if self.get_color(n) == color]

    @modifies
    def set_color(self, node_id: NodeID, color: Color, propagate: bool = True):
        if propagate:
            same_color_neighbors = self.get_same_color_neighbors(node_id)
            for neighbor in same_color_neighbors:
                self.set_color(neighbor, color, propagate=False)
        self.graph.nodes[node_id][NodeAttributeName.COLOR] = color

    @property
    def is_solved(self) -> bool:
        colors = {self.get_color(node) for node in self.graph.nodes}
        return len(colors) == 1
    
    # Doesn't modify the full hash because the graph structure doesn't change
    def collapse(self, node_id: NodeID | None = None) -> None:
        """Merge connected components of identical color into single nodes.

        When ``node_id`` is provided only the component containing that node is
        collapsed.  Otherwise all components in the puzzle are collapsed.
        """

        def _component(start: NodeID) -> set[NodeID]:
            color = self.get_color(start)
            stack = [start]
            comp = set()
            while stack:
                current = stack.pop()
                if current in comp:
                    continue
                if self.get_color(current) != color:
                    continue
                comp.add(current)
                stack.extend(self.get_neighbors(current))
            return comp

        def _collapse(start: NodeID, comp: set[NodeID]) -> None:
            color = self.get_color(start)
            new_neighbors = {
                neigh
                for node in comp
                for neigh in self.get_neighbors(node)
                if neigh not in comp
            }
            for node in comp:
                self.graph.remove_node(node)
            self.graph.add_node(start, **{NodeAttributeName.COLOR: color})
            for neigh in new_neighbors:
                self.graph.add_edge(start, neigh)

        if node_id is not None:
            comp = _component(node_id)
            _collapse(node_id, comp)
        else:
            visited: set[NodeID] = set()
            for node in list(self.graph.nodes):
                if node in visited or node not in self.graph.nodes:
                    continue
                comp = _component(node)
                visited.update(comp)
                _collapse(node, comp)

    def to_colored_digraph(self: "Puzzle") -> IsomorphicPuzzleGraph:
        """
        Return a new DiGraph with two kinds of nodes:
        kind = "v"  : original puzzle vertex
        kind = "c"  : one node per *color class*

        Edges:
        c  →  v       if v has that color
        v  ↔  w       (two directions) for every original undirected edge {v,w}

        This representation makes it so that graphs with the same structure with regards to connections and coloring are isomorphic.
        """
        G = nx.DiGraph()

        # 1. add vertex nodes
        for v in self.graph.nodes:
            G.add_node(("v", v), kind="v")          # tuple keeps IDs distinct

        # 2. add one color node per color value
        color_to_node = {}
        for v in self.graph.nodes:
            col = self.get_color(v)
            if col not in color_to_node:
                color_to_node[col] = ("c", col)    # keep Enum for uniqueness
                G.add_node(("c", col), kind="c")

            G.add_edge(("c", col), ("v", v))        # color  →  vertex

        # 3. add bidirectional edges for the puzzle links
        for u, w in self.graph.edges:
            G.add_edge(("v", u), ("v", w))
            G.add_edge(("v", w), ("v", u))

        return G

    def copy(self) -> "Puzzle":
        new_puzzle = Puzzle()
        # don't need deep copy since there are no nested structures
        new_puzzle.graph = self.graph.copy()
        return new_puzzle

    def display_graph(self):
        for node in self.graph.nodes:
            color = self.get_color(node)
            neighbors = self.get_neighbors(node)
            print(f'Node {node}: Color {color.name}, Neighbors {neighbors}')
    


def demo():
    hasher = HashTracker()
    puzzle1 = Puzzle(hasher)
    puzzle1.add_node(1, Color.ORANGE)
    puzzle1.add_node(2, Color.ORANGE)
    puzzle1.add_node(3, Color.DARK_BLUE)
    puzzle1.add_node(4, Color.CREAM)
    puzzle1.add_node(5, Color.CREAM)
    puzzle1.add_edge(1, 2)
    puzzle1.add_edge(2, 3)
    puzzle1.add_edge(3, 4)
    puzzle1.add_edge(4, 5)
    puzzle1.add_edge(5, 1)
    puzzle1.display_graph()

    puzzle2 = Puzzle(hasher)
    puzzle2.add_node(10, Color.CREAM)
    puzzle2.add_node(20, Color.CREAM)
    puzzle2.add_node(30, Color.TURQUOISE)
    puzzle2.add_node(80, Color.ORANGE)
    puzzle2.add_node(70, Color.ORANGE)
    puzzle2.add_edge(10, 20)
    puzzle2.add_edge(20, 30)
    puzzle2.add_edge(30, 80)
    puzzle2.add_edge(80, 70)
    puzzle2.add_edge(70, 10)
    puzzle2.display_graph()

    print(f'Puzzle 1 full hash: {puzzle1.full_hash}')
    print(f'Puzzle 2 full hash: {puzzle2.full_hash}')
    print(f'Are puzzles isomorphic? {puzzle1.full_hash == puzzle2.full_hash}')

if __name__ == '__main__':
    demo()