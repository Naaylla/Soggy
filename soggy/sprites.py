PALETTE = {
    "#": "#000000",
    "F": "#c58b36",
    "L": "#edc45e",
    "T": "#65afb0",
    "N": "#8e496e",
    "E": "#000000",
}


FRONT = [
    "..#.....#..",
    ".#F#...#F#.",
    ".#LF###FL#.",
    ".#FFFFFFF#.",
    "#FF#FFF#FF#",
    "#FFFFNFFFF#",
    "#FFF#F#FFF#",
    ".#FFFFFFF#.",
    ".#FFLLLFF#.",
    ".#FF###FF#.",
    "..##...##..",
]

SLEEP = [
    ".###...####",
    "#FLF###FLF#",
    ".#FFFFFFF#.",
    "#F##FFF##F#",
    "#FFFFNFFFF#",
    "#FFF#F#FFF#",
    ".#FFFFFFF#.",
    ".#FFLLLFF#.",
    "..########.",
]


SIDE_RIGHT = [
    ".......#....",
    "......#F#...",
    "......#LF##.",
    "......#FFF##",
    ".#...#FFF#F#",
    "#F##FFFFFEN#",
    ".#F#FFFFFF#.",
    "..##FFFFFF#.",
    "...#FLLLLF#.",
    "...#F####F#.",
    "...##...##..",
]

def side_walk_frame(lifted_leg=None):
    grid = [list(row) for row in SIDE_RIGHT]
    if lifted_leg == "left":
        grid[9][4] = "#"
        grid[10][3:5] = [".", "."]
    elif lifted_leg == "right":
        grid[9][9] = "#"
        grid[10][8:10] = [".", "."]
    return ["".join(row) for row in grid]


SIDE_WALK_RIGHT = [
    side_walk_frame(),
    side_walk_frame("left"),
    side_walk_frame(),
    side_walk_frame("right"),
]
SIDE_WALK = [[row[::-1] for row in grid] for grid in SIDE_WALK_RIGHT]
SIDE = SIDE_WALK[0]


def side_frame(index):
    return {
        "grid": SIDE_WALK[index],

        "tears": [(2, 5)],
        "offsets": (0,),
        "head_top": (4, 0),
    }


FRAME_SIT = {
    "grid": FRONT,
    "tears": [(3, 5), (7, 5)],
    "offsets": (0, 4),
    "head_top": (8, 0),
}
FRAME_SLEEP = {
    "grid": SLEEP,
    "tears": [],
    "offsets": (),
    "head_top": (9, 0),
}
FRAME_WALK = [side_frame(i) for i in range(4)]
FRONT_ROWS = len(FRONT)


for sprite in (FRONT, SLEEP, SIDE):
    width = len(sprite[0])
    assert all(len(row) == width for row in sprite), "Sprite rows have unequal widths"
for frame in FRAME_WALK:
    width = len(frame["grid"][0])
    assert all(len(row) == width for row in frame["grid"])


def tear_phase(t):
    if t < 3:
        return True, None
    if t == 3:
        return True, 1
    if t == 4:
        return False, 2
    if t == 5:
        return False, 3
    return False, None
