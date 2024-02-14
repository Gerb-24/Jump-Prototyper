from random_gen import CREATE_JUMP

# START VELOCITIES
CTAP_START = ( 0, 600, 925 )
WS_START_1 = ( 0, 800, 700 )

# CODE
start_velocity = CTAP_START
strafes = [0, 1, 2, 0, 1 ] # here the first entry is a dummy value
start_ws_type = 'r'

vmf = CREATE_JUMP(start_velocity, strafes, start_ws_type)
vmf.export( 'vmfs/random/test1.vmf' )
