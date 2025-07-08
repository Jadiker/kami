# 2025-07-03

## What I did
- Added a `progress` parameter to `SearchSolver.solve` for optional tqdm bars.
- Updated `SolvablePuzzle.solve` to forward the flag.
- Included lazy tqdm import and layer-wise progress display for BFS.
- Updated requirements installation and ran pyright/tests.

## Why I did it
- Allows visual progress monitoring during searches when desired.

## Questions
- DFS progress wasn't implemented because the solver currently only supports BFS. Should DFS support be restored in the future?
