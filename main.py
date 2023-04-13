from generate import multiple_jump_generator
from classes import Jump

dirname = './vmfs'
mapname = 'testing'
map_list = [
    Jump(
        [ '4-wr', 'wr', 'wl', 'wl' ],
        ['-', '-', 'l', 'r' ],
    ),
    Jump(
        [ '2-wr', 'wr', 'wl', 'wl' ],
        ['-', 'l', 'r', 'r' ],
    ),
    # Jump(
    #     [ 'wr', 'rs', 'wl', 'jr' ],
    #     ['-', '-', 'r', '-' ],
    # ),
    # Jump(
    #     [ 'wl', 'jl', 'wl', 'rs', 'wl' ],
    #     ['-', 'r', '-',  'r', '-' ],
    # ),
    # Jump(
    #     [ 'ss', 'sk', 'wl', 'rs', 'wl' ],
    #     ['-', '-', '-',  'r', '-' ],
    # ),
]

multiple_jump_generator( map_list, mapname, dirname )
