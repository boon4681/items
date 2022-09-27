from src.color import mix, to_rgb
from src.resource import Resource
import cv2

def spawn_egg(res:Resource,colors,name,size=128):
    model = res.readModel('item/template_spawn_egg')

    im = res.loadTexture(model['textures']['layer0'],size=size,rgba=True)
    im2 = res.loadTexture(model['textures']['layer1'],size=size,rgba=True)

    im = mix(im,to_rgb(colors[name]['primary_color']))
    im2 = mix(im2,to_rgb(colors[name]['secondary_color']))

    for i in range(3):
        im[:,:,i] = im[:,:,i]*(im[:,:,3]/255)
        im2[:,:,i] = im2[:,:,i]*(im2[:,:,3]/255)
    im = im + im2
    return cv2.cvtColor(im,cv2.COLOR_RGBA2BGRA)