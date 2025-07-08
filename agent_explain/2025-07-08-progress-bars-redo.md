# 2025-07-08

## What I did
- Removed lazy `tqdm` import in `SearchSolver` and imported at module level.
- Split `SearchSolver.solve` into helper methods to handle progress and non-progress cases.
- Avoided converting move generators to lists unless progress bars are requested.
- Added docstrings and newline at end of `requirements.txt`.

## Why I did it
- Addresses feedback to avoid lazy imports and unnecessary list conversions.
- Separate functions keep the progress logic isolated from the regular BFS path.

## Questions
- None.
