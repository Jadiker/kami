from core import Color, HashTracker, NodeID, Puzzle
from search_algs import SearchSolver

# a move sets a node to a color (and propagates to its same-color neighbors)
Move = tuple[NodeID, Color]

class SolvablePuzzle(Puzzle):
    def __init__(self, hasher: HashTracker | None = None, valid_colors: set[Color] | int = 2):
        super().__init__(hasher=hasher)
        if isinstance(valid_colors, int):
            valid_colors = {Color(i) for i in range(valid_colors)}
        self.valid_colors = valid_colors

    def copy(self) -> 'SolvablePuzzle':
        new_puzzle = SolvablePuzzle(hasher=self.hasher, valid_colors=self.valid_colors)
        new_puzzle.graph = self.graph.copy()
        return new_puzzle

    def get_valid_moves(self) -> list[Move]:
        return [
            (node, color)
            for node in self.graph.nodes
            for color in self.valid_colors
            if color != self.get_color(node)
        ]

    @classmethod
    def search_namer(cls, puzzle: 'SolvablePuzzle') -> str:
        return puzzle.full_hash
    
    @classmethod
    def search_detector(cls, puzzle: 'SolvablePuzzle') -> bool:
        return puzzle.is_solved
    
    @classmethod
    def search_expander(cls, puzzle: 'SolvablePuzzle') -> list[Move]:
        return puzzle.get_valid_moves()
    
    @classmethod
    def search_follower(cls, puzzle: 'SolvablePuzzle', move: Move) -> 'SolvablePuzzle':
        node, color = move
        new_puzzle = puzzle.copy()
        new_puzzle.set_color(node, color, propagate=True)
        new_puzzle.collapse()
        return new_puzzle

    def solve(self) -> list[Move] | None:
        solver = SearchSolver(
            namer=self.search_namer,
            detector=self.search_detector,
            expander=self.search_expander,
            follower=self.search_follower,
            breadth=True
        )
        return solver.solve(self)
    
if __name__ == '__main__':
    from enum import Enum
    puzzle = SolvablePuzzle(valid_colors={Color.TURQUOISE, Color.CREAM, Color.ORANGE, Color.DARK_BLUE})

    class PuzzleSection(int, Enum):
        TOP_CREAM = 0
        TOP_TURQUOISE = 1
        TOP_LEFT_ORANGE = 2
        MIDDLE_DARK_BLUE = 3
        TOP_RIGHT_ORANGE = 4
        MIDDLE_LEFT_CREAM = 5
        MIDDLE_RIGHT_CREAM = 6
        BOTTOM_LEFT_ORANGE = 7
        BOTTOM_RIGHT_ORANGE = 8
        BOTTOM_TURQUOISE = 9
        BOTTOM_CREAM = 10

    section_to_color: dict[PuzzleSection, Color] = {
        PuzzleSection.TOP_CREAM: Color.CREAM,
        PuzzleSection.TOP_TURQUOISE: Color.TURQUOISE,
        PuzzleSection.TOP_LEFT_ORANGE: Color.ORANGE,
        PuzzleSection.MIDDLE_DARK_BLUE: Color.DARK_BLUE,
        PuzzleSection.TOP_RIGHT_ORANGE: Color.ORANGE,
        PuzzleSection.MIDDLE_LEFT_CREAM: Color.CREAM,
        PuzzleSection.MIDDLE_RIGHT_CREAM: Color.CREAM,
        PuzzleSection.BOTTOM_LEFT_ORANGE: Color.ORANGE,
        PuzzleSection.BOTTOM_RIGHT_ORANGE: Color.ORANGE,
        PuzzleSection.BOTTOM_TURQUOISE: Color.TURQUOISE,
        PuzzleSection.BOTTOM_CREAM: Color.CREAM,
    }

    for section, color in section_to_color.items():
        puzzle.add_node(section, color)
        
    touching: dict[PuzzleSection, list[PuzzleSection]] = {
        PuzzleSection.TOP_CREAM: [
            PuzzleSection.TOP_TURQUOISE,
            PuzzleSection.TOP_LEFT_ORANGE,
            PuzzleSection.TOP_RIGHT_ORANGE,
        ],
        PuzzleSection.TOP_TURQUOISE: [
            PuzzleSection.TOP_CREAM,
            PuzzleSection.MIDDLE_DARK_BLUE,
        ],
        PuzzleSection.TOP_LEFT_ORANGE: [
            PuzzleSection.TOP_CREAM,
            PuzzleSection.MIDDLE_DARK_BLUE,
            PuzzleSection.MIDDLE_LEFT_CREAM,
        ],
        PuzzleSection.MIDDLE_DARK_BLUE: [
            PuzzleSection.TOP_TURQUOISE,
            PuzzleSection.TOP_LEFT_ORANGE,
            PuzzleSection.TOP_RIGHT_ORANGE,
            PuzzleSection.MIDDLE_LEFT_CREAM,
            PuzzleSection.MIDDLE_RIGHT_CREAM,
            PuzzleSection.BOTTOM_LEFT_ORANGE,
            PuzzleSection.BOTTOM_RIGHT_ORANGE,
            PuzzleSection.BOTTOM_TURQUOISE,
        ],
        PuzzleSection.TOP_RIGHT_ORANGE: [
            PuzzleSection.TOP_CREAM,
            PuzzleSection.MIDDLE_DARK_BLUE,
            PuzzleSection.MIDDLE_RIGHT_CREAM,
        ],
        PuzzleSection.MIDDLE_LEFT_CREAM: [
            PuzzleSection.TOP_LEFT_ORANGE,
            PuzzleSection.MIDDLE_DARK_BLUE,
            PuzzleSection.BOTTOM_LEFT_ORANGE,
        ],
        PuzzleSection.MIDDLE_RIGHT_CREAM: [
            PuzzleSection.TOP_RIGHT_ORANGE,
            PuzzleSection.MIDDLE_DARK_BLUE,
            PuzzleSection.BOTTOM_RIGHT_ORANGE,
        ],
        PuzzleSection.BOTTOM_LEFT_ORANGE: [
            PuzzleSection.MIDDLE_LEFT_CREAM,
            PuzzleSection.MIDDLE_DARK_BLUE,
            PuzzleSection.BOTTOM_CREAM,
        ],
        PuzzleSection.BOTTOM_RIGHT_ORANGE: [
            PuzzleSection.MIDDLE_RIGHT_CREAM,
            PuzzleSection.MIDDLE_DARK_BLUE,
            PuzzleSection.BOTTOM_CREAM,
        ],
        PuzzleSection.BOTTOM_TURQUOISE: [
            PuzzleSection.MIDDLE_DARK_BLUE,
            PuzzleSection.BOTTOM_CREAM,
        ],
        PuzzleSection.BOTTOM_CREAM: [
            PuzzleSection.BOTTOM_LEFT_ORANGE,
            PuzzleSection.BOTTOM_RIGHT_ORANGE,
            PuzzleSection.BOTTOM_TURQUOISE,
        ],
    }

    for section, neighbors in touching.items():
        for neighbor in neighbors:
            puzzle.add_edge(section, neighbor)

    print("Initial puzzle state:")
    puzzle.display_graph()

    from timer import timing

    times = []

    print("Solving puzzle...")
    with timing(times):
        solution = puzzle.solve()

    print(f"Solution found in {times[-1]} seconds:")
    if solution is None:
        print("No solution found.")
    else:
        for index, move in enumerate(solution):
            section_number, color = move
            print(f"{index + 1}. Set {PuzzleSection(section_number).name} to {color.name}")
        print(f"Total moves: {len(solution)}")