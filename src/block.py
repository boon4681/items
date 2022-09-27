import json
from OpenGL.GL import *
import numpy as np
from colorama import Fore
from colorama import Style
from src.scene import Scene
from src.resource import Resource, Texture


def uvMapper(raw_uv, face, texture: Texture, _del: bool = False):
    # if(face in ["south",'west'] and _del):
    #     x0,x1,y0,y1 = raw_uv
    #     raw_uv = [x0, 16 - y1, x1, 16 - y0]
    d = np.array(raw_uv)
    uv = np.array([(d[0], d[1]), (d[2], d[1]),
                  (d[2], d[3]), (d[0], d[3])]).astype(float)
    uv /= 16
    uv *= 128
    uv /= (texture.width, texture.height)
    if(face == "up"):
        uv = np.roll(uv, 6)
    elif(face == "south"):
        uv = np.roll(uv, 4)
    elif(face != "down"):
        uv = np.roll(uv, 4)
    # print('uvMap', uv.tolist())
    return uv


def cullMapper(raw_uv, face, texture: Texture):
    d = np.array(raw_uv)
    uv = np.array([(d[0], d[1]), (d[2], d[1]),
                  (d[2], d[3]), (d[0], d[3])]).astype(float)
    uv /= 16
    uv *= 128
    uv /= (texture.width, texture.height)
    if(face == "up"):
        uv = np.roll(uv, 2)
    # print('cullMap', uv.tolist())
    return uv


def uvRotate(uv, degree):
    rotateMap = {0: 0, 90: 1, 180: 2, 270: 3}
    return np.roll(uv, rotateMap[degree]*2)


class Cube:
    def __init__(self, cube, faces, textures):
        _from_ = cube['from']
        _to_ = cube['to']
        x0, y0, z0 = _from_
        x1, y1, z1 = _to_
        vertex = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                  (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        vertex = np.roll(vertex, 24)
        self.v = (np.array(vertex) / 16).tolist()
        self._from_ = _from_
        self._to_ = _to_
        if(abs(x1-x0) == 0):
            if('west' in faces):
                del faces['west']
        if(abs(y1-y0) == 0):
            if('down' in faces):
                del faces['down']
        if(abs(z1-z0) == 0):
            if('south' in faces):
                del faces['south']
        self.faces = faces
        self.textures = textures
        self.scene_rotation = 135
        self.cube = cube
        self.edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5),
                      (5, 4), (7, 6), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
        self.nv = [(0, 0, -1), (0, 0, 1), (-1, 0, 0),
                   (1, 0, 0), (0, -1, 0), (0, 1, 0)]
        self.uv = [(0, 1), (1, 1), (1, 0), (0, 0)]
        self.surfaces = [(0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7),
                         (1, 5, 6, 2), (4, 5, 1, 0), (2, 6, 7, 3)]

    def rotate(self, rotation):
        self.scene_rotation = abs(self.scene_rotation - rotation)

    def rotate_scene(self):
        rot = self.cube['rotation']
        x, y, z = (np.array(rot['origin']) / 16).tolist()
        axis = rot['axis']
        if(axis == 'x'):
            a, b, c = [1, 0, 0]
        if(axis == 'y'):
            a, b, c = [0, 1, 0]
        if(axis == 'z'):
            a, b, c = [0, 0, 1]

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(rot["angle"], a, b, c)
        glTranslatef(-x, -y, -z)

    def render(self, depth_test: bool = False, clip: bool = True):
        if('rotation' in self.cube):
            self.rotate_scene()
        mapping = ['north', 'south', 'west', 'east', 'down', 'up']
        clipping = ['south', 'west', 'down']
        if(self.scene_rotation == 90):
            clipping = ['west', 'down', 'north']
        if(self.scene_rotation == 270):
            clipping = ['east', 'down', 'south']
        if(not clip):
            clipping = []
        if(depth_test):
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LEQUAL)
        else:
            glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        x0, y0, z0 = self._from_
        x1, y1, z1 = self._to_
        for i, quad in enumerate(self.surfaces):
            glNormal3fv(self.nv[i])
            uv = self.uv
            if(mapping[i] not in clipping):
                if(mapping[i] in self.faces):
                    face = self.faces[mapping[i]]
                    texture = self.textures[face['texture']]
                    texture.bind()
                    f = mapping[i]
                    if('uv' in face and 'cullface' in face):
                        if(f in ['up', 'down']):
                            uv = cullMapper(
                                np.roll(face['uv'], 0), mapping[i], texture)
                        else:
                            uv = cullMapper(
                                np.roll(face['uv'], 2), mapping[i], texture)
                    elif('uv' in face):
                        uv = uvMapper(face['uv'], mapping[i], texture)
                    else:
                        uv = uvMapper([0, 0, 16, 16], mapping[i], texture)
                        if(f == 'north'):
                            uv = cullMapper(
                                [16 - x1, y1, 16 - x0, y0], mapping[i], texture)
                        if(f == 'south'):
                            uv = cullMapper(
                                [16 - x0, y1, 16 - x1, y0], mapping[i], texture)
                        if(f == 'east'):
                            uv = cullMapper(
                                [16 - z1, y1, 16 - z0, y0], mapping[i], texture)
                        if(f == 'west'):
                            uv = cullMapper(
                                [16 - z0, y1, 16 - z1, y0], mapping[i], texture)
                        if(f == 'up'):
                            uv = cullMapper([x1, z1, x0, z0],
                                            mapping[i], texture)
                        if(f == 'down'):
                            uv = uvMapper([x1, z1, x0, z0],
                                          mapping[i], texture)
                        # print(f, "cullface", uv)
                    if('rotation' in face):
                        uv = uvRotate(uv, face['rotation'])
                    glBegin(GL_QUADS)
                    for ti, iv in enumerate(quad):
                        glTexCoord2fv(uv[ti])
                        glVertex3fv(self.v[iv])
                    glEnd()
        glDisable(GL_POLYGON_OFFSET_FILL)
        if('rotation' in self.cube):
            glPopMatrix()


class Block:
    def __init__(self, scene: Scene, resource: Resource, source: str):
        self.cubes = []
        self.textures = {}
        self.source = source
        self.loaded_source = source
        self.resource = resource
        self.scene = scene
        self.rotation = []
        try:
            self.load()
        except Error as e:
            print(f'$ {Fore.RED}Block Failed to load: {self.source}{Fore.RESET}')
            print(e)
            raise

    def load(self):
        source = self.source
        loadedModel = False
        while not loadedModel:
            # print(f'{Fore.RED}Entered -> {Fore.LIGHTYELLOW_EX}{source}{Fore.RESET}')
            self.loaded_source = source
            model = self.resource.readModel(source)
            js = json.dumps(model, indent=4).split('\n')
            # # print('\n'.join(list(map(lambda i, x: Fore.CYAN + ''.join(np.zeros(len(str(len(js)))-len(str(i))).astype(int).astype(str).tolist())+f'{i}{Fore.RESET}:{x}', range(1, len(js)+1), js))))
            if('parent' in model):
                if('block/block' == model['parent']):
                    # print(f' Parent{Fore.BLUE}${model["parent"]}{Fore.RESET}')
                    save = source
                    if('textures' in model):
                        for i in model['textures']:
                            source = model['textures'][i]
                            if(source.startswith('#')):
                                self.textures.update(
                                    {'#'+i: self.textures[source]})
                            else:
                                self.textures.update(
                                    {'#'+i: self.resource.glLoadTexture(source)})
                    if('elements' in model):
                        for cube in model['elements']:
                            self.cubes.append(
                                Cube(cube, cube['faces'], self.textures))
                        loadedModel = True
                    source = save
                    break
            if('parent' in model):
                # print(f' Parent{Fore.BLUE}${model["parent"]}{Fore.RESET}')
                if('textures' in model):
                    for i in model['textures']:
                        source = model['textures'][i]
                        if(source.startswith('#')):
                            self.textures.update(
                                {'#'+i: self.textures[source]})
                        else:
                            self.textures.update(
                                {'#'+i: self.resource.glLoadTexture(source)})
                if('elements' in model):
                    for cube in model['elements']:
                        self.cubes.append(
                            Cube(cube, cube['faces'], self.textures))
                    loadedModel = True
                source = model['parent']
            else:
                # print(f' Parent{Fore.BLUE}${None}{Fore.RESET}')
                if('textures' in model):
                    for i in model['textures']:
                        source = model['textures'][i]
                        if(source.startswith('#')):
                            self.textures.update({'#'+i: source})
                        else:
                            self.textures.update(
                                {'#'+i: self.resource.glLoadTexture(source)})
                if('elements' in model):
                    for cube in model['elements']:
                        self.cubes.append(
                            Cube(cube, cube['faces'], self.textures))
                    loadedModel = True
                # print(self.cubes,self.textures)
                break
        model = self.resource.readModel(self.loaded_source)
        self.irotation = 135
        if('display' in model):
            if('gui' in model['display']):
                self.irotation = model['display']['gui']['rotation'][1]*3
        print(f'$ {Fore.RED}Loaded: -> {Fore.LIGHTYELLOW_EX}{self.source}{Fore.RESET}')

    def init(self):
        self.scene.rotate_by_axis(135, 'y')
        self.scene.rotate_by_axis(self.irotation, 'y')

    def render(self, clip: bool = False):
        try:
            for i, cube in enumerate(self.cubes):
                cube.rotate(self.irotation)
                cube.render(True, clip=clip)
        except:
            print(f'$ {Fore.RED}Block Failed to render: {self.source}{Fore.RESET}')
            raise
        self.scene.popMatrix()
        self.scene.popMatrix()

    def clearTexture(self):
        for name in self.textures:
            self.textures[name].delete()
