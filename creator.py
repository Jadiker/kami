# -*- coding: utf-8 -*-
"""Utilities for generating challenging puzzles."""

from __future__ import annotations

from itertools import combinations, product
from typing import Iterable, List, Tuple

import networkx as nx

from core import Color
from solver import Move, SolvablePuzzle


def _color_choices(k: int) -> List[Color]:
    all_colors = list(Color)
    if k > len(all_colors):
        raise ValueError(f"k may not exceed {len(all_colors)}")
    return all_colors[:k]


def _build_puzzle(n: int, edges: Iterable[Tuple[int, int]], colors: Iterable[Color]) -> SolvablePuzzle:
    puzzle = SolvablePuzzle(valid_colors=set(colors))
    for node, col in enumerate(colors):
        puzzle.add_node(node, col)
    for u, v in edges:
        puzzle.add_edge(u, v)
    return puzzle


def hardest_puzzle(n: int, k: int) -> Tuple[SolvablePuzzle, List[Move]]:
    """Return the planar puzzle requiring the most moves to solve."""
    color_choices = _color_choices(k)
    nodes = list(range(n))
    all_edges = list(combinations(nodes, 2))

    best_puzzle: SolvablePuzzle | None = None
    best_solution: List[Move] | None = None

    for mask in range(1 << len(all_edges)):
        edges = [all_edges[i] for i in range(len(all_edges)) if mask & (1 << i)]
        g = nx.Graph()
        g.add_nodes_from(nodes)
        g.add_edges_from(edges)
        if not nx.check_planarity(g)[0]:
            continue
        for color_assignment in product(color_choices, repeat=n):
            puzzle = _build_puzzle(n, edges, color_assignment)
            solver_copy = puzzle.copy()
            solution = solver_copy.solve()
            if solution is None:
                continue
            if best_solution is None or len(solution) > len(best_solution):
                best_solution = solution
                best_puzzle = puzzle.copy()
    if best_puzzle is None or best_solution is None:
        raise ValueError("No puzzles generated")
    return best_puzzle, best_solution


if __name__ == "__main__":
    puzzle, sol = hardest_puzzle(3, 3)
    print("Hardest puzzle for n=3, k=3:")
    puzzle.display_graph()
    print(f"Solution length: {len(sol)}")
    for i, (node, color) in enumerate(sol, 1):
        print(f"{i}. Set node {node} to {color.name}")
