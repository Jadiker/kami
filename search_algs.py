'''Classes for solving problems that can be modeled as a directed graph with goal nodes'''
from dataclasses import dataclass
from collections import deque
from typing import Callable, Iterable, List, Deque, Tuple, Dict, Optional, Hashable, Generic, TypeVar
from minheap import HeapItem, MinHeap, GenericScore

from tqdm import tqdm

# Type definitions
# representation of the state - same states do not need to have the same representation
GenericInfo = TypeVar('GenericInfo')
# hashable representation of the state - same states must have the same hashable representation
# usually, this is just a hashed or string version of GenericInfo
GenericName = TypeVar('GenericName', bound=Hashable)
# representation of the action
GenericMove = TypeVar('GenericMove')

class NodeSolver(Generic[GenericInfo, GenericName, GenericMove]):
    '''Class for modeling problems that can be modeled as a directed graph with goal nodes'''
    def __init__(
            self,
            namer:    Callable[[GenericInfo], GenericName],
            detector: Callable[[GenericInfo], bool],
            expander: Callable[[GenericInfo], Iterable[GenericMove]],
            follower: Callable[[GenericInfo, GenericMove], GenericInfo]
):
        '''
        Whatever decides to use this gets to define what structure info is.
        namer: takes info representing a node and returns a hashable object (the name);
               names must be equal if and only if the nodes are equal
        detector: takes info and returns True if the node represented by the info is the goal node,
                  ...False otherwise.
        expander: takes info and returns an iterable of moves that can be made from the node
                  ...that the info represents. (a.k.a. paths leading out of that node)
        follower: takes info and a move that can be made from the node that the info represents,
                  ...and returns the info that represents the node that the move leads to
        '''
        self.get_name = namer
        self.is_goal = detector
        self.get_moves = expander
        self.follow_move = follower

class BFSSolver(NodeSolver[GenericInfo, GenericName, GenericMove]):
    def __init__(
        self,
        namer: Callable[[GenericInfo], GenericName],
        detector: Callable[[GenericInfo], bool],
        expander: Callable[[GenericInfo], Iterable[GenericMove]],
        follower: Callable[[GenericInfo, GenericMove], GenericInfo],
    ) -> None:
        super().__init__(namer, detector, expander, follower)

    '''Class for solving node problems with BFS to reach the goal node.'''
    def solve(
        self,
        start_info: GenericInfo,
        progress: bool = False,
    ) -> Optional[List[GenericMove]]:
        """Solve using BFS and optionally show progress bars."""
        if progress:
            return self._solve_with_progress(start_info)
        return self._solve_without_progress(start_info)

    def _solve_without_progress(
        self, start_info: GenericInfo
    ) -> Optional[List[GenericMove]]:
        """Standard BFS without progress bars."""
        if self.is_goal(start_info):
            return []

        start_name = self.get_name(start_info)

        name_to_data: Dict[GenericName, Tuple[GenericInfo, List[GenericMove]]] = {
            start_name: (start_info, [])
        }
        queue: Deque[GenericName] = deque([start_name])

        while queue:
            current_name = queue.popleft()
            current_info, current_path = name_to_data[current_name]

            expanded_moves = self.get_moves(current_info)
            for move in expanded_moves:
                child_info = self.follow_move(current_info, move)
                child_path = current_path + [move]

                if self.is_goal(child_info):
                    return child_path

                child_name = self.get_name(child_info)
                if child_name not in name_to_data:
                    name_to_data[child_name] = (child_info, child_path)
                    queue.append(child_name)
        return None

    def _solve_with_progress(
        self, start_info: GenericInfo
    ) -> Optional[List[GenericMove]]:
        """BFS with layer-wise tqdm progress bars."""
        if self.is_goal(start_info):
            return []

        start_name = self.get_name(start_info)

        name_to_data: Dict[GenericName, Tuple[GenericInfo, List[GenericMove]]] = {
            start_name: (start_info, [])
        }
        queue: Deque[GenericName] = deque([start_name])
        depth = 0

        while queue:
            layer_size = len(queue)
            bar = tqdm(total=layer_size, desc=f"Depth {depth}", leave=True)

            for _ in range(layer_size):
                current_name = queue.popleft()
                current_info, current_path = name_to_data[current_name]

                moves = list(self.get_moves(current_info))
                for move in moves:
                    child_info = self.follow_move(current_info, move)
                    child_path = current_path + [move]

                    if self.is_goal(child_info):
                        bar.close()
                        return child_path

                    child_name = self.get_name(child_info)
                    if child_name not in name_to_data:
                        name_to_data[child_name] = (child_info, child_path)
                        queue.append(child_name)

                bar.update(1)

            bar.close()
            depth += 1

        return None

@dataclass
class SolutionHeapItem(
    HeapItem[GenericName, GenericScore],
    Generic[GenericName, GenericScore, GenericInfo]
    ):
    name: GenericName
    score: GenericScore
    info: GenericInfo

# ---------------------------------------------------------------------------
#  Fast A* searcher
# ---------------------------------------------------------------------------
class AStarSolver(
    NodeSolver[GenericInfo, GenericName, GenericMove],
    Generic[GenericInfo, GenericName, GenericMove, GenericScore]
):
    """Extremely efficient A* (min-heap, O(E log V))."""

    def __init__(
        self,
        namer:      Callable[[GenericInfo], GenericName],
        detector:   Callable[[GenericInfo], bool],
        expander:   Callable[[GenericInfo], Iterable[GenericMove]],
        follower:   Callable[[GenericInfo, GenericMove], GenericInfo],
        heuristic:  Callable[[GenericInfo], GenericScore],
        cost: Callable[[GenericInfo, GenericMove, GenericInfo], GenericScore],
        init_generic_score: GenericScore
    ) -> None:
        super().__init__(namer, detector, expander, follower)
        self.heuristic = heuristic
        self.cost = cost
        self.init_generic_score = init_generic_score
        self.heap: MinHeap[
            GenericName, GenericScore,
            SolutionHeapItem[GenericName, GenericScore,
                             GenericInfo]
        ] = MinHeap()

        # internal tables (allocated per call in `solve`)
        self._g: Dict[GenericName, GenericScore]                         # cost so far
        self._parent: Dict[GenericName, Tuple[GenericName, GenericMove]] # back-edges

    # -----------------------------------------------------------------------
    #  Public entry point
    # -----------------------------------------------------------------------
    def solve(self, start_info: GenericInfo) -> Optional[List[GenericMove]]:
        """
        Run A* and return the sequence of moves that reaches a goal,
        or None if no solution exists.
        """
        namer, detector = self.get_name, self.is_goal
        expander, follower = self.get_moves, self.follow_move
        heuristic, cost_fn = self.heuristic, self.cost
        heap = self.heap

        # ── initialise ────────────────────────────────────────────────────
        start_name: GenericName = namer(start_info)
        self._g = {start_name: self.init_generic_score}
        self._parent = {}

        f_start: GenericScore = self._g[start_name] + heuristic(start_info)
        heap.add_or_update(SolutionHeapItem(
            name=start_name,
            score=f_start,
            info=start_info,
        ))

        closed: set[GenericName] = set()

        # ── main loop ─────────────────────────────────────────────────────
        while heap:
            node = heap.pop()                 # node with smallest f
            name = node.name

            if detector(node.info):           # goal reached
                return self._reconstruct_path(name)

            closed.add(name)
            g_curr: GenericScore = self._g[name]

            for move in expander(node.info):
                nxt_info  = follower(node.info, move)
                nxt_name  = namer(nxt_info)
                if nxt_name in closed:
                    continue

                edge_cost: GenericScore = cost_fn(node.info, move, nxt_info)
                tentative_g: GenericScore = g_curr + edge_cost

                better_path = (
                    nxt_name not in self._g or tentative_g < self._g[nxt_name]
                )
                if better_path:
                    self._g[nxt_name] = tentative_g
                    self._parent[nxt_name] = (name, move)

                    f: GenericScore = tentative_g + heuristic(nxt_info)
                    heap.add_or_update(SolutionHeapItem(
                        name=nxt_name,
                        score=f,
                        info=nxt_info,
                    ))

        return None  # frontier exhausted, no goal found

    # -----------------------------------------------------------------------
    #  Helpers
    # -----------------------------------------------------------------------
    def _reconstruct_path(self, goal_name: GenericName) -> List[GenericMove]:
        path: List[GenericMove] = []
        parent = self._parent
        cur = goal_name
        while cur in parent:
            cur, mv = parent[cur]
            path.append(mv)
        path.reverse()
        return path