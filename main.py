from generate import multiple_jump_generator
from classes import Jump

dirname = './vmfs'
mapname = 'testing'
map_list = [
    Jump(
        [ 'wl', 'rs', 'wr', 'jl' ],
        ['-', '-', 'r', '-' ],
    ),
    Jump(
        [ 'wr', 'jr', 'wr', 'rs', 'wr' ],
        ['-', 'r', '-',  'r', '-' ],
    ),
    Jump(
        [ 'ss', 'sk', 'wr', 'rs', 'wr' ],
        ['-', '-', '-',  'r', '-' ],
    ),
]

multiple_jump_generator( map_list, mapname, dirname )
