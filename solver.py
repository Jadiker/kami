from core import HashTracker, NodeID, Puzzle
from color import InfiniteColor
from search_algs import SearchSolver

# a move sets a node to a color (and propagates to its same-color neighbors)
Move = tuple[NodeID, InfiniteColor]

class SolvablePuzzle(Puzzle):
    def __init__(self, hasher: HashTracker | None = None, valid_colors: set[InfiniteColor] | int = 2):
        super().__init__(hasher=hasher)
        if isinstance(valid_colors, int):
            valid_colors = {InfiniteColor(i) for i in range(valid_colors)}
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

    def solve(self, max_depth: int | None = None, progress: bool = False) -> list[Move] | None:
        solver = SearchSolver(
            namer=self.search_namer,
            detector=self.search_detector,
            expander=self.search_expander,
            follower=self.search_follower,
        )
        collapsed_self = self.copy()
        collapsed_self.collapse()
        return solver.solve(collapsed_self, max_depth=max_depth, progress=progress)
    
if __name__ == '__main__':
    import puzzles
    from timer import timing

    # puzzle = puzzles.puzzles[puzzles.PuzzleName.puzzle_3_3]
    # puzzle_section_to_name = lambda section: puzzles.Pz_3_3_Section(section).name

    puzzle = puzzles.puzzles[puzzles.PuzzleName.puzzle_4_6]
    puzzle_section_to_name = lambda section: puzzles.Pz_4_6_Section(section).name

    print("Initial puzzle state:")
    puzzle.display_graph()

    times = []

    print("Solving puzzle...")
    with timing(times):
        solution = puzzle.solve(progress=True)

    solve_time = times.pop()
    print(f"Solution found in {solve_time} seconds:")
    if solution is None:
        print("No solution found.")
    else:
        for index, move in enumerate(solution):
            section_number, color = move
            print(f"{index + 1}. Set {puzzle_section_to_name(section_number)} to {color.name}")
        print(f"Total moves: {len(solution)}")