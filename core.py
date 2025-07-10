
import warnings
from enum import Enum, auto, StrEnum
from typing import cast

import networkx as nx
from color import InfiniteColor

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

def embeddable(graph: nx.Graph) -> bool:
    """Return ``True`` if ``graph`` is planar.

    A graph is planar when it can be embedded in the plane without any
    edge crossings. The check is performed using :func:`networkx.check_planarity`.
    """

    return nx.check_planarity(graph)[0]

class WarningActionKind(StrEnum):
    IGNORE = "ignore"

class NodeAttributeName(StrEnum):
    COLOR = 'color'

class HashTracker:
    def __init__(self):
        self.hashes: dict[QuickHash, list[IsomorphicPuzzleGraph]] = {}

    @classmethod
    def _merge(cls, hash, index) -> FullHash:
        '''Take a quick hash and the index of the puzzle in the list corresponding to that hash and return the full hash.'''
        return f'{hash}_{index}'

    def full_hash(self, puzzle: "Puzzle") -> FullHash:
        '''
        Add the puzzle to the tracker and return its full hash.
        '''
        quick_hash, iso_graph = puzzle.quick_hash, puzzle.iso_graph
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
        
    @staticmethod
    def quick_hash(puzzle: "Puzzle") -> tuple[QuickHash, IsomorphicPuzzleGraph]:
        """Return a quick (not collision-free) hash and its associated isomorphic graph for the given puzzle."""
        puzzle = puzzle.copy()
        puzzle.collapse()
        iso_graph = puzzle.to_colored_digraph()
        with warnings.catch_warnings():
            warnings.simplefilter(cast("warnings._ActionKind", WarningActionKind.IGNORE), category=UserWarning)
            quick_hash: QuickHash = nx.weisfeiler_lehman_graph_hash(iso_graph)
        return quick_hash, iso_graph


class Puzzle:
    @staticmethod
    def set_recalc_full_hash(method):
        def wrapper(self, *args, **kwargs):
            self.recalc_full_hash = True
            return method(self, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def redo_all(method):
        def wrapper(self, *args, **kwargs):
            self.recalc_full_hash = True
            self.recalc_quick_hash = True
            self.not_collapsed = True
            return method(self, *args, **kwargs)
        return wrapper
    
    def __init__(self, hasher: HashTracker | None = None):
        self.graph = nx.Graph()
        self.hasher = hasher if hasher is not None else HashTracker()
        # whether the puzzle has been modified since last hash computation
        self.recalc_full_hash = True
        self.recalc_quick_hash = True
        self.not_collapsed = True
        self._full_hash: FullHash | None = None
        self._quick_hash: QuickHash | None = None
        self._iso_graph: IsomorphicPuzzleGraph | None = None

    @property
    def full_hash(self) -> FullHash:
        if self.recalc_full_hash:
            self._full_hash = self.hasher.full_hash(self)
            self.recalc_full_hash = False

        assert self._full_hash is not None
        return self._full_hash
    
    @property
    def quick_hash(self) -> QuickHash:
        if self.recalc_quick_hash:
            self._quick_hash, self._iso_graph = self.hasher.quick_hash(self)
            self.recalc_quick_hash = False
        assert self._quick_hash is not None
        return self._quick_hash
    
    @property
    def iso_graph(self) -> IsomorphicPuzzleGraph:
        if self.recalc_full_hash:
            self._quick_hash, self._iso_graph = self.hasher.quick_hash(self)
            self.recalc_quick_hash = False
        assert self._iso_graph is not None
        return self._iso_graph
    
    # doesn't modify the structure, but may modify the final hash
    @set_recalc_full_hash
    def set_hasher(self, hasher: HashTracker):
        self.hasher = hasher
    
    @redo_all
    def add_node(self, node_id: NodeID, color: InfiniteColor):
        self.graph.add_node(node_id, **{NodeAttributeName.COLOR: color})
    
    @redo_all
    def add_edge(self, node1: NodeID, node2: NodeID):
        self.graph.add_edge(node1, node2)

    @redo_all
    def set_color(self, node_id: NodeID, color: InfiniteColor, propagate: bool = True):
        if propagate:
            same_color_neighbors = self.get_same_color_neighbors(node_id)
            for neighbor in same_color_neighbors:
                self.set_color(neighbor, color, propagate=False)
        self.graph.nodes[node_id][NodeAttributeName.COLOR] = color
    
    def get_color(self, node_id: NodeID) -> InfiniteColor:
        return self.graph.nodes[node_id][NodeAttributeName.COLOR]
    
    def get_neighbors(self, node_id: NodeID):
        return list(self.graph.neighbors(node_id))
    
    def get_same_color_neighbors(self, node_id: NodeID):
        color = self.get_color(node_id)
        return [n for n in self.get_neighbors(node_id) if self.get_color(n) == color]

    @property
    def is_solved(self) -> bool:
        colors = {self.get_color(node) for node in self.graph.nodes}
        return len(colors) == 1
    
    # Doesn't modify the full hash because the graph structure doesn't change
    def collapse(self, node_id: NodeID | None = None) -> None:
        """Merge connected components of identical color into single nodes.

        When ``node_id`` is provided only the component containing that node is
        collapsed. Otherwise all components in the puzzle are collapsed.
        """
        if not self.not_collapsed:
            # No need to collapse again if nothing has changed
            return
        
        def _component(start: NodeID) -> set[NodeID]:
            '''Return the set of nodes in the connected component of the same color as start.'''
            color = self.get_color(start)
            stack = [start]
            # short for "component"
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
            '''Collapse the component ``comp`` into a single node with ID ``start``.'''
            color = self.get_color(start)
            new_neighbors = {
                neighbor
                for node in comp
                for neighbor in self.get_neighbors(node)
                if neighbor not in comp
            }
            for node in comp:
                self.graph.remove_node(node)
            self.graph.add_node(start, **{NodeAttributeName.COLOR: color})
            for neighbor in new_neighbors:
                self.graph.add_edge(start, neighbor)

        if node_id is not None:
            comp = _component(node_id)
            _collapse(node_id, comp)
            # could still be uncollapsed at this point
        else:
            visited: set[NodeID] = set()
            for node in list(self.graph.nodes):
                if node in visited or node not in self.graph.nodes:
                    continue
                comp = _component(node)
                visited.update(comp)
                _collapse(node, comp)
            # all components collapsed
            self.not_collapsed = False


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
        new_puzzle = Puzzle(self.hasher)
        # don't need deep copy since there are no nested structures
        new_puzzle.graph = self.graph.copy()
        new_puzzle.recalc_full_hash = self.recalc_full_hash
        new_puzzle.recalc_quick_hash = self.recalc_quick_hash
        new_puzzle.not_collapsed = self.not_collapsed
        new_puzzle._full_hash = self._full_hash
        new_puzzle._quick_hash = self._quick_hash
        new_puzzle._iso_graph = self._iso_graph
        return new_puzzle

    def display_graph(self):
        for node in self.graph.nodes:
            color = self.get_color(node)
            neighbors = self.get_neighbors(node)
            print(f'Node {node}: Color {color.name}, Neighbors {neighbors}')

    def __str__(self) -> str:
        return f'Puzzle(FullHash={self.full_hash}, QuickHash={self.quick_hash}, Nodes={self.graph.nodes(data=True)}, Edges={self.graph.edges})'
    


def demo():
    hasher = HashTracker()
    puzzle1 = Puzzle(hasher)
    puzzle1.add_node(1, InfiniteColor.ORANGE)
    puzzle1.add_node(2, InfiniteColor.ORANGE)
    puzzle1.add_node(3, InfiniteColor.DARK_BLUE)
    puzzle1.add_node(4, InfiniteColor.CREAM)
    puzzle1.add_node(5, InfiniteColor.CREAM)
    puzzle1.add_edge(1, 2)
    puzzle1.add_edge(2, 3)
    puzzle1.add_edge(3, 4)
    puzzle1.add_edge(4, 5)
    puzzle1.add_edge(5, 1)
    puzzle1.display_graph()

    puzzle2 = Puzzle(hasher)
    puzzle2.add_node(10, InfiniteColor.CREAM)
    puzzle2.add_node(20, InfiniteColor.CREAM)
    puzzle2.add_node(30, InfiniteColor.TURQUOISE)
    puzzle2.add_node(80, InfiniteColor.ORANGE)
    puzzle2.add_node(70, InfiniteColor.ORANGE)
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