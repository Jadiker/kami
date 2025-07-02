# 2025-07-02

## What I did
- Modified `creator.py` to pass a depth limit to `SolvablePuzzle.solve` based on the current best solution length.
- If no solution is found within this bound, run an unlimited search only for puzzles that might be harder.
- This avoids exploring unnecessary deep searches for easier puzzles.

## Why I did it
- Using the `max_depth` parameter speeds up brute-force search for the hardest puzzle by pruning easy puzzles early.

## Questions
- None.
