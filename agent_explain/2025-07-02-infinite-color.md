# 2025-07-02

## What I did
- Added a new module `color.py` defining `InfiniteColor`.
- Implemented `_missing_` to dynamically create enum members like `Color_6` when instantiated with out-of-range integers.
- Verified iteration still only covers the base four colors and pyright reports no issues.

## Why I did it
- Needed a color enum that gracefully handles arbitrary indices for puzzles with unlimited color slots.
- This allows requesting `InfiniteColor(n)` for any index without raising an error while maintaining compatibility with the existing `Color` ordering.

## Questions
- None.
