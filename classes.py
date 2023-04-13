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

class Textures:
    def __init__( self ):
        '''side textures'''
        self.x = 'dev/reflectivity_10'.upper()
        self.y = 'dev/reflectivity_20'.upper()
        self.z = 'dev/reflectivity_30'.upper()
        self.neg_x = 'dev/reflectivity_40'.upper()
        self.neg_y = 'dev/reflectivity_50'.upper()
        self.neg_z = 'dev/reflectivity_60'.upper()

        '''default textures'''
        self.nodraw = 'tools/toolsnodraw'.upper()
        self.trigger = 'tools/toolstrigger'.upper()
        self.black = 'tools/toolsblack'.upper()

        ''' jump textures '''
        self.side = ''  # used for nonaded surfaces
        self.skip = ''  # used for surfaces with a tele
        self.shoot = '' # used for wallshots
        self.walk = ''  # used for places you can land on

        ''' connectors textures '''
        self.ceiling = ''   # the texture for the ceiling
        self.corner = ''    # the texture for a corner
        self.floor = ''     # the texture for a teled floor
        self.search = ''    # the texture to search for when building connectors

    def load_textures( self ):
        with open("texture_settings.json", "r") as f:
            tex_dict = json.loads(f.read())

        self.side = tex_dict['side'].upper()
        self.skip = tex_dict['skip'].upper()
        self.shoot = tex_dict['shoot'].upper()
        self.walk = tex_dict['walk'].upper()

        self.ceiling = tex_dict['ceiling'].upper()
        self.corner = tex_dict['corner'].upper()
        self.floor = tex_dict['floor'].upper()
        self.search = tex_dict['search'].upper()

        return self

    def to_side( self, s ):
        side_dict = {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "-x": self.neg_x,
            "-y": self.neg_y,
            "-z": self.neg_z,
        }

        return side_dict[ s ]

    def to_sides( self, *args ):
        return { self.to_side(s) for s in args }

    def to_key( self, side ):
        key_dict = {
            self.x:         'x',
            self.y:         'y',
            self.z:         'z',
            self.neg_x:     '-x',
            self.neg_y:     '-y',
            self.neg_z:     '-z',
        }
        return key_dict[ side ]

    def mat_to_dic( self, proto, mat_dic ):
        solid = proto.get_solids()[0]
        pre_mat_dic = {
            "x":    self.nodraw,
            "y":    self.nodraw,
            "z":    self.nodraw,
            "-x":   self.nodraw,
            "-y":   self.nodraw,
            "-z":   self.nodraw,
        }
        for key in mat_dic:
            pre_mat_dic[key] = mat_dic[key]
        for side in solid.get_sides():
            side.material = pre_mat_dic[ self.to_key( side.material ) ]

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

    def move_to_dic( self, move_dic ):
        for key in move_dic:
            for vertex in self.verticesDict[ key ]:
                vertex.move( *self.getMove( key, move_dic[ key ] ))

    def moveToZero( self ):
        for direction in self.verticesDict:
            for vertex in self.verticesDict[ direction ]:
                vertex.move( *self.getMove( direction, -384 ) )

        return self

''' Classes for generate.py '''

class AbstractBrush:
    def __init__( self, move_dic, mat_dic ):
        self.move_dic = move_dic
        self.mat_dic = mat_dic

    def create( self, coord, textures, combined = None ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.translate( *coord )
        verts.move_to_dic( self.move_dic )
        textures.mat_to_dic( proto, self.mat_dic )

        if combined:
            for vertex in verts.verticesDict[ combined['keys'][ 0 ] ]:
                if vertex in verts.verticesDict[ combined['keys'][ 1 ] ]:
                    vertex.move( *verts.getMove( 'z', combined['val'] ))

        return proto

class AbstractSpacer:
    def __init__( self, l, int_dic, h ):
        self.l = l
        self.int_dic = int_dic
        self.h = h

    def update_coord( self, dir, coord ):
        move_list = []
        for key in self.int_dic:
            move_list.append( getMove( key, self.int_dic[ key ] ) )
        move_list.append( coord )
        start = (
            sum( [ e[0] for e in move_list ] ),
            sum( [ e[1] for e in move_list ] ),
            sum( [ e[2] for e in move_list ] ) + self.h,
        )

        # then we update the coord to the end position
        b_1, b_2, b_3 = getMove( dir, self.l )
        end = (start[0] + b_1, start[1] + b_2, start[2] + b_3)
        return self.l, start, end


class Platform:
    def  __init__( self, type ):
        self.type = type # ss or sk or rs or d
        self.start = None
        self.dir = None
        self.length = 4*128

    def update_coord( self, dir, coord ):
        self.dir = dir

        # first we get the starting position
        a_1, a_2, a_3 = getMove( dir, 4*128 )
        self.coord = ( coord[0] + a_1, coord[1] + a_2, coord[2] + a_3 )

        # then we update the coord to the end position
        b_1, b_2, b_3 = getMove( dir, self.length )
        new_coord = (self.coord[0] + b_1, self.coord[1] + b_2, self.coord[2] + b_3)
        return new_coord

    def create( self, textures ):

        # get the directions
        coord, dir = self.coord, self.dir
        dir_r = direction_dict[ dir ][ 'l' ]
        dir_l = direction_dict[ dir ][ 'r' ]
        dir_opp = direction_dict[ dir ][ 'o' ]

        move_dic = {
            dir_r:      2*128,
            dir_l:      2*128,
            dir:        4*128,
            dir_opp:    0,
            'z':        2*128,
            '-z':       2*128
        }

        combined = {        # we always want to go in the z direction for now
            'keys': ( dir, 'z' ),
            'val': 2*128
        } if self.type == 'rs' else None

        mat_dic = {
            dir_r:      textures.side,
            dir_l:      textures.side,
            dir:        textures.side,
            dir_opp:    textures.side
        }

        if self.type in { 'ss', 'rs' }:
            mat_dic[ 'z' ] = textures.walk
        else:
            mat_dic[ 'z' ] = textures.skip

        proto = AbstractBrush( move_dic, mat_dic ).create( coord, textures, combined )

        # c_1, c_2, _ = getMove( dir, 8*128 )
        # coord = ( coord[0]+c_1, coord[1]+c_2 )

        return proto

class Wallshot:
    def  __init__( self, l_or_r, initial=None ):
        self.l_or_r = l_or_r        # left or right
        self.dir = None
        self.coord = None
        self.length = 4*128
        self.height = 10*128
        self.initial = initial


    def update_coord( self, cur_dir, prev_dir, prev_l_or_r, strafe, coord, spacing_type ):
        self.dir = cur_dir

        if self.initial:
            spacing_type = self.initial

        if spacing_type == '4':
            self.height = 6*128
            l, h = 2*128, 4*128
            if self.initial:
                int_dic = {
                    cur_dir:    1*128
                }
                spacing = AbstractSpacer( l, int_dic, 0*128 )
            else:
                if prev_l_or_r == self.l_or_r:
                    if strafe == '-':
                        int_dic = {
                            cur_dir:    2*128
                        }
                    elif strafe == prev_l_or_r:
                        int_dic = {
                            cur_dir:    2*128,
                            prev_dir:   2*128,
                        }
                    elif strafe != prev_l_or_r:
                        int_dic = {
                            cur_dir:    1*128,
                            prev_dir:   1*128,
                        }
                elif prev_l_or_r != self.l_or_r:
                    if strafe == '-':
                        int_dic = {
                            cur_dir:    2*128
                        }
                    elif strafe == prev_l_or_r:
                        int_dic = {
                            cur_dir:    1*128,
                            prev_dir:   1*128,
                        }
                    elif strafe != prev_l_or_r:
                        int_dic = {
                            cur_dir:    1*128,
                            prev_dir:   1*128,
                        }

                spacing = AbstractSpacer( l, int_dic, h )

        elif spacing_type == '2':
            self.height = 4*128
            l, h = 3*128, 2*128
            if self.initial:
                int_dic = {
                    cur_dir:    2*128
                }
                spacing = AbstractSpacer( l, int_dic, 0*128 )
            else:
                if prev_l_or_r == self.l_or_r:
                    if strafe == '-':
                        int_dic = {
                            cur_dir:    3*128
                        }
                    elif strafe == prev_l_or_r:
                        int_dic = {
                            cur_dir:    3*128,
                            prev_dir:   3*128,
                        }
                    elif strafe != prev_l_or_r:
                        int_dic = {
                            cur_dir:    2*128,
                            prev_dir:   2*128,
                        }
                elif prev_l_or_r != self.l_or_r:
                    if strafe == '-':
                        int_dic = {
                            cur_dir:    3*128
                        }
                    elif strafe == prev_l_or_r:
                        int_dic = {
                            cur_dir:    2*128,
                            prev_dir:   2*128,
                        }
                    elif strafe != prev_l_or_r:
                        int_dic = {
                            cur_dir:    2*128,
                            prev_dir:   2*128,
                        }

                spacing = AbstractSpacer( l, int_dic, h )
        else:
            print(f'Something went wrong with the spacing_type lol')
        self.length, self.coord, coord = spacing.update_coord( cur_dir, coord )

        return coord, spacing_type

    def create( self, textures ):
        dir = self.dir
        coord = self.coord
        length = self.length
        # get the directions
        n_opp = direction_dict[ dir ][ self.l_or_r ]
        n = direction_dict[ n_opp ][ 'o' ]
        dir_opp = direction_dict[ dir ][ 'o' ]

        move_dic = {
            n: -1*128,
            n_opp: 2*128,
            dir: length,
            dir_opp: 0,
            'z': self.height,
            '-z': 0*128
        }

        mat_dic = {
            n:          textures.shoot,
            dir:        textures.side,
            dir_opp:    textures.side,
            'z':        textures.side,
        }

        proto = AbstractBrush( move_dic, mat_dic ).create( coord, textures )

        return proto

class Jurf:
    def  __init__( self, l_or_r ):
        self.l_or_r = l_or_r        # left or right
        self.dir = None
        self.coord = None
        self.length = 4*128

    def update_coord( self, dir, coord ):
        self.dir = dir

        # first we get the starting position
        a_1, a_2, a_3 = getMove( dir, 4*128 )
        self.coord = ( coord[0] + a_1, coord[1] + a_2, coord[2] + a_3 )

        # then we update the coord to the end position
        b_1, b_2, b_3 = getMove( dir, self.length )
        new_coord = (self.coord[0] + b_1, self.coord[1] + b_2, self.coord[2] + b_3)
        return new_coord

    def create( self, textures ):
        dir = self.dir
        coord = self.coord
        # get the directions
        n_opp = direction_dict[ dir ][ self.l_or_r ]
        n = direction_dict[ n_opp ][ 'o' ]
        dir_opp = direction_dict[ dir ][ 'o' ]

        move_dic = {
            n: 128,
            n_opp: 2*128,
            dir: 4*128,
            dir_opp: 0,
            'z': 2*128,
            '-z': 2*128
        }

        move_dic2 = {
            n: -2*128,
            n_opp: 3*128,
            dir: 4*128,
            dir_opp: 0,
            'z': 5*128+8,
            '-z': 2*128
        }

        combined = {
            'keys': ( n_opp, 'z' ),
            'val': 3*128+8
        }

        mat_dic = {
            'z':        textures.walk,
            dir:        textures.side,
            dir_opp:    textures.side,
            n:          textures.side,
        }

        mat_dic2 = {
            'z':        textures.skip,
            dir:        textures.side,
            dir_opp:    textures.side,
        }

        proto = AbstractBrush( move_dic, mat_dic ).create( coord, textures, combined )
        proto2 = AbstractBrush( move_dic2, mat_dic2 ).create( coord, textures )


        proto = addVMF( proto, proto2 )

        c_1, c_2, _ = getMove( dir, 8*128 )
        coord = ( coord[0]+c_1, coord[1]+c_2 )

        return proto

class Start:
    def create( self, cur, textures ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.full_move( 3*128, 0 , 0, -3*128, -4*128, -2*128 )

        mat_dic = {
            'z':    textures.walk,
            'y':    textures.side,
        }
        textures.mat_to_dic( proto, mat_dic )

        proto2 = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto2 ).createVerticesInBoxDict().moveToZero()
        verts.full_move( 3*128, 0 , 10*128, 128, -4*128, 0 )

        mat_dic2 = {
            '-x':    textures.shoot,
            'y':    textures.side,
        }
        textures.mat_to_dic( proto2, mat_dic2 )

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
    def create( self, dir, coord, next, textures ):
        def create_plat( ):

            dir_r = direction_dict[ dir ][ 'r' ]
            dir_l = direction_dict[ dir ][ 'l' ]
            dir_opp = direction_dict[ dir ][ 'o' ]
            move_dic = {
                dir_r:      3*128,
                dir_l:      3*128,
                dir:        26*128,
                dir_opp:    -20*128,
                'z':        0,
                '-z':       2*128,
            }

            mat_dic = {
                'z':        textures.walk,
                dir_opp:    textures.side
            }

            proto = AbstractBrush( move_dic, mat_dic ).create( coord, textures )

            return proto

        def create_tele_door():

            dir_r = direction_dict[ dir ][ 'r' ]
            dir_l = direction_dict[ dir ][ 'l' ]
            dir_opp = direction_dict[ dir ][ 'o' ]
            move_dic = {
                dir_r:     0.5*128,
                dir_l:      0.5*128,
                dir:        26*128,
                dir_opp:    -26*128+32,
                'z':        1.5*128,
                '-z':       0,
            }

            mat_dic = {
                'z':        textures.black,
                dir_opp:    textures.black,
                dir_l:      textures.black,
                dir_r:      textures.black
            }

            proto = AbstractBrush( move_dic, mat_dic ).create( coord, textures )

            return proto

        def create_tele():
            proto = createDuplicateVMF(prototypeVMF)
            verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
            verts.translate( *coord )
            dir_r, dir_l, dir_opp = direction_dict[ dir ][ 'l' ], direction_dict[ dir ][ 'r' ], direction_dict[ dir ][ 'o' ]
            move_dic = {
                dir_r:     0.5*128+8,
                dir_l:      0.5*128+8,
                dir:        26*128,
                dir_opp:    -26*128+32+8,
                'z':        1.5*128+8,
                '-z':       0,
            }
            verts.move_to_dic( move_dic )

            solid = proto.get_solids()[0]
            solid.set_texture( textures.trigger )

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
        tot_proto = addVMF( tot_proto, create_plat( ) )
        tot_proto = addVMF( tot_proto, create_tele_door() )
        tot_proto = addVMF( tot_proto, create_tele() )

        return tot_proto

class Triggers:
    def create( self, solids, textures ):
        dim_tuple = getMaxDimensionsOfList(solids)
        xMin, xMax, yMin, yMax, zMin, zMax = dim_tuple
        o_xMin, o_xMax, o_yMin, o_yMax, o_zMin, o_zMax = getDimensionsOfSolid( solids[0] )
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.full_move( xMax, yMax, zMax, xMin, yMin, zMin )
        for direction in verts.verticesDict:
            for vertex in verts.verticesDict[ direction ]:
                vertex.move( *verts.getMove( direction, 4*128 ) )

        solid = proto.get_solids()[0]
        solid.set_texture( textures.trigger )

        regen_dic = {
            'classname':    'func_regenerate',
        }
        regen_ent = Entity(dic=regen_dic)
        regen_ent.solids.append( solid )

        hurt_dic = {
            'origin':       f'{ (o_xMax + o_xMin)//2 } { (o_yMax + o_yMin)//2 } {(o_zMax + o_zMin)//2}',
            'classname':    'trigger_hurt',
            'damage':       '-9999999'
        }

        hurt_ent = Entity(dic=hurt_dic)
        hurt_ent.solids.append( solid )

        proto = new_vmf()
        proto.add_entities(*[regen_ent, hurt_ent])

        return proto, dim_tuple

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
    entities = vmf.get_entities( include_solid_entities=True )
    for entity in entities:
        if "origin" in entity.other:
            print( entity.classname )
            origin = entity.other["origin"]
            entity.other["origin"] = Vertex( origin.x + coord[0], origin.y + coord[1], origin.z + coord[2] )

def getMove( direction, value ):
    moveDict = {
    'x': (value, 0, 0),
    'y': (0, value, 0),
    'z': (0, 0, value),
    '-x': (-value, 0, 0),
    '-y': (0, -value, 0),
    '-z': (0, 0, -value),
    }
    return moveDict[ direction ]
