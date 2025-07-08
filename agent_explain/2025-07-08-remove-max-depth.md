# 2025-07-08

## What I did
- Removed the `max_depth` parameter from `SearchSolver.solve` and helper methods.
- Updated `SolvablePuzzle.solve` to match the simplified solver interface.
- Verified `pyright` passes with zero issues and no tests fail.

## Why I did it
- Limiting depth actually slowed searches rather than improving them.
- Reverting the parameter keeps the API minimal and avoids unnecessary complexity.

## Questions
- None.
