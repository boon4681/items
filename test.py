import math
from OpenGL.WGL import *
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
renderTest = ['command_block', 'composter', 'furnace',
              'stonecutter', 'big_dripleaf', 'andesite_stairs', 'scaffolding_stable','purple_glazed_terracotta','acacia_trapdoor_bottom','cactus']
# renderTest = ['composter','stonecutter']
# renderTest = ['andesite_stairs']
for test in renderTest:
    scene.clear()
    block = Block(scene,res, f'block/{test}')
    block.render()
    cv2.imwrite(f'./test/{test}.png', scene.readScene())