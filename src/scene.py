import cv2
from cv2 import Mat
import numpy as np
import win32api
import win32con
import win32gui
import math

from OpenGL.WGL import *
from OpenGL.GL import *
from PIL import Image
from PIL import ImageOps
import cv2

PFD_TYPE_RGBA = 0
PFD_MAIN_PLANE = 0
PFD_DOUBLEBUFFER = 0x00000001
PFD_DRAW_TO_WINDOW = 0x00000004
PFD_SUPPORT_OPENGL = 0x00000020


def createContext(hWnd):
    pfd = PIXELFORMATDESCRIPTOR()
    pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL
    pfd.iPixelType = PFD_TYPE_RGBA
    pfd.cColorBits = 32
    pfd.cDepthBits = 24
    pfd.iLayerType = PFD_MAIN_PLANE
    hdc = win32gui.GetDC(hWnd)
    pixelformat = ChoosePixelFormat(hdc, pfd)
    SetPixelFormat(hdc, pixelformat, pfd)
    oglrc = wglCreateContext(hdc)
    wglMakeCurrent(hdc, oglrc)


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


def createFakeWindow():
    hInstance = win32api.GetModuleHandle(None)
    wndClass = win32gui.WNDCLASS()
    wndClass.lpfnWndProc = win32gui.DefWindowProc
    wndClass.hInstance = hInstance
    wndClass.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
    wndClass.hCursor = win32api.LoadCursor(0, win32con.IDC_ARROW)
    wndClass.lpszClassName = str("HELL THE F*CK")
    wndClass.style = win32con.CS_OWNDC

    wndClassAtom = win32gui.RegisterClass(wndClass)

    return win32gui.CreateWindow(wndClassAtom, '', win32con.WS_POPUP, 0, 0, 1, 1, 0, 0, hInstance, None)


class Scene:
    def __init__(self, size: int, setup):
        self.size = size
        Wnd = createFakeWindow()
        createContext(Wnd)
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

    def rotate(self,deg):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(0.5, 0, 0.5)
        glRotatef(deg, 0, 1, 0)
        glTranslatef(-0.5, 0, -0.5)

    def popRotate(self):
        glPopMatrix()