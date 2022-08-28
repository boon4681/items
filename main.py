

import json
import math
from time import sleep
from OpenGL.WGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import cv2
import pathlib
from src.scene import Scene
from src.block import Block
from src.resource import Resource
from src.logger import Logger
from alive_progress import alive_bar

def setup(size):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
    glLight(GL_LIGHT0, GL_POSITION,  (1.7, 3.5, 2, 1))

    glShadeModel(GL_FLAT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    scale = 1
    focus = 5
    glOrtho(-1.0 / scale, 1.0 / scale, -1.0 / scale,
            1.0 / scale, -2.0/scale, 1.0/scale*focus)
    dist = math.sqrt(1 / 3.0)
    gluLookAt(dist, dist, dist,
              0.0,  0.0,  0.0,
              0.0,  1.0,  0.0)
    glTranslated(0, 0, 0)
    glMatrixMode(GL_MODELVIEW)
    glViewport(0, 0, size, size)

res = Resource('./resource/1.18.2/assets/minecraft')
scene = Scene(64, setup)
scene.clear()

items = list(pathlib.Path().glob("./resource/1.18.2/assets/minecraft/models/item/*.json"))
i = 0
with alive_bar(len(items), force_tty=True) as bar:
    logger = Logger(bar)
    logger.start()
    for item in items:
        scene.clear()
        f = item.open('rb')
        j = json.loads(f.read())
        f.close()
        if('parent' in j):
            parent = j['parent']
            if(parent.startswith('minecraft:block')):
                block = Block(scene,res, j["parent"])
                block.render()
                cv2.imwrite(f'./generate/{item.name.replace(".json","")}.png', scene.readScene())
                i+=1
                logger.bar()
            elif(parent.startswith('minecraft:item/generated')):
                logger.bar()
            else:
                print(f'url->{item.__str__}')
    logger.stop()
print(f'Rendered block_item {i} block')