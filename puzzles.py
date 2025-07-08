from dataclasses import dataclass
from enum import StrEnum, Enum

import networkx as nx

from core import NodeID
from color import InfiniteColor
from solver import SolvablePuzzle

class PuzzleName(StrEnum):
    puzzle_3_3 = "3-3"
    puzzle_4_6 = "4-6"

puzzles: dict[PuzzleName, SolvablePuzzle] = {}

def add_puzzle(name, section_to_color: dict[NodeID, InfiniteColor], touching: dict[NodeID, list[NodeID]]):
    global puzzles
    puzzle = SolvablePuzzle(valid_colors=set(section_to_color.values()))
    for section, color in section_to_color.items():
        puzzle.add_node(section, color)
    for section, neighbors in touching.items():
        for neighbor in neighbors:
            puzzle.add_edge(section, neighbor)

    # Ensure that all the sections are connected
    assert nx.is_connected(puzzle.graph), f"Puzzle {name} is not connected"
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


class Pz_4_6_Section(NodeID, Enum):
    ALL_STRIPE_1 = 0
    LEFT_STRIPE_2 = 1
    RIGHT_STRIPE_2 = 2
    ALL_STRIPE_3 = 3
    LEFT_STRIPE_4 = 4
    BOTTOM_STRIPE_4 = 5
    RIGHT_STRIPE_4 = 6
    ALL_STRIPE_5 = 7
    ALL_HEX_1 = 8
    LEFT_HEX_2 = 9
    MIDDLE_STAR_2 = 10
    RIGHT_HEX_2 = 11
    LEFT_HEX_3 = 12
    MIDDLE_HEX_3 = 13
    RIGHT_HEX_3 = 14
    LEFT_HEX_4 = 15
    MIDDLE_HEX_4 = 16
    RIGHT_STAR_4 = 17
    ALL_HEX_5 = 18

section_to_color_4_6: dict[NodeID, InfiniteColor] = {
    Pz_4_6_Section.ALL_STRIPE_1: InfiniteColor.DARK_BLUE,

    Pz_4_6_Section.LEFT_STRIPE_2: InfiniteColor.RED,
    Pz_4_6_Section.RIGHT_STRIPE_2: InfiniteColor.RED,

    Pz_4_6_Section.ALL_STRIPE_3: InfiniteColor.CREAM,

    Pz_4_6_Section.LEFT_STRIPE_4: InfiniteColor.DARK_BLUE,
    Pz_4_6_Section.BOTTOM_STRIPE_4: InfiniteColor.DARK_BLUE,
    Pz_4_6_Section.RIGHT_STRIPE_4: InfiniteColor.DARK_BLUE,

    Pz_4_6_Section.ALL_STRIPE_5: InfiniteColor.RED,

    Pz_4_6_Section.ALL_HEX_1: InfiniteColor.CREAM,

    Pz_4_6_Section.LEFT_HEX_2: InfiniteColor.CREAM,
    Pz_4_6_Section.MIDDLE_STAR_2: InfiniteColor.DARK_BLUE,
    Pz_4_6_Section.RIGHT_HEX_2: InfiniteColor.CREAM,

    Pz_4_6_Section.LEFT_HEX_3: InfiniteColor.RED,
    Pz_4_6_Section.MIDDLE_HEX_3: InfiniteColor.DARK_BLUE,
    Pz_4_6_Section.RIGHT_HEX_3: InfiniteColor.RED,

    Pz_4_6_Section.LEFT_HEX_4: InfiniteColor.CREAM,
    Pz_4_6_Section.MIDDLE_HEX_4: InfiniteColor.RED,
    Pz_4_6_Section.RIGHT_STAR_4: InfiniteColor.CREAM,

    Pz_4_6_Section.ALL_HEX_5: InfiniteColor.CREAM
}

touching_4_6: dict[NodeID, list[NodeID]] = {
    Pz_4_6_Section.ALL_STRIPE_1: [
        Pz_4_6_Section.ALL_HEX_1,

        Pz_4_6_Section.LEFT_STRIPE_2,
        Pz_4_6_Section.RIGHT_STRIPE_2,
    ],
    Pz_4_6_Section.LEFT_STRIPE_2: [
        Pz_4_6_Section.ALL_STRIPE_1,

        Pz_4_6_Section.LEFT_HEX_2,
        Pz_4_6_Section.MIDDLE_STAR_2,

        Pz_4_6_Section.ALL_STRIPE_3
    ],
    Pz_4_6_Section.RIGHT_STRIPE_2: [
        Pz_4_6_Section.ALL_STRIPE_1,

        Pz_4_6_Section.MIDDLE_STAR_2,
        Pz_4_6_Section.RIGHT_HEX_2,

        Pz_4_6_Section.ALL_STRIPE_3
    ],
    Pz_4_6_Section.ALL_STRIPE_3: [
        Pz_4_6_Section.LEFT_STRIPE_2,
        Pz_4_6_Section.RIGHT_STRIPE_2,

        Pz_4_6_Section.LEFT_HEX_3,
        Pz_4_6_Section.MIDDLE_HEX_3,
        Pz_4_6_Section.RIGHT_HEX_3,

        Pz_4_6_Section.LEFT_STRIPE_4,
        Pz_4_6_Section.RIGHT_STRIPE_4
    ],
    Pz_4_6_Section.LEFT_STRIPE_4: [
        Pz_4_6_Section.ALL_STRIPE_3,

        Pz_4_6_Section.LEFT_HEX_4,
        Pz_4_6_Section.MIDDLE_HEX_4,
        Pz_4_6_Section.RIGHT_STAR_4,

        Pz_4_6_Section.ALL_STRIPE_5
    ],

    Pz_4_6_Section.BOTTOM_STRIPE_4: [
        Pz_4_6_Section.RIGHT_STAR_4,

        Pz_4_6_Section.ALL_STRIPE_5
    ],

    Pz_4_6_Section.RIGHT_STRIPE_4: [
        Pz_4_6_Section.ALL_STRIPE_3,

        Pz_4_6_Section.RIGHT_STAR_4,
    ],

    Pz_4_6_Section.ALL_STRIPE_5: [
        Pz_4_6_Section.LEFT_STRIPE_4,
        Pz_4_6_Section.BOTTOM_STRIPE_4,

        Pz_4_6_Section.ALL_HEX_5
    ]

    # None of the hexes or stars touch so just mapping the stripes is enough
}

add_puzzle(PuzzleName.puzzle_4_6, section_to_color_4_6, touching_4_6)