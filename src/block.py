import json
from OpenGL.GL import *
import numpy as np
from colorama import Fore
from colorama import Style
from src.scene import Scene
from src.resource import Resource, Texture

def uvMapper(raw_uv, face, texture: Texture):
    d = np.array(raw_uv)
    uv = np.array([(d[0], d[1]), (d[2], d[1]),
                  (d[2], d[3]), (d[0], d[3])]).astype(float)
    uv /= 16
    uv *= 128
    uv /= (texture.width, texture.height)
    if(face == "up" or face == "down"):
        uv = np.roll(uv, 6)
    else:
        uv = np.roll(uv, 4)
    print('uvMap', uv.tolist())
    return uv


def cullMapper(raw_uv, face, texture: Texture):
    d = np.array(raw_uv)
    uv = np.array([(d[0], d[1]), (d[2], d[1]),
                  (d[2], d[3]), (d[0], d[3])]).astype(float)
    uv /= 16
    uv *= 128
    uv /= (texture.width, texture.height)
    if(face == "up" or face == "down"):
        uv = np.roll(uv, 2)
    print('cullMap', uv.tolist())
    return uv


def uvRotate(uv, degree):
    rotateMap = {0: 0, 90: 1, 180: 2, 270: 3}
    return np.roll(uv, rotateMap[degree]*2)


class Cube:
    def __init__(self, _from_, _to_, faces, textures):
        x0, y0, z0 = _from_
        x1, y1, z1 = _to_
        vertex = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                  (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        vertex = np.roll(vertex, 24)
        self.v = (np.array(vertex) / 16).tolist()
        self._from_ = _from_
        self._to_ = _to_
        self.faces = faces
        self.textures = textures
        self.rotation = 270
        self.edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5),
                      (5, 4), (7, 6), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
        self.nv = [(0, 0, -1), (0, 0, 1), (-1, 0, 0),
                   (1, 0, 0), (0, -1, 0), (0, 1, 0)]
        self.uv = [(0, 1), (1, 1), (1, 0), (0, 0)]
        self.surfaces = [(0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7),
                         (1, 5, 6, 2), (4, 5, 1, 0), (2, 6, 7, 3)]

    def rotate(self,rotation):
        self.rotation = abs(self.rotation - rotation)
    def render(self,depth_test:bool = False):
        mapping = ['north', 'south', 'west', 'east', 'down', 'up']
        clipping = ['south','west','down']
        if(self.rotation == 270):
            clipping = ['south','west','down']
        if(self.rotation == 90):
            clipping = ['north','east','down']
        if(depth_test):
            glEnable(GL_DEPTH_TEST)
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
                    if('uv' in face and 'cullface' in face):
                        uv = cullMapper(
                            np.roll(face['uv'],2), mapping[i], texture)
                    elif('uv' in face):
                        uv = uvMapper(face['uv'], mapping[i], texture)
                    else:
                        uv = uvMapper([0, 0, 16, 16], mapping[i], texture)
                        f = mapping[i]
                        if(f == 'north'):
                            uv = cullMapper(
                                [16 - x1, y1, 16 - x0, y0], mapping[i], texture)
                        if(f == 'south'):
                            uv = cullMapper(
                                [x0, 16 - y1, x1, 16 - y0], mapping[i], texture)
                        if(f == 'east'):
                            uv = cullMapper(
                                [16 - z1, y1, 16 - z0, y0], mapping[i], texture)
                        if(f == 'west'):
                            uv = cullMapper(
                                [z0, 16 - y1, z1, 16 - y0], mapping[i], texture)
                        if(f == 'up'):
                            uv = cullMapper(
                                [x1, z1, x0, z0], mapping[i], texture)
                        if(f == 'down'):
                            uv = uvMapper([x1, z1, x0, z0], mapping[i], texture)
                        print(f, "cullface", uv)
                    if('rotation' in face):
                        uv = uvRotate(uv, face['rotation'])
                    glBegin(GL_QUADS)
                    for ti, iv in enumerate(quad):
                        glTexCoord2fv(uv[ti])
                        glVertex3fv(self.v[iv])
                    glEnd()
        glDisable(GL_POLYGON_OFFSET_FILL)


class Block:
    def __init__(self,scene: Scene, resource: Resource, source: str):
        self.cubes = []
        self.textures = {}
        self.source = source
        self.loaded_source = source
        self.resource = resource
        self.scene = scene
        try:
            self.load()
        except:
            print(f' ${Fore.RED}Block Failed to loading {source}{Fore.RESET}')
            raise

    def load(self):
        source = self.source
        loadedModel = False
        while not loadedModel:
            print(f'{Fore.RED}Entered -> {Fore.LIGHTYELLOW_EX}{source}{Fore.RESET}')
            model = self.resource.readModel(source)
            js = json.dumps(model, indent=4).split('\n')
            # print('\n'.join(list(map(lambda i, x: Fore.CYAN + ''.join(np.zeros(len(str(len(js)))-len(str(i))).astype(int).astype(str).tolist())+f'{i}{Fore.RESET}:{x}', range(1, len(js)+1), js))))
            if('parent' in model):
                if('block/block' == model['parent']):
                    print(f' Parent{Fore.BLUE}${model["parent"]}{Fore.RESET}')
                    save = source
                    if('textures' in model):
                        for i in model['textures']:
                            source = model['textures'][i]
                            if(source.startswith('#')):
                                self.textures.update(
                                    {'#'+i: self.textures[source]})
                            else:
                                self.textures.update(
                                    {'#'+i: self.resource.loadTexture(source)})
                    if('elements' in model):
                        for cude in model['elements']:
                            _from_ = cude['from']
                            _to_ = cude['to']
                            _face_ = cude['faces']
                            print(_face_)
                            self.cubes.append(
                                Cube(_from_, _to_, _face_, self.textures))
                        loadedModel = True
                    source = save
                    break
            if('parent' in model):
                print(f' Parent{Fore.BLUE}${model["parent"]}{Fore.RESET}')
                if('textures' in model):
                    for i in model['textures']:
                        source = model['textures'][i]
                        if(source.startswith('#')):
                            self.textures.update(
                                {'#'+i: self.textures[source]})
                        else:
                            self.textures.update(
                                {'#'+i: self.resource.loadTexture(source)})
                if('elements' in model):
                    for cude in model['elements']:
                        _from_ = cude['from']
                        _to_ = cude['to']
                        _face_ = cude['faces']
                        print(_face_)
                        self.cubes.append(
                            Cube(_from_, _to_, _face_, self.textures))
                    loadedModel = True
                source = model['parent']
            else:
                print(f' Parent{Fore.BLUE}${None}{Fore.RESET}')
                if('textures' in model):
                    for i in model['textures']:
                        source = model['textures'][i]
                        if(source.startswith('#')):
                            self.textures.update({'#'+i: source})
                        else:
                            self.textures.update(
                                {'#'+i: self.resource.loadTexture(source)})
                if('elements' in model):
                    for cude in model['elements']:
                        _from_ = cude['from']
                        _to_ = cude['to']
                        _face_ = cude['faces']
                        print(_face_)
                        self.cubes.append(
                            Cube(_from_, _to_, _face_, self.textures))
                    loadedModel = True
                print(
                    self.cubes,
                    self.textures
                )
                break
        self.loaded_source = source

    def render(self):
        model = self.resource.readModel(self.loaded_source)
        rotation = 270
        if('display' in model):
            if('gui' in model['display']):
                rotation = model['display']['gui']['rotation'][1] * 2 - 180
        print(f"scene rotation {rotation}")
        self.scene.rotate(rotation)
        try:
            # I don't know how to fix depth_test so i do this
            for i, cube in enumerate(self.cubes):
                cube.rotate(rotation)
                cube.render()
            for i, cube in enumerate(self.cubes[::-1]):
                cube.rotate(rotation)
                cube.render(True)
        except:
            print(
                f' ${Fore.RED}Block Failed to rendering {self.source}{Fore.RESET}')
            raise
        self.scene.popRotate()
        print(f'{Fore.RED}Ended -> {Fore.LIGHTYELLOW_EX}{self.source}{Fore.RESET}')

    def clearTexture(self):
        for name in self.textures:
            self.textures[name].delete()
