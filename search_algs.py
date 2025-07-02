'''Classes for solving problems that can be modeled as a directed graph with goal nodes'''

from collections import deque
from typing import Callable, Iterable, List, Deque, Tuple, Dict, Optional, Hashable, Generic, TypeVar

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

class SearchSolver(NodeSolver[GenericInfo, GenericName, GenericMove]):
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
        self, start_info: GenericInfo, max_depth: int | None = None
    ) -> Optional[List[GenericMove]]:
        '''
        Return the list of moves required to reach the goal node from
        ``start_info``.

        When ``max_depth`` is provided, the search stops expanding paths
        longer than this value and returns ``None`` if no solution is found
        within the limit.
        '''
        if self.is_goal(start_info):
            return []

        start_name = self.get_name(start_info)

        # data is in the form (info, path)
        name_to_data: Dict[GenericName, Tuple[GenericInfo, List[GenericMove]]] = {
            start_name: (start_info, [])
        }
        queue: Deque[GenericName] = deque([start_name])

        while queue:
            current_name = queue.popleft()
            current_info, current_path = name_to_data[current_name]

            if max_depth is not None and len(current_path) >= max_depth:
                # Can't expand this node further
                continue

            expanded_moves = self.get_moves(current_info)
            for move in expanded_moves:
                child_info = self.follow_move(current_info, move)
                child_path = current_path + [move]

                if self.is_goal(child_info):
                    return child_path

                if max_depth is not None and len(child_path) >= max_depth:
                    continue

                child_name = self.get_name(child_info)
                if child_name not in name_to_data:
                    name_to_data[child_name] = (child_info, child_path)
                    queue.append(child_name)
        return None
