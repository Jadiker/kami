"""Utilities for generating challenging Kami puzzles."""
import itertools
from typing import Iterable, List, Tuple

import networkx as nx
from tqdm import tqdm

from color import InfiniteColor
from solver import SolvablePuzzle, Move, HashTracker


Coloring = Tuple[InfiniteColor, ...]


def _all_graphs(n: int) -> Iterable[nx.Graph]:
    """Yield all simple graphs with ``n`` nodes."""
    nodes = list(range(n))
    edges = list(itertools.combinations(nodes, 2))
    for mask in tqdm(range(1 << len(edges)), desc="All graphs", unit="graphs"):
        g = nx.Graph()
        g.add_nodes_from(nodes)
        for i, (u, v) in enumerate(edges):
            if mask & (1 << i):
                g.add_edge(u, v)
        yield g


def _all_colorings(n: int, colors: List[InfiniteColor]) -> Iterable[Coloring]:
    """Yield all assignments of ``colors`` to ``n`` nodes."""
    for prod in tqdm(itertools.product(colors, repeat=n), desc="All colorings", unit="colorings", total=len(colors)**n, leave=False):
        yield prod


def _puzzle_from_graph_and_colors(g: nx.Graph, coloring: Coloring, valid_colors: List[InfiniteColor]) -> SolvablePuzzle:
    puzzle = SolvablePuzzle(valid_colors=set(valid_colors))
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
    seen = set()

    for g in _all_graphs(n):
        if not nx.is_connected(g):
            continue
        is_planar, _ = nx.check_planarity(g)
        if not is_planar:
            continue
        for coloring in _all_colorings(n, colors):
            puzzle = _puzzle_from_graph_and_colors(g, coloring, colors)
            if fuzzy:
                quick_hash = puzzle.quick_hash
                if quick_hash in seen:
                    continue
                seen.add(quick_hash)
            solution = puzzle.solve()
            if solution is not None and len(solution) > max_moves:
                max_moves = len(solution)
                best_puzzle = puzzle
                best_solution = solution

    return best_puzzle, best_solution


if __name__ == "__main__":
    from timer import timing
    N = 5
    K = 5
    FUZZY = True
    assert 1 <= K <= N, f"Must have 1  <=  {K=}  <=  {N=}"
    print(f"Searching for hardest {N}-node puzzle with {K} colors...")
    print(f"{FUZZY=}")
    with timing():
        puzzle, solution = hardest_puzzle(N, K, fuzzy=FUZZY)
    print(f"Hardest {N}-node puzzle with {K} colors uses {len(solution) if solution else 'no'} moves")
    if puzzle is not None and solution is not None:
        puzzle.display_graph()
        for idx, move in enumerate(solution, 1):
            node, color = move
            print(f"{idx}. Set node {node} to {color.name}")
    else:
        print("No solvable puzzle found.")
