import json
import math
import requests
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import cv2
from src.scene import Scene
from src.block import Block
from src.resource import Resource


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
    scale = 1.225
    focus = 5
    glOrtho(-1.0 / scale, 1.0 / scale, -1.0 / scale,
            1.0 / scale, -2.0/scale, 1.0/scale*focus)
    gluLookAt(1, 6**0.5/3, 1,
              0.0,  0.0,  0.0,
              0.0,  1.0,  0.0)
    glTranslated(0, -(6**0.58/3)*0.1, 0)
    glMatrixMode(GL_MODELVIEW)
    glViewport(0, 0, size, size)

colors = json.loads(requests.get(f'https://raw.githubusercontent.com/boon4681/itemsflower/1.19.2/blocks.json').text)
res = Resource('./resource/1.18.2/assets/minecraft',colors)
scene = Scene(128, setup)
scene.clear()
renderTest = ['command_block', 'composter', 'furnace',
              'stonecutter', 'big_dripleaf', 'andesite_stairs', 'scaffolding_stable','purple_glazed_terracotta','acacia_trapdoor_bottom','acacia_fence_inventory','acacia_fence_gate','cactus']
# renderTest = ['composter','stonecutter']
# renderTest = ['andesite_stairs','andesite_wall_inventory','beacon']
renderTest = ['andesite_stairs','andesite_wall_inventory','black_stained_glass','acacia_leaves']
for test in renderTest:
    scene.clear()
    block = Block(scene,res, f'block/{test}')
    block.init()
    block.render(clip=True)
    cv2.imwrite(f'./test/{test}.png', scene.readScene())