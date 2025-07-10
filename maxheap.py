from __future__ import annotations

from typing import (
    Protocol,
    TypeVar,
    Generic,
    Iterable,
    List,
    Dict,
    Optional,
    runtime_checkable,
)

# ────────────────────────────────────────────────────────────
#  Interface required of heap elements
# ────────────────────────────────────────────────────────────

@runtime_checkable
class HeapItem(Protocol):
    """
    Minimal contract for objects stored in MaxHeap.
    • .name  must be a unique, hashable identifier.
    • .score must be a numeric value (higher = better).
    """
    name: str
    score: float


T = TypeVar("T", bound=HeapItem)

# ────────────────────────────────────────────────────────────
#  The heap itself
# ────────────────────────────────────────────────────────────


class MaxHeap(Generic[T]):
    """Array-backed max-heap keyed by .score and addressed by .name."""

    __slots__ = ("_heap", "_pos")

    # ───── construction ─────
    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        self._heap: List[T] = []
        self._pos: Dict[str, int] = {}  # maps .name → index in _heap

        if items:
            # Load in O(n) and heapify bottom-up
            for obj in items:
                self._pos[obj.name] = len(self._heap)
                self._heap.append(obj)

            for i in reversed(range(len(self._heap) // 2)):
                self._sift_down(i)

    # ───── public API ─────
    def add_or_update(self, obj: T) -> None:
        """
        Insert *obj* or, if another element with the same .name is present,
        replace and restore order in O(log n).
        """
        idx: Optional[int] = self._pos.get(obj.name)
        if idx is None:  # true insert
            self._pos[obj.name] = len(self._heap)
            self._heap.append(obj)
            self._sift_up(len(self._heap) - 1)
        else:  # update in place
            old = self._heap[idx]
            self._heap[idx] = obj
            if obj.score > old.score:
                self._sift_up(idx)
            elif obj.score < old.score:
                self._sift_down(idx)

    def pop(self) -> T:
        """Remove and return the element with the highest score (O(log n))."""
        if not self._heap:
            raise IndexError("pop from empty heap")

        top: T = self._heap[0]
        last: T = self._heap.pop()
        del self._pos[top.name]

        if self._heap:
            self._heap[0] = last
            self._pos[last.name] = 0
            self._sift_down(0)

        return top

    def peek(self) -> Optional[T]:
        """Read-only access to the current max element (or None if empty)."""
        return self._heap[0] if self._heap else None

    # Pythonic helpers
    def __len__(self) -> int:  # len(heap)
        return len(self._heap)

    def __bool__(self) -> bool:  # bool(heap)
        return bool(self._heap)

    def __iter__(self):  # iterate raw heap order
        return iter(self._heap)

    # ───── internal machinery ─────
    def _sift_up(self, idx: int) -> None:
        heap, pos = self._heap, self._pos
        item: T = heap[idx]

        while idx:
            parent = (idx - 1) >> 1
            if item.score <= heap[parent].score:
                break
            heap[idx] = heap[parent]
            pos[heap[parent].name] = idx
            idx = parent

        heap[idx] = item
        pos[item.name] = idx

    def _sift_down(self, idx: int) -> None:
        heap, pos = self._heap, self._pos
        size = len(heap)
        item: T = heap[idx]

        while True:
            left = (idx << 1) + 1
            if left >= size:
                break

            right = left + 1
            larger = right if right < size and heap[right].score > heap[left].score else left

            if heap[larger].score <= item.score:
                break

            heap[idx] = heap[larger]
            pos[heap[larger].name] = idx
            idx = larger

        heap[idx] = item
        pos[item.name] = idx