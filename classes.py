from src.PyVMF import *
import json
prototypeVMF = load_vmf('vmfs/prototype.vmf')

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
sideTextures = [f"dev/reflectivity_{10*(i+1)}" for i in range(6)]
sideDict = {
    "x": sideTextures[0],
    "y": sideTextures[1],
    "z": sideTextures[2],
    "-x": sideTextures[3],
    "-y": sideTextures[4],
    "-z": sideTextures[5],
}

with open("texture_settings.json", "r") as f:
    tex_dict = json.loads(f.read())
''' connectors textures '''
ceiling_tex = tex_dict['ceiling_tex']
corner_tex = tex_dict['corner_tex']
floor_tex = tex_dict['floor_tex']
search_tex = tex_dict['search_tex']

''' jump textures '''
side_tex = tex_dict['side_tex']
skip_tex = tex_dict['skip_tex']
shoot_tex = tex_dict['shoot_tex']
walk_tex = tex_dict['walk_tex']

nodraw = 'tools/toolsnodraw'
trigger_tex = 'tools/toolstrigger'
black_tex = 'tools/toolsblack'

class VertexManipulationBox:
    def __init__( self, xMin, xMax, yMin, yMax, zMin, zMax ):
        self.xMin, self.xMax, self.yMin, self.yMax, self.zMin, self.zMax = xMin, xMax, yMin, yMax, zMin, zMax

    def getVerticesInBox( self, vmf ):
        allVertices = []
        for solid in vmf.get_solids():
            allVertices.extend(solid.get_all_vertices())
        verticesInBox = []
        for vertex in allVertices:
            if self.xMin < vertex.x < self.xMax and self.yMin < vertex.y < self.yMax and self.zMin < vertex.z < self.zMax:
                verticesInBox.append( vertex )
        return verticesInBox

class BrushVertexManipulationBox:

    def __init__( self, proto ):
        self.proto = proto
        self.boxes = self.createBoxesDict()

    def createBoxesDict( self ):
        verts = {
        'x':    VertexManipulationBox( 0, 512, -512, 512, -512, 512),
        'y':    VertexManipulationBox( -512, 512, 0, 512, -512, 512),
        'z':    VertexManipulationBox( -512, 512, -512, 512, 0, 512),
        '-x':   VertexManipulationBox( -512, 0, -512, 512, -512, 512),
        '-y':   VertexManipulationBox( -512, 512, -512, 0, -512, 512 ),
        '-z':   VertexManipulationBox( -512, 512, -512, 512, -512, 0),
        }
        return verts

    def createVerticesInBoxDict( self ):
        '''Creates a dictionary of lists of vertices that are contained in the given VMB'''
        verticesDict = { key: self.boxes[key].getVerticesInBox( self.proto ) for key in self.boxes }
        return VerticesToManipulate( verticesDict )

class VerticesToManipulate:
    def __init__( self, verticesDict ):
        self.verticesDict = verticesDict

    def getMove( self, direction, value ):
        moveDict = {
        'x': (value, 0, 0),
        'y': (0, value, 0),
        'z': (0, 0, value),
        '-x': (-value, 0, 0),
        '-y': (0, -value, 0),
        '-z': (0, 0, -value),
        }
        return moveDict[ direction ]

    def translate( self, x, y, z ):
        moveDict = {
        'x': (x, 0, 0),
        'y': (0, y, 0),
        'z': (0, 0, z),
        '-x': (x, 0, 0),
        '-y': (0, y, 0),
        '-z': (0, 0, z),
        }

        for direction in self.verticesDict:
            for vertex in self.verticesDict[ direction ]:
                vertex.move( *moveDict[ direction ] )

    def full_move( self, a, b, c, d, e, f ):
        moveDict = {
        'x': (a, 0, 0),
        'y': (0, b, 0),
        'z': (0, 0, c),
        '-x': (d, 0, 0),
        '-y': (0, e, 0),
        '-z': (0, 0, f),
        }

        for direction in self.verticesDict:
            for vertex in self.verticesDict[ direction ]:
                vertex.move( *moveDict[ direction ] )

    def moveToZero( self ):
        for direction in self.verticesDict:
            for vertex in self.verticesDict[ direction ]:
                vertex.move( *self.getMove( direction, -384 ) )

        return self

''' Classes for generate.py '''

class Platform:
    def  __init__( self, type ):
        self.type = type # ss or sk or rs
    def create( self, dir, coord ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.translate( *coord, 0 )
        dir_r, dir_l, dir_opp = direction_dict[ dir ][ 'l' ], direction_dict[ dir ][ 'r' ], direction_dict[ dir ][ 'o' ]
        for vertex in verts.verticesDict[ dir_r ]:
            vertex.move( *verts.getMove( dir_r, 2*128 ))
        for vertex in verts.verticesDict[ dir_l ]:
            vertex.move( *verts.getMove( dir_l, 2*128 ))

        for vertex in verts.verticesDict[ dir ]:
            vertex.move( *verts.getMove( dir, 6*128 ))
        for vertex in verts.verticesDict[ dir_opp ]:
            vertex.move( *verts.getMove( dir_opp, -2*128 ))

        for vertex in verts.verticesDict[ 'z' ]:
            vertex.move( *verts.getMove( 'z', 2*128 ))
        for vertex in verts.verticesDict[ '-z' ]:
            vertex.move( *verts.getMove( '-z', 2*128 ))

        if self.type == 'rs':
            for vertex in verts.verticesDict[ dir ]:
                if vertex in verts.verticesDict[ 'z' ]:
                    vertex.move( *verts.getMove( 'z', 2*128 ))

        c_1, c_2, _ = verts.getMove( dir, 8*128 )
        coord = ( coord[0]+c_1, coord[1]+c_2 )

        solid = proto.get_solids()[0]

        for side in solid.get_sides():
            if side.material == sideDict[ 'z' ].upper():
                if self.type in { 'ss', 'rs' }:
                    side.material = walk_tex.upper()
                else:
                    side.material = skip_tex.upper()
            elif side.material == sideDict[ '-z' ].upper():
                side.material = nodraw.upper()
            else:
                side.material = side_tex.upper()

        return proto, coord

class Wallshot:
    def  __init__( self, l_or_r ):
        self.l_or_r = l_or_r        # left or right

    def create( self, dir, coord ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.translate( *coord, 0 )
        n = direction_dict[ dir ][ self.l_or_r ]
        n_opp = direction_dict[ n ][ 'o' ]
        dir_opp = direction_dict[ dir ][ 'o' ]
        for vertex in verts.verticesDict[ n ]:
            vertex.move( *verts.getMove( n, -128 ))
        for vertex in verts.verticesDict[ n_opp ]:
            vertex.move( *verts.getMove( n_opp, 3*128 ))

        for vertex in verts.verticesDict[ 'z' ]:
            vertex.move( *verts.getMove( 'z', 10*128 ))
        for vertex in verts.verticesDict[ '-z' ]:
            vertex.move( *verts.getMove( '-z', 2*128 ))

        for vertex in verts.verticesDict[ dir ]:
            vertex.move( *verts.getMove( dir, 6*128 ))

        for vertex in verts.verticesDict[ dir_opp ]:
            vertex.move( *verts.getMove( dir_opp, -2*128 ))

        c_1, c_2, _ = verts.getMove( dir, 8*128 )
        coord = ( coord[0]+c_1, coord[1]+c_2 )

        solid = proto.get_solids()[0]
        for side in solid.get_sides():
            if side.material == sideDict[dir].upper() or side.material == sideDict[dir_opp].upper():
                side.material = side_tex.upper()
            elif side.material == sideDict[ n ].upper():
                side.material = shoot_tex.upper()
            else:
                side.material = nodraw.upper()

        return proto, coord

class Jurf:
    def  __init__( self, l_or_r ):
        self.l_or_r = l_or_r        # left or right
    def create( self, dir, coord ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.translate( *coord, 0 )

        proto2 = createDuplicateVMF(prototypeVMF)
        verts2 = BrushVertexManipulationBox( proto2 ).createVerticesInBoxDict().moveToZero()
        verts2.translate( *coord, 0 )

        n = direction_dict[ dir ][ self.l_or_r ]
        n_opp = direction_dict[ n ][ 'o' ]
        dir_opp = direction_dict[ dir ][ 'o' ]

        # here we move the jurf
        for vertex in verts.verticesDict[ n ]:
            vertex.move( *verts.getMove( n, 128 ))
        for vertex in verts.verticesDict[ n_opp ]:
            vertex.move( *verts.getMove( n_opp, 2*128 ))

        for vertex in verts.verticesDict[ 'z' ]:
            vertex.move( *verts.getMove( 'z', 2*128 ))
        for vertex in verts.verticesDict[ '-z' ]:
            vertex.move( *verts.getMove( '-z', 2*128 ))

        for vertex in verts.verticesDict[ dir ]:
            vertex.move( *verts.getMove( dir, 6*128 ))

        for vertex in verts.verticesDict[ dir_opp ]:
            vertex.move( *verts.getMove( dir_opp, -2*128 ))

        for vertex in verts.verticesDict[ n_opp ]:
            if vertex in verts.verticesDict[ 'z' ]:
                vertex.move( *verts.getMove( 'z', 3*128+8 ))

        # here we move the sidewall
        for vertex in verts2.verticesDict[ n ]:
            vertex.move( *verts2.getMove( n, -2*128 ))
        for vertex in verts2.verticesDict[ n_opp ]:
            vertex.move( *verts2.getMove( n_opp, 3*128 ))

        for vertex in verts2.verticesDict[ 'z' ]:
            vertex.move( *verts2.getMove( 'z', 5*128+8 ))
        for vertex in verts2.verticesDict[ '-z' ]:
            vertex.move( *verts2.getMove( '-z', 2*128 ))

        for vertex in verts2.verticesDict[ dir ]:
            vertex.move( *verts2.getMove( dir, 6*128 ))

        for vertex in verts2.verticesDict[ dir_opp ]:
            vertex.move( *verts2.getMove( dir_opp, -2*128 ))

        c_1, c_2, _ = verts.getMove( dir, 8*128 )
        coord = ( coord[0]+c_1, coord[1]+c_2 )

        solid = proto.get_solids()[0]
        for side in solid.get_sides():
            if side.material == sideDict['z'].upper():
                side.material = walk_tex.upper()
            elif side.material in { sideDict[ n_opp ].upper(), sideDict[ '-z' ].upper() }:
                side.material = nodraw.upper()
            else:
                side.material = side_tex.upper()

        solid = proto2.get_solids()[0]
        for side in solid.get_sides():
            if side.material in {sideDict['-z'].upper(), sideDict[ n ].upper() , sideDict[n_opp].upper() } :
                side.material = nodraw.upper()
            else:
                side.material = side_tex.upper()


        proto = addVMF( proto, proto2 )

        return proto, coord

class Start:
    def create( self, cur ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.full_move( 3*128, 0 , 0, -3*128, -4*128, -2*128 )

        solid = proto.get_solids()[0]
        for side in solid.get_sides():
            if side.material == sideDict[ 'z' ].upper():
                side.material = walk_tex.upper()
            elif side.material == sideDict[ 'y' ].upper():
                side.material = side_tex.upper()
            else:
                side.material = nodraw.upper()

        proto2 = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto2 ).createVerticesInBoxDict().moveToZero()
        verts.full_move( 3*128, 0 , 10*128, 128, -4*128, 0 )

        solid = proto2.get_solids()[0]
        for side in solid.get_sides():
            if side.material == sideDict['y'].upper():
                side.material = side_tex.upper()
            elif side.material == sideDict[ '-x' ].upper():
                side.material = shoot_tex.upper()
            else:
                side.material = nodraw.upper()

        proto = addVMF( proto, proto2 )

        # Now we make the info_teleport_destination
        dic = {
            'classname':    'info_teleport_destination',
            'origin':       f'{64} {-2*128} {1}',
            'angles':       '0 90 0',
        	'targetname':   f'jump_{cur+1}',
        }
        dest = Entity(dic=dic)
        proto.add_entities(dest)

        return proto

class End:
    def create( self, dir, coord, next ):
        def create_plat():
            proto = createDuplicateVMF(prototypeVMF)
            verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
            verts.translate( *coord, 0 )
            dir_r, dir_l, dir_opp = direction_dict[ dir ][ 'l' ], direction_dict[ dir ][ 'r' ], direction_dict[ dir ][ 'o' ]
            for vertex in verts.verticesDict[ dir_r ]:
                vertex.move( *verts.getMove( dir_r, 3*128 ))
            for vertex in verts.verticesDict[ dir_l ]:
                vertex.move( *verts.getMove( dir_l, 3*128 ))

            for vertex in verts.verticesDict[ dir ]:
                vertex.move( *verts.getMove( dir, 26*128 ))
            for vertex in verts.verticesDict[ dir_opp ]:
                vertex.move( *verts.getMove( dir_opp, -20*128 ))

            for vertex in verts.verticesDict[ 'z' ]:
                vertex.move( *verts.getMove( 'z', 0))
            for vertex in verts.verticesDict[ '-z' ]:
                vertex.move( *verts.getMove( '-z', 2*128 ))


            solid = proto.get_solids()[0]
            for side in solid.get_sides():
                if side.material == sideDict[ 'z' ].upper():
                    side.material = walk_tex.upper()
                elif side.material == sideDict[ dir_opp ].upper():
                    side.material = side_tex.upper()
                else:
                    side.material = nodraw.upper()
            return proto

        def create_tele_door():
            proto = createDuplicateVMF(prototypeVMF)
            verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
            verts.translate( *coord, 0 )
            dir_r, dir_l, dir_opp = direction_dict[ dir ][ 'l' ], direction_dict[ dir ][ 'r' ], direction_dict[ dir ][ 'o' ]
            for vertex in verts.verticesDict[ dir_r ]:
                vertex.move( *verts.getMove( dir_r, 0.5*128 ))
            for vertex in verts.verticesDict[ dir_l ]:
                vertex.move( *verts.getMove( dir_l, 0.5*128 ))

            for vertex in verts.verticesDict[ dir ]:
                vertex.move( *verts.getMove( dir, 26*128 ))
            for vertex in verts.verticesDict[ dir_opp ]:
                vertex.move( *verts.getMove( dir_opp, -26*128+32 ))

            for vertex in verts.verticesDict[ 'z' ]:
                vertex.move( *verts.getMove( 'z', 1.5*128))
            for vertex in verts.verticesDict[ '-z' ]:
                vertex.move( *verts.getMove( '-z', 0 ))


            solid = proto.get_solids()[0]
            for side in solid.get_sides():
                if side.material in {sideDict[ dir ].upper(), sideDict[ '-z' ].upper()}:
                    side.material = nodraw.upper()
                else:
                    side.material = black_tex.upper()


            return proto

        def create_tele():
            proto = createDuplicateVMF(prototypeVMF)
            verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
            verts.translate( *coord, 0 )
            dir_r, dir_l, dir_opp = direction_dict[ dir ][ 'l' ], direction_dict[ dir ][ 'r' ], direction_dict[ dir ][ 'o' ]
            for vertex in verts.verticesDict[ dir_r ]:
                vertex.move( *verts.getMove( dir_r, 0.5*128 ))
            for vertex in verts.verticesDict[ dir_l ]:
                vertex.move( *verts.getMove( dir_l, 0.5*128 ))

            for vertex in verts.verticesDict[ dir ]:
                vertex.move( *verts.getMove( dir, 26*128 ))
            for vertex in verts.verticesDict[ dir_opp ]:
                vertex.move( *verts.getMove( dir_opp, -26*128+32 ))

            for vertex in verts.verticesDict[ 'z' ]:
                vertex.move( *verts.getMove( 'z', 1.5*128))
            for vertex in verts.verticesDict[ '-z' ]:
                vertex.move( *verts.getMove( '-z', 0 ))
            for vertex in verts.verticesDict[ 'z' ]:
                vertex.move( *verts.getMove( 'z', 8))
            for vertex in verts.verticesDict[ dir_r ]:
                vertex.move( *verts.getMove( dir_r, 8 ))
            for vertex in verts.verticesDict[ dir_l ]:
                vertex.move( *verts.getMove( dir_l, 8 ))
            for vertex in verts.verticesDict[ dir_opp ]:
                vertex.move( *verts.getMove( dir_opp, 8 ))

            solid = proto.get_solids()[0]
            solid.set_texture( trigger_tex )

            tele_dic = {
                'classname':    'trigger_teleport',
                'target':       f'jump_{next+1}'

            }
            tele_ent = Entity(dic=tele_dic)
            tele_ent.solids.append( solid )
            proto = new_vmf()
            proto.add_entities(*[tele_ent])

            return proto

        tot_proto = new_vmf()
        tot_proto = addVMF( tot_proto, create_plat() )
        tot_proto = addVMF( tot_proto, create_tele_door() )
        tot_proto = addVMF( tot_proto, create_tele() )

        return tot_proto

class Connectors:
    def create( self, strafes, directions ):
        coord = ( 0, 0 )
        proto_list = []
        verts_list = []
        for i in range(len( strafes )):

            if i == 0 or strafes[i] != '-':
                dir = directions[i]
                proto = createDuplicateVMF(prototypeVMF)
                verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
                verts.translate( *coord, 0 )
                dir_r, dir_l, dir_opp = direction_dict[ dir ][ 'l' ], direction_dict[ dir ][ 'r' ], direction_dict[ dir ][ 'o' ]
                for vertex in verts.verticesDict[ dir_r ]:
                    vertex.move( *verts.getMove( dir_r, 3*128 ))
                for vertex in verts.verticesDict[ dir_l ]:
                    vertex.move( *verts.getMove( dir_l, 3*128 ))

                for vertex in verts.verticesDict[ dir ]:
                    vertex.move( *verts.getMove( dir, 8*128 ))

                if i == 0:
                    for vertex in verts.verticesDict[ dir_opp ]:
                        vertex.move( *verts.getMove( dir_opp, 4*128 ))

                for vertex in verts.verticesDict[ 'z' ]:
                    vertex.move( *verts.getMove( 'z', 10*128))
                for vertex in verts.verticesDict[ '-z' ]:
                    vertex.move( *verts.getMove( '-z', 2*128 ))

                solid = proto.get_solids()[0]
                for side in solid.get_sides():
                    side.material = search_tex.upper()
                proto_list.append( proto )
                verts_list.append( verts )

                c_1, c_2, _ = verts.getMove( dir, 8*128 )
                coord = ( coord[0]+c_1, coord[1]+c_2 )

            elif strafes[i] == '-':
                verts = verts_list[-1]
                dir = directions[i]
                for vertex in verts.verticesDict[ dir ]:
                    vertex.move( *verts.getMove( dir, 8*128 ))
                c_1, c_2, _ = verts.getMove( dir, 8*128 )
                coord = ( coord[0]+c_1, coord[1]+c_2 )

            if i == len(strafes)-1:
                verts = verts_list[-1]
                dir = directions[i]
                for vertex in verts.verticesDict[ dir ]:
                    vertex.move( *verts.getMove( dir, 26*128 ))

            if i!= 0 and strafes[i] != '-':
                cur_verts, prev_verts = verts_list[-1], verts_list[-2]
                cur_dir, prev_dir = directions[i], directions[i-1]
                cur_dir_opp = direction_dict[ cur_dir ][ 'o' ]

                for vertex in prev_verts.verticesDict[ prev_dir ]:
                    vertex.move( *verts.getMove( prev_dir, 3*128 ))
                for vertex in cur_verts.verticesDict[ cur_dir_opp ]:
                    vertex.move( *verts.getMove( cur_dir_opp, -3*128 ))



        tot_proto = new_vmf()
        for proto in proto_list:
            tot_proto = addVMF( tot_proto, proto )
        return tot_proto

class Triggers:
    def create( self, vmf ):
        solids = vmf.get_solids()
        xMin, xMax, yMin, yMax, zMin, zMax = getMaxDimensionsOfList( solids )

        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.full_move( xMax, yMax, zMax, xMin, yMin, zMin )
        for direction in verts.verticesDict:
            for vertex in verts.verticesDict[ direction ]:
                vertex.move( *verts.getMove( direction, 4*128 ) )

        solid = proto.get_solids()[0]
        solid.set_texture( trigger_tex )

        regen_dic = {
            'classname':    'func_regenerate',
        }
        regen_ent = Entity(dic=regen_dic)
        regen_ent.solids.append( solid )

        hurt_dic = {
            'classname':    'trigger_hurt',
            'damage':       '-9999999'
        }

        hurt_ent = Entity(dic=hurt_dic)
        hurt_ent.solids.append( solid )

        proto = new_vmf()
        proto.add_entities(*[regen_ent, hurt_ent])

        return proto

''' Classes for main.py '''

class Jump:
    def __init__( self, jumps, strafes ):
        self.jumps = jumps
        self.strafes = strafes


def getDimensionsOfSolid( solid: Solid ):
    allVertices = solid.get_all_vertices()
    xMin = min([ vertex.x for vertex in allVertices ])
    yMin = min([ vertex.y for vertex in allVertices ])
    zMin = min([ vertex.z for vertex in allVertices ])
    xMax = max([ vertex.x for vertex in allVertices ])
    yMax = max([ vertex.y for vertex in allVertices ])
    zMax = max([ vertex.z for vertex in allVertices ])
    return xMin, xMax, yMin, yMax, zMin, zMax

def addVMF( vmf: VMF, vmf_to_add: VMF ):
    total_vmf = createDuplicateVMF( vmf )

    #add solids
    solids = vmf_to_add.get_solids( include_solid_entities=False )
    copiedSolids = [ solid.copy() for solid in solids ]
    total_vmf.add_solids(*copiedSolids)

    # add entities
    entities = vmf_to_add.get_entities( include_solid_entities=True )
    copiedEntities = [ entity.copy() for entity in entities ]
    total_vmf.add_entities(*copiedEntities)

    return total_vmf

def createDuplicateVMF(vmf: VMF):
    duplicateVMF = new_vmf()
    solids = vmf.get_solids( include_solid_entities=False )
    copiedSolids = [solid.copy() for solid in solids]
    duplicateVMF.add_solids(*copiedSolids)

    entities = vmf.get_entities( include_solid_entities=True )
    copiedEntities = [ entity.copy() for entity in entities ]
    duplicateVMF.add_entities(*copiedEntities)
    return duplicateVMF

def getMaxDimensionsOfList( solids ):
    xMin_l, xMax_l, yMin_l, yMax_l, zMin_l, zMax_l = set(), set(), set(), set(), set(), set()
    for solid in solids:
        xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )
        xMin_l.add(xMin)
        xMax_l.add(xMax)
        yMin_l.add(yMin)
        yMax_l.add(yMax)
        zMin_l.add(zMin)
        zMax_l.add(zMax)
    xMin, xMax, yMin, yMax, zMin, zMax = min( xMin_l ), max( xMax_l ), min( yMin_l ), max( yMax_l ), min( zMin_l ), max( zMax_l )
    return ( xMin, xMax, yMin, yMax, zMin, zMax )

def moveVMF( vmf: VMF, coord ):
    solids = vmf.get_solids( include_solid_entities=True )
    for solid in solids:
        solid.move( *coord )
    entities = vmf.get_entities( include_solid_entities=False )
    for entity in entities:
        origin = entity.other["origin"]
        entity.other["origin"] = Vertex( origin.x + coord[0], origin.y + coord[1], origin.z + coord[2] )
