# 2025-07-02

## What I did
- Reimplemented `SearchSolver` to always use BFS and accept an optional `max_depth` limit.
- Updated `SolvablePuzzle.solve` to forward this parameter.
- Removed the unused DFS option from the solver constructor.

## Why I did it
- Addressed feedback on earlier implementation by simplifying the solver and ensuring depth bounds work correctly.

## Questions
- None.
