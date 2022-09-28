import json
import os.path as path
from pathlib import Path
import re

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
        print(f'$ Texture: {Fore.GREEN}Loading{Fore.RESET} {source} -> glTexture id {self.id}')
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

class Redirect:
    force = False
    type = ''

    def __init__(self,path,to) -> None:
        self.path = path
        self.to = Path(to).resolve().as_posix()
    
    def set_force(self,type):
        self.force = True
        self.type = type

class Resource:
    location = ''
    redirect = dict()

    def __init__(self, location: str,colors={}) -> None:
        if location.startswith('.'):
            self.location = Path(location).resolve().as_posix()
        else:
            self.location = location
        self.colors = colors

    def _suffix_check(self, type):
        suffix = {
            'models': '.json',
            'textures': '.png'
        }
        return suffix[type]

    def add_redirect(self,path:str,to:str):
        to = to.replace('{origin}',self.location)
        redirect = Redirect(path,to)
        if(self.redirect.get(path) is None):
            self.redirect.update({path:redirect})
        else:
            return f"Found {path} was declared"
        return redirect

    def goto(self, type: str, text: str,suffix:str = ''):
        """
        :parent string
        :path string
        """
        if(suffix == ''):
            suffix = self._suffix_check(type)
        cut = text.split(":")
        if len(cut) > 1 and cut[::-1][0].startswith('minecraft:'):
            cut = cut[::-1]
            cut.pop()
            cut = cut[::-1]
        text = ':'.join(cut)
        text = text.replace('minecraft:', '')
        locate = self.location
        for i in self.redirect.keys():
            if(re.search(i,text) is not None):
                redirect = self.redirect.get(i)
                locate = redirect.to
                if(redirect.force):
                    type = redirect.type
                break
        source = path.join(locate, type, *Path(text+suffix).parts)
        return Path(source).as_posix()

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
        if(not Path(fpath).exists()):
            print(f'{Fore.LIGHTRED_EX}$ Path Failed Texture: {fpath}{Fore.RESET}')
        else:
            print(f'{Fore.LIGHTRED_EX}$ Path Texture: {fpath}{Fore.RESET}')
        return self.loadImage(fpath,size,rgba)

    def loadImage(self, source: str, size: int = 128,rgba:bool = True):
        image = cv2.imread(source, cv2.IMREAD_UNCHANGED)
        h, w, c = image.shape
        origin = np.array([w, h])
        scale = size/origin
        scale.sort()
        dim = (origin * scale[1]).astype(int)
        image = cv2.resize(image, (dim[0], dim[1]),
                           interpolation=cv2.INTER_AREA)
        if(rgba): image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        return image