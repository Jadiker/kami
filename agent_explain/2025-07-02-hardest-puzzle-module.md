# 2025-07-02

## What I did
- Added new `creator.py` module with `hardest_puzzle` for brute-force search of planar puzzles with the maximum solution length.
- Implemented helper functions to enumerate graphs and colorings and a demonstration `__main__` section.
- Ensured pyright passes without errors and executed existing tests (none found).

## Why I did it
- Needed an example generator for challenging puzzles to showcase solver capabilities.
- Brute force works for small `n` and `k` and keeps implementation simple while meeting the requirement of planarity using `nx.check_planarity`.

## Questions
- The solver seems to find very short solutions for small puzzles. Are there known configurations requiring more moves that could be used for testing?
