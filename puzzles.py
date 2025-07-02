from dataclasses import dataclass
from enum import StrEnum, Enum

from core import NodeID
from color import InfiniteColor
from solver import SolvablePuzzle

class PuzzleName(StrEnum):
    puzzle_3_3 = "3-3"

puzzles: dict[PuzzleName, SolvablePuzzle] = {}

def add_puzzle(name, section_to_color: dict[NodeID, InfiniteColor], touching: dict[NodeID, list[NodeID]]):
    global puzzles
    puzzle = SolvablePuzzle(valid_colors=set(section_to_color.values()))
    for section, color in section_to_color.items():
        puzzle.add_node(section, color)
    for section, neighbors in touching.items():
        for neighbor in neighbors:
            puzzle.add_edge(section, neighbor)
    puzzles[name] = puzzle

class Pz_3_3_Section(NodeID, Enum):
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

section_to_color: dict[NodeID, InfiniteColor] = {
    Pz_3_3_Section.TOP_CREAM: InfiniteColor.CREAM,
    Pz_3_3_Section.TOP_TURQUOISE: InfiniteColor.TURQUOISE,
    Pz_3_3_Section.TOP_LEFT_ORANGE: InfiniteColor.ORANGE,
    Pz_3_3_Section.MIDDLE_DARK_BLUE: InfiniteColor.DARK_BLUE,
    Pz_3_3_Section.TOP_RIGHT_ORANGE: InfiniteColor.ORANGE,
    Pz_3_3_Section.MIDDLE_LEFT_CREAM: InfiniteColor.CREAM,
    Pz_3_3_Section.MIDDLE_RIGHT_CREAM: InfiniteColor.CREAM,
    Pz_3_3_Section.BOTTOM_LEFT_ORANGE: InfiniteColor.ORANGE,
    Pz_3_3_Section.BOTTOM_RIGHT_ORANGE: InfiniteColor.ORANGE,
    Pz_3_3_Section.BOTTOM_TURQUOISE: InfiniteColor.TURQUOISE,
    Pz_3_3_Section.BOTTOM_CREAM: InfiniteColor.CREAM,
}

touching: dict[NodeID, list[NodeID]] = {
    Pz_3_3_Section.TOP_CREAM: [
        Pz_3_3_Section.TOP_TURQUOISE,
        Pz_3_3_Section.TOP_LEFT_ORANGE,
        Pz_3_3_Section.TOP_RIGHT_ORANGE,
    ],
    Pz_3_3_Section.TOP_TURQUOISE: [
        Pz_3_3_Section.TOP_CREAM,
        Pz_3_3_Section.MIDDLE_DARK_BLUE,
    ],
    Pz_3_3_Section.TOP_LEFT_ORANGE: [
        Pz_3_3_Section.TOP_CREAM,
        Pz_3_3_Section.MIDDLE_DARK_BLUE,
        Pz_3_3_Section.MIDDLE_LEFT_CREAM,
    ],
    Pz_3_3_Section.MIDDLE_DARK_BLUE: [
        Pz_3_3_Section.TOP_TURQUOISE,
        Pz_3_3_Section.TOP_LEFT_ORANGE,
        Pz_3_3_Section.TOP_RIGHT_ORANGE,
        Pz_3_3_Section.MIDDLE_LEFT_CREAM,
        Pz_3_3_Section.MIDDLE_RIGHT_CREAM,
        Pz_3_3_Section.BOTTOM_LEFT_ORANGE,
        Pz_3_3_Section.BOTTOM_RIGHT_ORANGE,
        Pz_3_3_Section.BOTTOM_TURQUOISE,
    ],
    Pz_3_3_Section.TOP_RIGHT_ORANGE: [
        Pz_3_3_Section.TOP_CREAM,
        Pz_3_3_Section.MIDDLE_DARK_BLUE,
        Pz_3_3_Section.MIDDLE_RIGHT_CREAM,
    ],
    Pz_3_3_Section.MIDDLE_LEFT_CREAM: [
        Pz_3_3_Section.TOP_LEFT_ORANGE,
        Pz_3_3_Section.MIDDLE_DARK_BLUE,
        Pz_3_3_Section.BOTTOM_LEFT_ORANGE,
    ],
    Pz_3_3_Section.MIDDLE_RIGHT_CREAM: [
        Pz_3_3_Section.TOP_RIGHT_ORANGE,
        Pz_3_3_Section.MIDDLE_DARK_BLUE,
        Pz_3_3_Section.BOTTOM_RIGHT_ORANGE,
    ],
    Pz_3_3_Section.BOTTOM_LEFT_ORANGE: [
        Pz_3_3_Section.MIDDLE_LEFT_CREAM,
        Pz_3_3_Section.MIDDLE_DARK_BLUE,
        Pz_3_3_Section.BOTTOM_CREAM,
    ],
    Pz_3_3_Section.BOTTOM_RIGHT_ORANGE: [
        Pz_3_3_Section.MIDDLE_RIGHT_CREAM,
        Pz_3_3_Section.MIDDLE_DARK_BLUE,
        Pz_3_3_Section.BOTTOM_CREAM,
    ],
    Pz_3_3_Section.BOTTOM_TURQUOISE: [
        Pz_3_3_Section.MIDDLE_DARK_BLUE,
        Pz_3_3_Section.BOTTOM_CREAM,
    ],
    Pz_3_3_Section.BOTTOM_CREAM: [
        Pz_3_3_Section.BOTTOM_LEFT_ORANGE,
        Pz_3_3_Section.BOTTOM_RIGHT_ORANGE,
        Pz_3_3_Section.BOTTOM_TURQUOISE,
    ],
}

add_puzzle(PuzzleName.puzzle_3_3, section_to_color, touching)