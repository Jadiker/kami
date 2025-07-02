# 2024-06-11

## What I did
- Implemented a more robust `Puzzle.collapse` that merges full connected components of the same color instead of only immediate neighbors. This ensures color propagation behaves as expected when solving puzzles.
- Verified the updated solver now finds a 3-move solution and runs without errors.
- Ensured pyright reports zero issues.

## Why I did it
- Previous collapse logic merged only direct neighbors which could disconnect regions and prevent finding optimal solutions. Using a DFS based component merge fixes the bug.

## Questions
- None.
