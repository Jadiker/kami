from __future__ import annotations
from typing import List, Dict, Optional

class MaxHeap:
    """
    Max-heap keyed by an object's .score (higher is better) and
    identified uniquely by .name.  Requires every element to expose:
        • .score  (numeric, used for ordering)
        • .name   (hashable, unique)
    """

    __slots__ = ("_heap", "_pos")   # save memory; prevents __dict__ creation

    def __init__(self, items: Optional[List] = None) -> None:
        self._heap: List = []
        self._pos: Dict[str, int] = {}      # name -> index
        if items:
            for obj in items:
                self._heap.append(obj)
                self._pos[obj.name] = len(self._heap) - 1
            # heapify bottom-up in place
            for i in reversed(range(len(self._heap) // 2)):
                self._sift_down(i)

    # ─────────── user-facing API ───────────

    def add_or_update(self, obj) -> None:
        """
        Insert a new element or update an existing one
        (if another object with the same .name already exists).
        """
        idx = self._pos.get(obj.name)
        if idx is None:                 # ⇒ true insert
            self._heap.append(obj)
            idx = len(self._heap) - 1
            self._pos[obj.name] = idx
            self._sift_up(idx)
        else:                           # ⇒ update existing
            old_obj = self._heap[idx]
            self._heap[idx] = obj       # replace
            # decide which direction to restore heap property
            if obj.score > old_obj.score:
                self._sift_up(idx)
            elif obj.score < old_obj.score:
                self._sift_down(idx)
            # if equal: nothing to do

    def pop(self):
        """Remove and return the max-score element.  Raises IndexError if empty."""
        if not self._heap:
            raise IndexError("pop from empty heap")
        top = self._heap[0]
        last = self._heap.pop()
        del self._pos[top.name]
        if self._heap:                  # move last to root and fix
            self._heap[0] = last
            self._pos[last.name] = 0
            self._sift_down(0)
        return top

    def __len__(self) -> int:
        return len(self._heap)

    def peek(self):
        """Read-only access to current max element (or None if empty)."""
        return self._heap[0] if self._heap else None

    # ─────────── internal helpers ───────────

    def _sift_up(self, i: int) -> None:
        heap, pos = self._heap, self._pos
        item = heap[i]
        while i:
            parent = (i - 1) >> 1
            if item.score <= heap[parent].score:
                break
            heap[i] = heap[parent]
            pos[heap[parent].name] = i
            i = parent
        heap[i] = item
        pos[item.name] = i

    def _sift_down(self, i: int) -> None:
        heap, pos = self._heap, self._pos
        size = len(heap)
        item = heap[i]
        while True:
            left = (i << 1) + 1
            if left >= size:
                break
            right = left + 1
            larger = left
            if right < size and heap[right].score > heap[left].score:
                larger = right
            if heap[larger].score <= item.score:
                break
            heap[i] = heap[larger]
            pos[heap[larger].name] = i
            i = larger
        heap[i] = item
        pos[item.name] = i
