# 2025-07-02

## What I did
- Added `creator.py` providing a `hardest_puzzle` function to brute-force search for the most difficult planar puzzle for given node and color counts.
- Implemented planarity checks with `nx.check_planarity` and used the existing solver to evaluate puzzle difficulty.
- Included a simple `__main__` demonstration for `n=3` and `k=3`.
- Verified `pyright` shows no errors and ran `pytest` (no tests present).

## Why I did it
- To allow automatic generation of challenging puzzles which may aid in testing and exploring the solver.

## Questions
- None.
