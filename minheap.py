from __future__ import annotations

from typing import (
    Any, Dict, Self, Generic, Hashable, Iterable, List, Optional,
    Protocol, TypeVar, runtime_checkable
)

# ────────────────────────────
#  Generic parameters
# ────────────────────────────
GenericName  = TypeVar("GenericName", bound=Hashable)              # unique key
GenericCost = TypeVar("GenericCost", bound="AddableComparable")  # ordered and can add

# ────────────────────────────
#  Minimal contract for something you can sort and add.
# ────────────────────────────
class AddableComparable(Protocol):
    def __lt__(self, other: Self, /) -> bool: ...   # total order
    def __le__(self, other: Self, /) -> bool: ...
    def __add__(self, other: Self, /) -> Self: ...  # closed under +

@runtime_checkable
class HeapItem(Protocol[GenericName, GenericCost]):
    name: GenericName
    cost: GenericCost

ItemT = TypeVar("ItemT", bound=HeapItem[Any, Any])

# ────────────────────────────
#  Min-heap implementation
# ────────────────────────────
class MinHeap(Generic[GenericName, GenericCost, ItemT]):
    """Array-backed min-heap keyed by .cost and addressed by .name."""

    __slots__ = ("_heap", "_pos")

    # ── construction ──
    def __init__(self, items: Optional[Iterable[ItemT]] = None) -> None:
        self._heap: List[ItemT] = []
        self._pos: Dict[GenericName, int] = {}
        if items:
            for o in items:
                self._pos[o.name] = len(self._heap)
                self._heap.append(o)
            for i in reversed(range(len(self._heap) // 2)):
                self._sift_down(i)

    # ── public API ──
    def add_or_update(self, obj: ItemT) -> None:
        idx = self._pos.get(obj.name)
        if idx is None:                       # insert
            idx = len(self._heap)
            self._heap.append(obj)
            self._pos[obj.name] = idx
            self._sift_up(idx)
        else:                                 # update existing
            old = self._heap[idx]
            self._heap[idx] = obj
            if obj.cost < old.cost:
                self._sift_up(idx)
            elif obj.cost > old.cost:
                self._sift_down(idx)

    def pop(self) -> ItemT:
        if not self._heap:
            raise IndexError("pop from empty heap")
        top: ItemT = self._heap[0]
        last: ItemT = self._heap.pop()
        del self._pos[top.name]
        if self._heap:
            self._heap[0] = last
            self._pos[last.name] = 0
            self._sift_down(0)
        return top

    def peek(self) -> Optional[ItemT]:
        return self._heap[0] if self._heap else None

    # Pythonic helpers
    def __len__(self) -> int:          # len(heap)
        return len(self._heap)

    def __bool__(self) -> bool:        # bool(heap)
        return bool(self._heap)

    # ── internal sift helpers ──
    def _sift_up(self, idx: int) -> None:
        heap, pos = self._heap, self._pos
        item = heap[idx]
        while idx:
            parent = (idx - 1) >> 1
            if item.cost >= heap[parent].cost:
                break
            heap[idx] = heap[parent]
            pos[heap[parent].name] = idx
            idx = parent
        heap[idx] = item
        pos[item.name] = idx

    def _sift_down(self, idx: int) -> None:
        heap, pos = self._heap, self._pos
        size = len(heap)
        item = heap[idx]
        while True:
            left = (idx << 1) + 1
            if left >= size:
                break
            right = left + 1
            smaller = right if right < size and heap[right].cost < heap[left].cost else left
            if heap[smaller].cost >= item.cost:
                break
            heap[idx] = heap[smaller]
            pos[heap[smaller].name] = idx
            idx = smaller
        heap[idx] = item
        pos[item.name] = idx
