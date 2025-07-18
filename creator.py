"""Utilities for generating challenging Kami puzzles."""
import itertools
from typing import Iterable, List, Tuple

import networkx as nx
from tqdm import tqdm

from color import InfiniteColor
from solver import SolvablePuzzle, Move, HeuristicName, HashTracker


Coloring = Tuple[InfiniteColor, ...]


def _all_graphs(n: int) -> Iterable[nx.Graph]:
    """Yield all simple graphs with ``n`` nodes."""
    nodes = list(range(n))
    edges = list(itertools.combinations(nodes, 2))
    # lower smoothing (EMA) so that time estimates are more accurate throughout jitters
    for mask in tqdm(range(1 << len(edges)), desc="All graphs", unit="graph", smoothing=0.05):
        g = nx.Graph()
        g.add_nodes_from(nodes)
        for i, (u, v) in enumerate(edges):
            if mask & (1 << i):
                g.add_edge(u, v)
        yield g


def _all_colorings(n: int, colors: List[InfiniteColor]) -> Iterable[Coloring]:
    """Yield all assignments of ``colors`` to ``n`` nodes."""
    for prod in tqdm(itertools.product(colors, repeat=n), desc="All colorings", unit="coloring", total=len(colors)**n, leave=False):
        yield prod


def _create_puzzle(g: nx.Graph, coloring: Coloring, valid_colors: List[InfiniteColor], hasher: HashTracker | None) -> SolvablePuzzle:
    puzzle = SolvablePuzzle(hasher=hasher, valid_colors=set(valid_colors))
    for node, color in enumerate(coloring):
        puzzle.add_node(node, color)
    for u, v in g.edges:
        puzzle.add_edge(u, v)
    return puzzle


def hardest_puzzle(n: int, k: int, fuzzy: bool = False) -> tuple[SolvablePuzzle | None, List[Move] | None]:
    """
    Return the planar puzzle needing the most moves for ``n`` nodes and ``k`` colors.
    If ``fuzzy`` is ``True``, use quick hash to avoid duplicate puzzles.
    (This may miss some puzzles.)
    """

    colors = list(InfiniteColor)[:k]
    max_moves = -1
    best_puzzle: SolvablePuzzle | None = None
    best_solution: List[Move] | None = None
    hasher = None # each puzzle gets its own hasher
    # hasher = HashTracker()
    seen = set()

    for g in _all_graphs(n):
        if not nx.is_connected(g):
            continue
        is_planar, _ = nx.check_planarity(g)
        if not is_planar:
            continue
        for coloring in _all_colorings(n, colors):
            puzzle = _create_puzzle(g, coloring, colors, hasher)
            if fuzzy:
                quick_hash = puzzle.quick_hash
                if quick_hash in seen:
                    continue
                seen.add(quick_hash)

            # solution = puzzle.a_star_solve([heuristic for heuristic in HeuristicName])
            # solution = puzzle.a_star_solve([HeuristicName.COLOR])
            solution = puzzle.a_star_solve([HeuristicName.MAX_EDGE_REDUCTION])
            # solution = puzzle.bfs_solve(progress=False)

            if solution is not None and len(solution) > max_moves:
                max_moves = len(solution)
                best_puzzle = puzzle
                best_solution = solution

    return best_puzzle, best_solution


if __name__ == "__main__":
    from timer import timing
    n_nodes = 5
    n_colors = 4
    FUZZY = True
    assert 1 <= n_colors <= n_nodes, f"Must have 1  <=  {n_colors=}  <=  {n_nodes=}"
    print(f"Searching for hardest {n_nodes}-node puzzle with {n_colors} colors...")
    print(f"{FUZZY=}")
    with timing():
        puzzle, solution = hardest_puzzle(n_nodes, n_colors, fuzzy=FUZZY)
    print(f"Hardest {n_nodes}-node puzzle with {n_colors} colors uses {len(solution) if solution else 'no'} moves")
    if puzzle is not None and solution is not None:
        puzzle.display_graph()
        for idx, move in enumerate(solution, 1):
            node, color = move
            print(f"{idx}. Set node {node} to {color.name}")
    else:
        print("No solvable puzzle found.")
