import math
from enum import StrEnum
from typing import cast, Callable

import networkx as nx

from core import HashTracker, NodeID, Puzzle
from color import InfiniteColor
from search_algs import BFSSolver, AStarSolver, GenericCost

# a move sets a node to a color (and propagates to its same-color neighbors)
Move = tuple[NodeID, InfiniteColor]

class SolverType(StrEnum):
    BFS = "breadth first search"
    A_STAR = "A* search"

class HeuristicName(StrEnum):
    COLOR = "color"
    MAX_EDGE_REDUCTION = "max edge reduction"

def color_heuristic(puzzle: Puzzle) -> int:
    '''
    One move can never create a new color and it can eliminate at most one existing color.
    The puzzle is solved when there is only one color left.
    '''
    return len({puzzle.get_color(node_id) for node_id in puzzle.graph.nodes}) - 1

def max_edge_reduction_heuristic(puzzle: Puzzle) -> int:
    '''
    Calculates the maximum number of moves required to solve the puzzle, assuming that you continue to make moves that reduce the current number of edges by k, where k is the current maximum number of edges that can be reduced by a single move.
    '''

    """
    Consistency proof for the heuristic

            h(n) = ceil(E(n) / K(n))

    where
        E(n)  = number of (undirected) edges remaining in state n
        K(n)  = max { edges a *single* legal move can delete in state n }
                (here: the maximum degree after collapsing same-colour components)

    Assumptions
    -----------
    1.  Unit-cost moves:  c(n, n') = 1  for every legal transition n → n'.
    2.  Edge deletion only: a move can never add edges, so
            E(n') ≥ E(n) - K(n).                              (A)
    3.  Monotone-K: deleting edges cannot *increase* any node's degree, hence
            K(n') ≤ K(n).                                     (B)

    Goal
    ----
    Show    h(n) ≤ 1 + h(n')    for every edge n → n'
            ⇒ the heuristic is *consistent*.

    Proof
    -----
    Start from (A) and (B):

        E(n') ≥ E(n) - K(n)               # from (A)
        divide by K(n) (positive):
            E(n') / K(n) ≥ E(n)/K(n) - 1
        but K(n') ≤ K(n) ⇒ E(n')/K(n') ≥ E(n')/K(n)

    So                                   # combine the two inequalities
            E(n) / K(n) ≤ 1 + E(n') / K(n')                (C)

    Apply ceil(), which is monotone and satisfies ceil(x) ≤ 1 + ceil(x-1):

            ceil(E(n)/K(n)) ≤ 1 + ceil(E(n')/K(n'))

    That is

            h(n) ≤ 1 + h(n')            ⇒   consistency □
    """
    def edge_reduction_bound(puzzle: Puzzle) -> int:
        """
        Upper bound on how many edges a *single* move can delete in this state.

        This is computed as the maximum degree of any node (after collapse).
        """
        puzzle = puzzle.copy()
        puzzle.collapse()
        # Compute the maximum degree across all nodes in the graph.
        return max([
            cast(
                int,
                cast(
                    nx.classes.reportviews.DegreeView,
                    puzzle.graph.degree
                )[v]
            )
            for v in puzzle.graph.nodes
        ])
    
    k: int = edge_reduction_bound(puzzle)
    if k == 0:
        # No edges left - puzzle is solved
        return 0
    
    assert k > 0, f"Invalid edge reduction bound: {k=}"
    return math.ceil(puzzle.graph.number_of_edges() / k)

HEURISTICS: dict[HeuristicName, Callable[[Puzzle], float]] = {
    HeuristicName.COLOR: color_heuristic,
    HeuristicName.MAX_EDGE_REDUCTION: max_edge_reduction_heuristic,
}

class SolvablePuzzle(Puzzle):
    def __init__(self, hasher: HashTracker | None = None, valid_colors: set[InfiniteColor] | int = 2):
        super().__init__(hasher=hasher)
        if isinstance(valid_colors, int):
            valid_colors = {InfiniteColor(i) for i in range(valid_colors)}
        self.valid_colors = valid_colors

    def copy(self) -> 'SolvablePuzzle':
        new_puzzle = SolvablePuzzle(hasher=self.hasher, valid_colors=self.valid_colors)
        new_puzzle.graph = self.graph.copy()
        new_puzzle.recalc_full_hash = self.recalc_full_hash
        new_puzzle.recalc_quick_hash = self.recalc_quick_hash
        new_puzzle.not_collapsed = self.not_collapsed
        new_puzzle._full_hash = self._full_hash
        new_puzzle._quick_hash = self._quick_hash
        new_puzzle._iso_graph = self._iso_graph
        return new_puzzle

    def get_valid_moves(self) -> list[Move]:
        return [
            (node, color)
            for node in self.graph.nodes
            for color in self.valid_colors
            if color != self.get_color(node)
        ]

    @classmethod
    def search_namer(cls, puzzle: 'SolvablePuzzle') -> str:
        return puzzle.full_hash
    
    @classmethod
    def search_detector(cls, puzzle: 'SolvablePuzzle') -> bool:
        return puzzle.is_solved
    
    @classmethod
    def search_expander(cls, puzzle: 'SolvablePuzzle') -> list[Move]:
        return puzzle.get_valid_moves()
    
    @classmethod
    def search_heuristic(cls, puzzle: 'SolvablePuzzle') -> float:
        return float(color_heuristic(puzzle))
    
    @classmethod
    def search_cost(cls, puzzle1: 'SolvablePuzzle', move: Move, puzzle2: 'SolvablePuzzle') -> int:
        # The cost of a move is always 1; a better solution is one with less moves.
        return 1
    
    @classmethod
    def search_follower(cls, puzzle: 'SolvablePuzzle', move: Move) -> 'SolvablePuzzle':
        node, color = move
        new_puzzle = puzzle.copy()
        new_puzzle.set_color(node, color, propagate=True)
        new_puzzle.collapse()
        return new_puzzle

    def bfs_solve(self, progress: bool = False) -> list[Move] | None:
        collapsed_self = self.copy()
        collapsed_self.collapse()
        solver = BFSSolver(
            namer=self.search_namer,
            detector=self.search_detector,
            expander=self.search_expander,
            follower=self.search_follower,
        )
        return solver.solve(collapsed_self, progress=progress)
    
    def a_star_solve(self, heuristics: list[HeuristicName]) -> list[Move] | None:
        collapsed_self = self.copy()
        collapsed_self.collapse()
        # using the maximum of consistent heuristics is also consistent
        heuristic: Callable[[Puzzle], float] = lambda puzzle: max([HEURISTICS[h](puzzle) for h in heuristics])
        solver = AStarSolver(
            namer=self.search_namer,
            detector=self.search_detector,
            expander=self.search_expander,
            follower=self.search_follower,
            heuristic=heuristic,
            cost=self.search_cost,
            init_cost=0
        )
        return solver.solve(collapsed_self)
    
if __name__ == '__main__':
    import puzzles
    from timer import timing

    # puzzle = puzzles.puzzles[puzzles.PuzzleName.puzzle_3_3]
    # puzzle_section_to_name = lambda section: puzzles.Pz_3_3_Section(section).name

    puzzle = puzzles.puzzles[puzzles.PuzzleName.puzzle_4_6]
    puzzle_section_to_name = lambda section: puzzles.Pz_4_6_Section(section).name

    a_star_heuristics = [HeuristicName.COLOR, HeuristicName.MAX_EDGE_REDUCTION]
    bfs_progress_bar = True


    for solver_type in (SolverType.A_STAR, SolverType.BFS):
        times = []

        print(f"Solving puzzle using {solver_type}...")
        with timing(times):
            if solver_type == SolverType.A_STAR:
                print(f"Using {a_star_heuristics=}")
                solution = puzzle.a_star_solve(a_star_heuristics)
            elif solver_type == SolverType.BFS:
                solution = puzzle.bfs_solve(progress=bfs_progress_bar)
            else:
                raise ValueError(f"Unknown solver type: {solver_type}")

        solve_time = times.pop()
        print(f"Solution found in {solve_time} seconds:")
        if solution is None:
            print("No solution found.")
        else:
            for index, move in enumerate(solution):
                section_number, color = move
                print(f"{index + 1}. Set {puzzle_section_to_name(section_number)} to {color.name}")
            print(f"Total moves: {len(solution)}")