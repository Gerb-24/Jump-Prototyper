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

def num_to_move_dic_handler( num, _dir ):
    '''
        Here 1 will be a wallshot, 2 will be a platform, and 3 will be a skip
    '''
    handler = {
        1:  {
            _dir:                       textures.shoot,
            dir_handler(_dir, 'l'):     textures.side,
            dir_handler(_dir, 'r'):     textures.side,
            'z':                        textures.side,
        },
        2:  {
            'z':                        textures.walk,
            dir_handler(_dir, 'r'):     textures.side,
            dir_handler(_dir, 'l'):     textures.side,
            _dir:                       textures.side,
            dir_handler(_dir, 'l'):     textures.side,
        },
        3:  {
            'z':                        textures.skip,
            dir_handler(_dir, 'r'):     textures.side,
            dir_handler(_dir, 'l'):     textures.side,
            _dir:                       textures.side,
            dir_handler(_dir, 'l'):     textures.side,
        },
    }
    return handler[num]

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
        move_dic = {
            'x':        x_diff,
            '-y':       y_diff,
            'z':        z_max,
        }
        
        mat_dic = num_to_move_dic_handler( jump_item.num, _dir )
        proto = AbstractBrush(move_dic, mat_dic).create( ( x_min, -y_min, 0 ), textures )
        dummy_vmf = addVMF( dummy_vmf, proto )
    dummy_vmf.export( 'vmfs/prototype/test1.vmf' )



