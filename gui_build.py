from classes import *
from src.PyVMF import *
from classes import Textures, AbstractBrush

def dir_handler( _dir, s ):
    '''
    Here we use: 'l' for turn left, 'r' for turn right, 'o' for opposite, and '-' for do nothing
    '''
    direction_dict = {
                'x':
                    {
                    'r':    '-y',
                    'l':    'y',
                    '-':    'x',
                    'o':    '-x',
                    },
                'y':
                    {
                    'r':    'x',
                    'l':    '-x',
                    '-':    'y',
                    'o':    '-y',
                    },
                '-x':
                    {
                    'r':    'y',
                    'l':    '-y',
                    '-':    '-x',
                    'o':    'x',
                    },
                '-y':
                    {
                    'r':    '-x',
                    'l':    'x',
                    '-':    '-y',
                    'o':    'y',
                    },
                }
    return direction_dict[_dir][s]

def type_to_move_dic_handler( type, _dir ):
    '''
        Here 0 will be a wallshot, 1 will be a platform, and 2 will be a skip
    '''
    handler = {
        0:  {
            _dir:                       textures.shoot,
            dir_handler(_dir, 'l'):     textures.side,
            dir_handler(_dir, 'r'):     textures.side,
            'z':                        textures.side,
        },
        1:  {
            'z':                        textures.walk,
            dir_handler(_dir, 'r'):     textures.side,
            dir_handler(_dir, 'l'):     textures.side,
            _dir:                       textures.side,
            dir_handler(_dir, 'l'):     textures.side,
        },
        2:  {
            'z':                        textures.skip,
            dir_handler(_dir, 'r'):     textures.side,
            dir_handler(_dir, 'l'):     textures.side,
            _dir:                       textures.side,
            dir_handler(_dir, 'l'):     textures.side,
        },
        3: {
            'z':                        textures.walk,
            dir_handler(_dir, 'r'):     textures.side,
            dir_handler(_dir, 'l'):     textures.side,
            _dir:                       textures.side,
            dir_handler(_dir, 'l'):     textures.side,
        },
    }
    return handler[type]

def ramp_to_factor( ramp ):
    handler = {
        0:  0,
        1:  1/2,
        2:  2/3,
        3:  2/1,
    }
    return handler[ ramp ]


factor = 128/32
prototype_vmf = load_vmf('vmfs/prototype.vmf')

textures = Textures()
textures.load_textures()

def generate_vmf( jump_items ):
    num_to_dir = {
        0:  'x',
        1:  '-y',
        2:  '-x',
        3:  'y',
    }
    dummy_vmf = new_vmf()
    for jump_item in jump_items:
        z_max = jump_item.get_z_max() * 128
        x_min, y_min, x_diff, y_diff = jump_item.dims
        x_min, y_min, x_diff, y_diff = x_min*factor, y_min*factor, x_diff*factor, y_diff*factor
        _dir = num_to_dir[jump_item.dir]

        if _dir in { 'x', '-x' }:
            length = x_diff
            width = y_diff
        else:
            length = y_diff
            width = x_diff

        move_dic = {
            'x':        x_diff,
            '-y':       y_diff,
            'z':        z_max,
        }

        combined = None
        if jump_item.type in {1,2} and jump_item.ramp != 0:
            combined = {
            'keys': ( _dir, 'z' ),
            'val': ramp_to_factor( jump_item.ramp ) * length
        }
        elif jump_item.type in {3}:
            combined = {
            'keys': ( dir_handler(_dir,'o'), 'z' ),
            'val': length + 8
        }
        
        mat_dic = type_to_move_dic_handler( jump_item.type, _dir )
        proto = AbstractBrush(move_dic, mat_dic).create( ( x_min, -y_min, 0 ), textures, combined=combined )
        dummy_vmf = addVMF( dummy_vmf, proto )
    dummy_vmf.export( 'vmfs/prototype/test1.vmf' )



