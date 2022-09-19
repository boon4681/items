import json
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import cv2
import click
import requests
from src.item import spawn_egg
from src.source import Source
from src.scene import Scene
from src.block import Block
from src.resource import Resource
from src.logger import Logger
from alive_progress import alive_bar

def gl_setup(size):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glAlphaFunc(GL_GREATER, 0.1)
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


@click.command()
@click.option('--version')
def main(version: str):
    source = Source('./source')
    location = source.make(version)
    source.fetch(version)
    source.extract_resource(version)
    colors = json.loads(requests.get(f'https://raw.githubusercontent.com/boon4681/itemsflower/{version}/all.json').text)
    resource = Resource(location.resource.joinpath('assets', 'minecraft').as_posix(),colors['blocks'])
    size = 256
    scene = Scene(size, gl_setup)
    items = list(location.resource.joinpath('assets', 'minecraft','models','item').glob('*.json'))
    b = 0
    i = 0
    fail = 0
    with alive_bar(len(items), force_tty=True) as bar:
        logger = Logger(bar)
        logger.start()
        for j in range(len(items)):
            item = items[j]
            print(f'Item {j}:')
            print(f'$ name: {item.name.replace(".json","")}')
            scene.clear()
            f = item.open('rb')
            j = json.loads(f.read())
            f.close()
            if('parent' in j):
                parent = str(j['parent'])
                if(parent.startswith('minecraft:block')):
                    block = Block(scene,resource, j["parent"])
                    block.init()
                    block.render(clip=True)
                    block.clearTexture()
                    cv2.imwrite(f'./generate/{item.name.replace(".json","")}.png', scene.readScene())
                    b+=1
                    logger.bar()
                elif(parent.startswith('minecraft:item') and not parent.startswith('minecraft:item/template')):
                    if('textures' in j):
                        # logger.print(f'{item.name} {json.dumps(j)}')
                        texture = resource.loadTexture(j['textures']['layer0'],size,False)
                        cv2.imwrite(f'./generate/{item.name.replace(".json","")}.png', texture)
                        i+=1
                    else:
                        print(f'$ Failed: not found textures {item.name}')
                        print(f'$ {json.dumps(j)}')
                        fail+=1
                    logger.bar()
                elif(parent.startswith('minecraft:item/template')):
                    if(parent.endswith('spawn_egg')):
                        cv2.imwrite(f'./generate/{item.name.replace(".json","")}.png', spawn_egg(resource,colors['spawn_eggs'],item.name.replace(".json","")))
                else:
                    print('$ NOT LOAD',resource.goto('models','item/'+item.name.replace(".json","")))
                    logger.bar()
            else:
                print(f'$ Failed: not found textures {item.name}')
                print(f'$ {json.dumps(j)}')
                fail+=1
                logger.bar()
        print(f'Rendered block_items: {b} block')
        print(f'Rendered items: {i} item')
        print(f'Failed: {fail}')
        print(f'Total: {b+i}/{len(items)} {round((i+b)*100/len(items),2)}')
        logger.stop()

if __name__ == '__main__':
    main()
