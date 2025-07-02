# 2025-07-02

## What I did
- Implemented `embeddable` in `core.py` which checks if a graph is planar using `networkx.check_planarity`.
- Confirmed `pyright` runs without warnings and `pytest` shows no failing tests.

## Why I did it
- The project needed a utility to determine if a given graph can be drawn in 2D without edge crossings. `networkx` has built-in planarity checking which suits this.

## Questions
- None.
