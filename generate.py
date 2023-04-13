from classes import *
from src.PyVMF import *
import json
import os

def string_to_class( s ):
    if s == '4-wr':
        return Wallshot( 'r', initial='4' )
    elif s == '4-wl':
        return Wallshot( 'l', initial='4' )
    elif s == '2-wr':
        return Wallshot( 'r', initial='2' )
    elif s == '2-wl':
        return Wallshot( 'l', initial='2' )
    elif s == 'wr':
        return Wallshot( 'r' )
    elif s == 'wl':
        return Wallshot( 'l' )
    elif s == 'jr':
        return Jurf( 'r' )
    elif s == 'jl':
        return Jurf( 'l' )
    elif s == 'rs':
        return Platform( 'rs' )
    elif s == 'ss':
        return Platform( 'ss' )
    elif s == 'sk':
        return Platform( 'sk' )

def strafes_to_directions( strafes ):
    directions = strafes.copy()
    directions[0] = 'y'
    for i in range( 1, len( directions ) ):
        directions[i] = direction_dict[directions[i-1]][directions[i]]

    return directions

def jump_generator( jumps, strafes, mapname, dirname, cur, next ):

    jumps_as_classes = [ string_to_class( jump ) for jump in jumps ]
    directions = strafes_to_directions( strafes )

    dummyVMF = new_vmf()
    coord = ( 0, 0, 0 )

    textures = Textures().load_textures()
    start, end = Start(), End()
    dummyVMF = addVMF( dummyVMF, start.create( cur, textures ) )

    # first get all the coordinates
    spacing_type = ''
    for i in range( len( directions ) ):
        jump, cur_dir, strafe = jumps_as_classes[i], directions[i], strafes[i]
        prev_dir = directions[i-1] if i != 0 else cur_dir
        prev_jump = jumps_as_classes[i-1] if i!= 0 else None
        prev_l_or_r = prev_jump.l_or_r if prev_jump else None
        if type(jump).__name__ in { 'Wallshot', 'Jurf' }:
            coord, spacing_type = jump.update_coord( cur_dir, prev_dir, prev_l_or_r, strafe, coord, spacing_type )
    # create the jump elements
    for jump in jumps_as_classes:
        jump_vmf = jump.create( textures  )
        dummyVMF = addVMF( dummyVMF, jump_vmf )
    dummyVMF = addVMF( dummyVMF, end.create( cur_dir, coord, next, textures  ) )
    # connectors_vmf = connectors.create( strafes, directions, textures  )
    # dummyVMF = addVMF( dummyVMF, connectors_vmf )

    os.makedirs( dirname, exist_ok=True)
    filename = os.path.join( dirname, mapname, f'jump_{cur+1}.vmf' )
    dummyVMF.export( filename )
    return filename

def multiple_jump_generator( map_list, mapname, dirname ):
    vmf_list = []
    for i in range( len( map_list ) ):
        jumps, strafes = map_list[i].jumps, map_list[i].strafes
        cur, next = i, (i+1) % len( map_list )
        vmf_file = jump_generator( jumps, strafes, mapname, dirname, cur, next )
        vmf_list.append( vmf_file )

    save_data = {
        'mapname': mapname,
        'vmf_list': vmf_list,
    }
    json_data = json.dumps( save_data, indent=2 )
    with open("settings.json", "w") as f:
        f.write(json_data)
