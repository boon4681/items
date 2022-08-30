import cv2
import numpy as np
import math
from OpenGL.GL import *
from PIL import Image
from PIL import ImageOps
from cv2 import Mat
import glfw

def createContext():
    glfw.init()
    glfw.window_hint(glfw.VISIBLE,glfw.FALSE)
    hWnd = glfw.create_window(64,64,"",None,None)
    glfw.make_context_current(hWnd)


def createBuffer(size: int):
    fbo = glGenFramebuffers(1)
    color_buf = glGenRenderbuffers(1)
    depth_buf = glGenRenderbuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    glBindRenderbuffer(GL_RENDERBUFFER, color_buf)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA8, size, size)
    glFramebufferRenderbuffer(
        GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, color_buf)
    glBindRenderbuffer(GL_RENDERBUFFER, depth_buf)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, size, size)
    glFramebufferRenderbuffer(
        GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_buf)


def readBuffer(size: int):
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    glReadBuffer(GL_COLOR_ATTACHMENT0)
    data = glReadPixels(0, 0, size, size, GL_RGBA, GL_UNSIGNED_BYTE)
    return data

class Scene:
    def __init__(self, size: int, setup):
        self.size = size
        createContext()
        createBuffer(self.size)
        setup(self.size)

    def clear(self):
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def readScene(self) -> Mat:
        data = readBuffer(self.size)
        image = Image.frombytes("RGBA", (self.size, self.size), data)
        image = ImageOps.flip(image)
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)
        return image

    def rotate_by_axis(self,deg,axis):
        v = [0,0,0]
        if('x' in axis): v[0] = 1
        if('y' in axis): v[1] = 1
        if('z' in axis): v[2] = 1
        a,b,c = v
        x,y,z = ((1-np.array(v))*0.5).tolist()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(deg, a, b, c)
        glTranslatef(-x, -y, -z)

    def translate(self,x,y,z):
        glTranslatef(x, y,z)
        
    def popMatrix(self):
        glPopMatrix()