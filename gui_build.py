from classes import *
from src.PyVMF import *
from classes import Textures, AbstractBrush

factor = 128/32
z_value = 4*128
prototype_vmf = load_vmf('vmfs/prototype.vmf')

textures = Textures()
textures_dic = {
    1:  'customdev/dev_measurewall01red'.upper(),
    2:  'orange_dev/dev_measurewall_green03'.upper(),
    3:  'customdev/dev_measurewall01blu'.upper(),
}

def generate_vmf( jump_items ):
    num_to_dir = {
        0:  'x',
        1:  '-y',
        2:  '-x',
        3:  'y',
    }
    dummy_vmf = new_vmf()
    for jump_item in jump_items:
        x_min, y_min, x_diff, y_diff = jump_item.dims
        x_min, y_min, x_diff, y_diff = x_min*factor, y_min*factor, x_diff*factor, y_diff*factor
        move_dic = {
            'x':        x_diff,
            '-y':       y_diff,
            'z':        z_value,
        }
        mat_dic = {
            'z':                        textures_dic[jump_item.num],
            num_to_dir[jump_item.dir]:  'dev/reflectivity_70'.upper(),
        }
        proto = AbstractBrush(move_dic, mat_dic).create( ( x_min, -y_min, 0 ), textures )
        dummy_vmf = addVMF( dummy_vmf, proto )
    dummy_vmf.export( 'vmfs/prototype/test1.vmf' )



