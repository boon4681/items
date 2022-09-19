import json
import os.path as path
from pathlib import Path

from OpenGL.GL import *
from colorama import Fore, Style
import cv2
from PIL import Image
from cv2 import Mat
import numpy as np

from src.color import mix, to_rgb

class Texture:
    def __init__(self,source:str, image:Mat) -> None:
        h, w, c = image.shape
        self.id = glGenTextures(1)
        self.name = source
        self.image = image
        self.width = w
        self.height = h
        print(f'$- {Fore.GREEN}Loading{Fore.RESET} {source} -> glTexture id {self.id}')
        datas = Image.fromarray(image)
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, datas.size[0], datas.size[1],
                     0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.id)

    def delete(self):
        glDeleteTextures(self.id,[self.id])


class Resource:
    location = ''

    def __init__(self, location: str,colors={}) -> None:
        if location.startswith('.'):
            self.location = Path(location).resolve()
        else:
            self.location = location
        self.colors = colors

    def _suffix_check(self, type):
        suffix = {
            'models': '.json',
            'textures': '.png'
        }
        return suffix[type]

    def goto(self, type: str, text: str):
        """
        :parent string
        :path string
        """
        suffix = self._suffix_check(type)
        cut = text.split(":")
        if len(cut) > 1 and cut[::-1][0].startswith('minecraft:'):
            cut = cut[::-1]
            cut.pop()
            cut = cut[::-1]
        text = ':'.join(cut)
        text = text.replace('minecraft:', '')
        source = path.join(self.location, type, *Path(text+suffix).parts)
        return source

    def readModel(self, name: str):
        fpath = self.goto('models', name)
        fs = open(fpath, 'rb')
        data = fs.read()
        fs.close()
        return json.loads(data)

    def glLoadTexture(self, source: str, size: int = 128,rgba:bool = True):
        name = source.split('/')[-1]
        image = self.loadTexture(source,size,rgba)
        if(name in self.colors):
            image = mix(image,to_rgb(self.colors[name]))
        return Texture(source,image)
        
    def loadTexture(self, source: str, size: int = 128,rgba:bool = True):
        fpath = self.goto('textures', source)
        print(f'{Fore.LIGHTRED_EX}$ Loaded Texture: {fpath}{Fore.RESET}')
        image = cv2.imread(fpath, cv2.IMREAD_UNCHANGED)
        h, w, c = image.shape
        origin = np.array([w, h])
        scale = size/origin
        scale.sort()
        dim = (origin * scale[1]).astype(int)
        image = cv2.resize(image, (dim[0], dim[1]),
                           interpolation=cv2.INTER_AREA)
        if(rgba): image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        return image