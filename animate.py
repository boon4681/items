import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import cv2
from src.source import Source
from src.scene import Scene
from src.block import Block
from src.resource import Resource


def setup(size):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glAlphaFunc (GL_GREATER, 0.1)
    glEnable(GL_ALPHA_TEST)
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
    scale = 0.8
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


res = Resource('./source/1.19.2/resource/assets/minecraft')
res.add_redirect(r'^custom','./custom/test')
# res.add_redirect(r'^entity','{origin}')
scene = Scene(320, setup)
scene.clear()

deg = 0
deg2 = 0
block = Block(scene, res, f'custom/algaela')
# block = Block(scene, res, f'block/big_dripleaf')
import time
while True:
    start_time = time.time()
    scene.clear()
    block.init()
    scene.rotate_by_axis(deg2,'xz')
    scene.rotate_by_axis(deg,'y')
    scene.translate(0,math.sin(math.radians(deg))*0.5,0)
    block.render(clip=False)
    scene.popMatrix()
    scene.popMatrix()
    deg = (deg+6)%360
    deg2 = (deg2+12)%360
    cv2.imshow('HI', scene.readScene())
    print("FPS: ", 1.0 / (time.time() - start_time))
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
