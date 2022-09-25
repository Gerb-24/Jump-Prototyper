from src.PyVMF import *
from classes import *
import os
import json

leftDict = {
    'y':    'x',
    'x':    '-y',
    '-y':   '-x',
    '-x':   'y',
}

rightDict = {
    'x':    'y',
    '-y':    'x',
   '-x':    '-y',
    'y':    '-x',
}

class edgeData:
    def __init__(self, normal, pos,  _min, _max, z_min, z_max ):
        self.normal = normal
        self.pos = int(pos)
        self.interval = ( _min, _max )
        self.height_interval = ( z_min, z_max )

    def get_start( self ):
        if self.normal in {'x', '-x'}:
            return ( self.pos, self.interval[0] )
        return ( self.interval[0], self.pos )

    def get_end( self ):
        if self.normal in {'x', '-x'}:
            return ( self.pos, self.interval[1] )
        return ( self.interval[1], self.pos )

    def corner_points_checks( self, corner_points, visited ):
        start, end = self.get_start(), self.get_end()
        if start in corner_points:
            self.interval = (self.interval[0] + 128, self.interval[1])
            visited.add( start )
        if end in corner_points:
            self.interval = (self.interval[0], self.interval[1] - 128)
            visited.add( end )

    def change_interval( self, new_min, new_max ):

        ed = edgeData(
            self.normal,
            self.pos,
            new_min,
            new_max,
            self.height_interval[0],
            self.height_interval[1]
        )
        return ed

    def toWall( self ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()

        verts.full_move( 0, 0, self.height_interval[1], 0, 0, self.height_interval[0] )

        if self.normal == 'x':
            verts.full_move( self.pos, self.interval[1], 0, self.pos - 128, self.interval[0], 0  )

        elif self.normal == 'y':
            verts.full_move( self.interval[1], self.pos, 0, self.interval[0], self.pos - 128, 0  )

        elif self.normal == '-x':
            verts.full_move( self.pos + 128, self.interval[1], 0, self.pos, self.interval[0], 0  )

        elif self.normal == '-y':
            verts.full_move( self.interval[1], self.pos + 128, 0, self.interval[0], self.pos, 0  )

        solid = proto.get_solids()[0]
        for side in solid.get_sides():
            if side.material == sideDict[self.normal].upper():
                side.material = side_tex
            else:
                side.material = nodraw.upper()
        return proto

class cornerPoint:
    def __init__(self, pos, z_min, z_max, n_1, n_2 ):
        self.pos = pos
        self.z_min, self.z_max = z_min, z_max
        if n_1 in {'x', '-x'}:
            self.n_x, self.n_y = n_1, n_2
        else:
            self.n_x, self.n_y = n_2, n_1

    def toCorner( self ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()

        verts.translate( *self.pos, 0 )
        normalsDict = {
        'x':    ( -128, 0, 0, 0, 0, 0 ),
        'y':    ( 0, -128, 0, 0, 0, 0 ),
        '-x':   ( 0, 0, 0, 128, 0, 0 ),
        '-y':   ( 0, 0, 0, 0, 128, 0 ),
        }
        verts.full_move( *normalsDict[self.n_x] )
        verts.full_move( *normalsDict[self.n_y] )
        verts.full_move( 0, 0, self.z_max, 0, 0, self.z_min )

        solid = proto.get_solids()[0]
        for side in solid.get_sides():
            if side.material == sideDict[self.n_x].upper() or side.material == sideDict[self.n_y].upper():
                side.material = nodraw.upper()
            elif side.material == sideDict['z'].upper() or side.material == sideDict['-z'].upper():
                side.material = nodraw.upper()
            else:
                side.material = corner_tex.upper()
        return proto

def solidToCeiling( solid: Solid, tot_z_max ):
    proto = createDuplicateVMF(prototypeVMF)
    verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()

    xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )

    verts.full_move( xMax, yMax, tot_z_max + 128, xMin, yMin, tot_z_max )

    solid = proto.get_solids()[0]
    for side in solid.get_sides():
        if side.material == sideDict['-z'].upper():
            side.material = ceiling_tex.upper()
        else:
            side.material = nodraw.upper()
    return proto

def solidToFloor( solid: Solid, tot_z_min, filename ):
    proto = createDuplicateVMF(prototypeVMF)
    verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()

    xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )

    verts.full_move( xMax, yMax, zMin, xMin, yMin, tot_z_min - 128 )

    solid = proto.get_solids()[0]
    for side in solid.get_sides():
        if side.material == sideDict['z'].upper():
            side.material = floor_tex.upper()
        else:
            side.material = nodraw.upper()

    proto2 = createDuplicateVMF(prototypeVMF)
    verts = BrushVertexManipulationBox( proto2 ).createVerticesInBoxDict().moveToZero()
    verts.full_move( xMax, yMax, zMin+64, xMin, yMin, zMin )

    # proto3 = createDuplicateVMF(prototypeVMF)
    # verts = BrushVertexManipulationBox( proto3 ).createVerticesInBoxDict().moveToZero()
    # verts.full_move( xMax, yMax, zMin+64, xMin, yMin, zMin )

    solid = proto2.get_solids()[0]
    for side in solid.get_sides():
        side.material = trigger_tex.upper()
    target = os.path.splitext(os.path.basename(filename))[0]

    tele_dic = {
        'classname':    'trigger_teleport',
        'target':       f'{target}'

    }
    tele_ent = Entity(dic=tele_dic)
    tele_ent.solids.append( solid )

    # solid = proto3.get_solids()[0]
    # for side in solid.get_sides():
    #     side.material = trigger_tex.upper()
    _solid = solid.copy()
    cata_dic = {
        'classname':    'trigger_catapult',
        'playerSpeed':  '0'
    }
    cata_ent = Entity(dic=cata_dic)
    cata_ent.solids.append( _solid )
    proto.add_entities(*[tele_ent, cata_ent])

    return proto

def getDimensionsOfSolid( solid: Solid ):
    allVertices = solid.get_all_vertices()
    xMin = min([ vertex.x for vertex in allVertices ])
    yMin = min([ vertex.y for vertex in allVertices ])
    zMin = min([ vertex.z for vertex in allVertices ])
    xMax = max([ vertex.x for vertex in allVertices ])
    yMax = max([ vertex.y for vertex in allVertices ])
    zMax = max([ vertex.z for vertex in allVertices ])
    return xMin, xMax, yMin, yMax, zMin, zMax

def removeSolids(vmf: VMF, solidsToRemove):
    vmf.world.solids = [ solid for solid in vmf.world.solids if solid not in solidsToRemove ]
    return vmf

def getEdgeDataOfSolid( solid: Solid ):
    xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )
    solid_ed_dict = {
        'x':    edgeData( 'x', xMin, yMin, yMax, zMin, zMax ),
        '-x':   edgeData( '-x', xMax, yMin, yMax, zMin, zMax ),
        'y':    edgeData( 'y', yMin, xMin, xMax, zMin, zMax ),
        '-y':   edgeData( '-y', yMax, xMin, xMax, zMin, zMax ),
    }

    solid_data = [ solid_ed_dict[key] for key in solid_ed_dict ]
    return solid_data

def generate_connectors( filename ):
    dummyVMF = new_vmf()
    testVMF = createDuplicateVMF(load_vmf(filename))
    solids = [solid for solid in testVMF.get_solids() if solid.has_texture(search_tex)]
    dim_tuple = getMaxDimensionsOfList(solids)
    edgeDataList = []

    tot_z_min, tot_z_max = None, None
    for solid in solids:
        _, _, _, _, zMin, zMax = getDimensionsOfSolid( solid )
        if tot_z_min != None:
            tot_z_min = min( zMin, tot_z_min )
        else:
            tot_z_min = zMin
        if tot_z_max != None:
            tot_z_max = max( zMax, tot_z_max )
        else:
            tot_z_max = zMax


    for solid in solids:
        dummyVMF = addVMF(dummyVMF, solidToCeiling( solid, tot_z_max ) )
        dummyVMF = addVMF(dummyVMF, solidToFloor( solid, tot_z_min, filename ) )
        edgeDataList.extend(getEdgeDataOfSolid(solid))
    ed_x_dict = {}
    ed_y_dict = {}
    for ed in edgeDataList:
        if ed.normal == 'x' or ed.normal == '-x':
            if ed.pos not in ed_x_dict:
                ed_x_dict[ ed.pos ] = [ ed ]
            else:
                ed_x_dict[ ed.pos ].append( ed )
        else:
            if ed.pos not in ed_y_dict:
                ed_y_dict[ ed.pos ] = [ ed ]
            else:
                ed_y_dict[ ed.pos ].append( ed )

    def change_ed_dict( ed_dict, x_or_y ):
        corner_points = []
        def add_corner_point( pos, val, bot, top, n_1, n_2 ):
            if x_or_y == 'x':
                corner_points.append( cornerPoint( (pos, val), bot, top, n_1, n_2 ) )
            else:
                corner_points.append( cornerPoint( (val, pos), bot, top, n_1, n_2 ) )


        for key in ed_dict:
            if len( ed_dict[key] ) > 1:

                intervals = ed_dict[key]
                intervals.sort( key= lambda ed: ed.interval[0] )
                new_intervals = []
                i = 0
                while i < len( intervals ) - 1:
                    cur, next = intervals[i].interval, intervals[i + 1].interval # the current interval and the interval next in line
                    cur_n, next_n = intervals[i].normal, intervals[i+1].normal
                    cur_h, next_h = intervals[i].height_interval, intervals[i+1].height_interval
                    bot, top = min( cur_h[0], next_h[0] ), max( cur_h[1], next_h[1] )
                    end_condition = True

                    if cur[1] < next[1]:
                        if cur[1] < next[0]:        # Disjoint
                            new_intervals.append( intervals[i] )

                        elif cur[1] == next[0]:     # Touching
                            new_intervals.append( intervals[i] )

                        elif cur[0] < next[0]:      # Partial Overlap
                            new_intervals.append( intervals[i].change_interval( cur[0], next[0]))
                            intervals[i+1] = intervals[i+1].change_interval( cur[1], next[1])
                            if cur_n in { 'y', '-x' }:
                                n_1, n_2 = cur_n, leftDict[cur_n]
                                n_3, n_4 = next_n, leftDict[next_n]
                            else:
                                n_1, n_2 = cur_n, rightDict[cur_n]
                                n_3, n_4 = next_n, rightDict[next_n]
                            add_corner_point( key, next[0], bot, top, n_1, n_2 )
                            add_corner_point( key, cur[1], bot, top, n_3, n_4 )

                        elif cur[0] == next[0]:     # Start overlap on cur
                            intervals[i+1] = intervals[i+1].change_interval( cur[1], next[1])
                            if cur_n in { 'y', '-x' }:
                                n_1, n_2 = next_n, leftDict[next_n]
                            else:
                                n_1, n_2 = next_n, rightDict[next_n]
                            add_corner_point( key, cur[1], bot, top, n_1, n_2 )


                    elif cur[1] == next[1]:
                        if cur[0] < next[0]:        # Total overlap on next
                            new_intervals.append( intervals[i].change_interval( cur[0], next[0] ))
                            if cur_n in { 'y', '-x' }:
                                n_1, n_2 = cur_n, leftDict[cur_n]
                            else:
                                n_1, n_2 = cur_n, rightDict[cur_n]
                            add_corner_point( key, next[0], bot, top, n_1, n_2 )
                            i += 1

                        elif cur[0] == next[0]:     # Total overlap on both
                            i += 2
                            continue

                    elif cur[1] > next[1]:
                        if cur[0] < next[0]:        # Mid overlap
                            new_intervals.append( intervals[i].change_interval( cur[0], next[0]))
                            intervals[i+1] = intervals[i].change_interval(next[1], cur[1])
                            if cur_n in { 'y', '-x' }:
                                n_1, n_2 = cur_n, leftDict[cur_n]
                                n_3, n_4 = cur_n, rightDict[cur_n]
                            else:
                                n_1, n_2 = cur_n, rightDict[cur_n]
                                n_3, n_4 = cur_n, leftDict[cur_n]
                            add_corner_point( key, next[0], bot, top, n_1, n_2 )
                            add_corner_point( key, next[1], bot, top, n_3, n_4 )

                        elif cur[0] == next[0]:     # Start overlap
                            intervals[i+1] = intervals[i].change_interval( next[1], cur[1] )
                            if cur_n in { 'y', '-x' }:
                                n_1, n_2 = cur_n, rightDict[cur_n]
                            else:
                                n_1, n_2 = cur_n, leftDict[cur_n]
                            add_corner_point( key, next[1], bot, top, n_1, n_2 )

                    # here we add the last segement as there is no next
                    if end_condition and i == len( intervals ) - 2:
                        new_intervals.append( intervals[i+1] )
                    i += 1
                ed_dict[key] = new_intervals
        return corner_points

    corner_points_x = change_ed_dict( ed_x_dict, 'x' )
    corner_points_y = change_ed_dict( ed_y_dict, 'y' )

    corner_points = corner_points_x.copy()
    corner_points.extend( corner_points_y )

    edgeDataList = []
    for key in ed_x_dict:
        edgeDataList.extend(ed_x_dict[key])
    for key in ed_y_dict:
        edgeDataList.extend(ed_y_dict[key])

    cp_positions = { cp.pos for cp in corner_points }
    visited = set()
    for ed in edgeDataList:
        ed.corner_points_checks( cp_positions, visited )
        dummyVMF = addVMF(dummyVMF, ed.toWall() )

    for cp in corner_points:
        if cp.pos in visited:
            dummyVMF = addVMF(dummyVMF, cp.toCorner() )

    testVMF = removeSolids( testVMF, solids )
    testVMF = addVMF( testVMF, dummyVMF )
    return testVMF, dim_tuple

def combine( ):
    with open("settings.json", "r") as f:
        load_data = json.loads(f.read())
    vmf_list, mapname = load_data['vmf_list'], load_data['mapname']
    tot_vmf = new_vmf()
    c_list = [ 0 ]
    for i, vmf_file in enumerate(vmf_list):
        vmf, dim_tuple = generate_connectors( vmf_file )
        a, a_max, b, b_max, c, c_max = dim_tuple
        moveVMF( vmf, (-a, -b, -c -80*128) )
        moveVMF( vmf, ( 0, 0, c_list[-1] ) )
        a_max, b_max, c_max = a_max - a, b_max - b, c_max - c
        tot_vmf = addVMF( tot_vmf, vmf )
        c_list.append( c_max + c_list[ -1 ] + 8*128 )
    filename = os.path.join( os.path.dirname(vmf_list[0]), f'{mapname}.vmf' )
    tot_vmf.export(filename)
