from math import sqrt, cos, sin, acos, pi
from classes import Textures, AbstractBrush, addVMF
from src.PyVMF import *

FIRE_RATE = 0.8 # seconds
GRAVITY_ACCELERATION = -800 # units/second^2
ROCKET_SPEED = 1100 # units/s
JUMP_VELOCITY = 277 # units/s
ROCKET_JUMP_VELOCITY = 960 # units/s
CTAP_VELOCITY = 1040 # units/s
ROCKET_PUSH = 640 # units/s
JUMP_PLUS_CROUCH = 320 # units/s


def ROUND_VALUE_TO_GRID(value, grid_value):
    q, r = divmod(value, grid_value)
    if r > grid_value/2:
        return q*grid_value + 1
    else:
        return q*grid_value
    
def ROUND_POSITION_TO_GRID(position, grid_value):
    return (ROUND_VALUE_TO_GRID(position[0], grid_value), ROUND_VALUE_TO_GRID(position[1], grid_value), ROUND_VALUE_TO_GRID(position[2], grid_value))

def GET_NEXT_HEIGHT(vertical_speed, t=FIRE_RATE):
    return vertical_speed*t + 0.5*GRAVITY_ACCELERATION*t**2

def GET_NEXT_VERTICAL_SPEED(vertical_speed, t=FIRE_RATE):
    return vertical_speed + GRAVITY_ACCELERATION * t

def GET_NEXT_VELOCITY(velocity, strafe_type, ws_type, t=FIRE_RATE):
    v_x, v_y, v_z = velocity
    if strafe_type in {0,1}:
        return (v_x, v_y, GET_NEXT_VERTICAL_SPEED(v_z, t))
    if strafe_type == 2:
        theta = pi/2 if ws_type == 'r' else -pi/2
        new_v_x, new_v_y = cos(theta)*v_x - sin(theta)*v_y, sin(theta)*v_x + cos(theta)*v_y
        return (new_v_x, new_v_y, GET_NEXT_VERTICAL_SPEED(v_z, t))

def GET_SYNC_VELOCITY(amount_of_rockets):
    return ROCKET_PUSH*amount_of_rockets + JUMP_PLUS_CROUCH

def GET_MAX_HEIGHT(vertical_speed):
    t_max = (-vertical_speed)/GRAVITY_ACCELERATION
    return GET_NEXT_HEIGHT(vertical_speed, t=t_max)

def GET_POSITION_IN_DIRECTION( position, direction ):
    if direction in {'x', '-x'}:
        return position[0]
    if direction in {'y', '-y'}:
        return position[1]
    if direction in {'z', '-z'}:
        return position[2]

def GET_NEXT_POSITION(velocity, position, strafe_type, prev_ws_type, t=FIRE_RATE):
    def GET_MOVE( direction, value ):
        moveDict = {
        'x': (value, 0, 0),
        'y': (0, value, 0),
        'z': (0, 0, value),
        '-x': (-value, 0, 0),
        '-y': (0, -value, 0),
        '-z': (0, 0, -value),
        }
        return moveDict[ direction ]
    
    direction = GET_DIRECTION_OF_VELOCITY( velocity )
    v_x, v_y, v_z = velocity
    prev_x, prev_y, prev_z = position
    new_z = GET_NEXT_HEIGHT(v_z, t) + prev_z

    if strafe_type == 0:
        x, y = v_x*t, v_y*t
        return (x + prev_x, y + prev_y, new_z)
    if strafe_type == 1:
        direction_to_new_wallshot = DIRECTION_HANDLER( DIRECTION_HANDLER( direction, prev_ws_type ), 'o') # this is maybe a bit confusing as ws_type is confusing
        switch_correction = GET_MOVE( direction_to_new_wallshot, GET_HOR_SPEED(velocity)*t*(1/2) )
        x, y = v_x*t, v_y*t 
        return (x + prev_x + switch_correction[0], y + prev_y + switch_correction[1], new_z )
    if strafe_type == 2:
        direction_strafe = DIRECTION_HANDLER( DIRECTION_HANDLER( direction, prev_ws_type ), 'o')
        strafe_correction = GET_MOVE( direction_strafe, GET_HOR_SPEED(velocity)*t*(3/4) )
        x, y = v_x*t*(3/4), v_y*t*(3/4)
        return (x + prev_x + strafe_correction[0], y + prev_y + strafe_correction[1], new_z )

def GET_MAGNITUDE(velocity):
    v_x, v_y, v_z = velocity
    return sqrt( v_x**2 + v_y**2 + v_z**2 )

def GET_HOR_SPEED(velocity):
    v_x, v_y, _ = velocity
    return sqrt( v_x**2+v_y**2 )

def GET_VER_SPEED(velocity):
    _, _, v_z = velocity
    return abs(v_z)

def GET_DIRECTION_OF_VELOCITY(velocity):
    v_x, v_y, _ = velocity
    if v_x == 0 and v_y == 0:
        return 'z'
    if abs(v_x) > abs(v_y):
        if v_x > 0:
            return 'x'
        else:
            return '-x'
    else:
        if v_y > 0:
            return 'y'
        else:
            return '-y'

def UPDATE_VELOCITY_AFTER_WALLSHOT(velocity, angle=0):
    # the rotation is between 0 and pi/2 and rotates the ROCKET_PUSH velocity

    ROTATED_ROCKET_PUSH_HOR = sin(angle)*ROCKET_PUSH
    ROTATED_ROCKET_PUSH_Z = cos(angle)*ROCKET_PUSH
    
    v_x, v_y, v_z = velocity
    hor_angle = acos(v_x/(sqrt(v_x**2 + v_y**2)))
    hor_angle = hor_angle if v_y > 0 else -hor_angle
    ROTATED_ROCKET_PUSH_X = cos(hor_angle)*ROTATED_ROCKET_PUSH_HOR
    ROTATED_ROCKET_PUSH_Y = sin(hor_angle)*ROTATED_ROCKET_PUSH_HOR
    return (v_x + ROTATED_ROCKET_PUSH_X, v_y + ROTATED_ROCKET_PUSH_Y, v_z + ROTATED_ROCKET_PUSH_Z)

def UPDATE_WS_TYPE( strafe_type, ws_type ):
    strafe_dict = {
        # stay
        0:  { 
            'l':    'l',
            'r':    'r',
        },
        # switch
        1:  {
            'l':    'r',
            'r':    'l',
        },
        # outward corner
        2:  {
            'l':    'l',
            'r':    'r',
        },
        # inward corner
        3:  {
            'l':    'l',
            'r':    'r',
        },
    }
    return strafe_dict[strafe_type][ws_type]

def DIRECTION_HANDLER( direction, s ):
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
    return direction_dict[direction][s]

def CREATE_WALLSHOT( velocity, position, textures, ws_type ):
    grid_value = 64
    hor_speed = GET_HOR_SPEED( velocity )
    ver_speed = GET_VER_SPEED( velocity )
    print( velocity )
    direction = GET_DIRECTION_OF_VELOCITY( velocity )
    pos = ROUND_POSITION_TO_GRID( position, grid_value )
    
    wallshot_half_length = ROUND_VALUE_TO_GRID( max( hor_speed*0.2, 128), grid_value )
    wallshot_half_height = ROUND_VALUE_TO_GRID( max( ver_speed*1.5, 2*128), grid_value )

    normal = DIRECTION_HANDLER( DIRECTION_HANDLER(direction, ws_type), 'o')
    _, res =divmod(GET_POSITION_IN_DIRECTION(pos, normal), 128)

    materials_dictionary = {
            direction:                              textures.side,
            normal:                                 textures.shoot,
            DIRECTION_HANDLER(direction, 'o'):      textures.side,
            'z':                                    textures.side,
        }
    move_dictionary = {
        direction:                                  wallshot_half_length,
        DIRECTION_HANDLER(direction, 'o'):          wallshot_half_length,
        DIRECTION_HANDLER(direction, ws_type):      128 + res,
        'z':                                        wallshot_half_height,
        '-z':                                       wallshot_half_height,
    }
    proto = AbstractBrush(move_dictionary, materials_dictionary).create( pos, textures )
    return proto

def CREATE_ENDPLATFORM( velocity, position, textures ):
    grid_value = 128
    pos = ROUND_POSITION_TO_GRID( position, grid_value )
    direction = GET_DIRECTION_OF_VELOCITY( velocity )

    materials_dictionary = {
            DIRECTION_HANDLER(direction, 'o'):      textures.side,
            'z':                                    textures.walk,
        }
    move_dictionary = {
        direction:                                  6*128,
        DIRECTION_HANDLER(direction, 'r'):          2*128,
        DIRECTION_HANDLER(direction, 'l'):          2*128,
        '-z':                                       4*128,
    }
    proto = AbstractBrush(move_dictionary, materials_dictionary).create( pos, textures )
    return proto

def CREATE_JUMP( start_velocity, strafes, start_ws_type ):
    
    dummy_vmf = new_vmf()
    textures = Textures()
    textures.load_textures()

    pos = (0, 0, 0)
    v = start_velocity
    ws_type = start_ws_type
    amount_of_wallshots = len(strafes)
    falling_time = 2

    # create the wallshots
    for i in range(amount_of_wallshots):
        pos = GET_NEXT_POSITION( v, pos, strafes[i], ws_type )
        v = GET_NEXT_VELOCITY( v, strafes[i], ws_type )
        ws_type = UPDATE_WS_TYPE( strafes[i], ws_type )
        dummy_vmf = addVMF( dummy_vmf, CREATE_WALLSHOT( v, pos, textures, ws_type ))
        v = UPDATE_VELOCITY_AFTER_WALLSHOT( v, (pi/2)/amount_of_wallshots*i )

    # create the end platform
    pos = GET_NEXT_POSITION( v, pos, 0, ws_type, t=falling_time )
    v = GET_NEXT_VELOCITY( v, 0, ws_type, t=falling_time )
    dummy_vmf = addVMF( dummy_vmf, CREATE_ENDPLATFORM( v, pos, textures ) )


    return dummy_vmf 

