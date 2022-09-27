import json
from pathlib import Path
import re
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
import numpy as np
import yaml

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
@click.option('--size','-s',default=[256],multiple=True)
def main(version: str,size):
    source = Source('./source')
    location = source.make(version)
    source.fetch(version)
    source.extract_resource(version)
    colors = json.loads(requests.get(f'https://raw.githubusercontent.com/boon4681/itemsflower/{version}/all.json').text)
    # colors = json.loads(requests.get(f'http://localhost:8000/flower/colors/{version}/all.json').text)
    resource = Resource(location.resource.joinpath('assets', 'minecraft').as_posix(),colors['blocks'])
    banlist = [r'_\d+']
    items = [i for i in list(location.resource.joinpath('assets', 'minecraft','models','item').glob('*.json')) if all(re.search(j,i.name) is None for j in banlist)]
    origin = Path('./generate').resolve()
    for _size_ in size:
        path = origin.joinpath('items',f'x{_size_}')
        atlas = origin.joinpath('atlas',f'x{_size_}')
        path.mkdir(parents=True, exist_ok=True)
        atlas.mkdir(parents=True, exist_ok=True)
        scene = Scene(_size_, gl_setup)
        block_count = 0
        item_count = 0
        fail = 0
        images = []
        items_error_png = resource.loadImage('./items.error.png',_size_,False)
        with alive_bar(len(items), force_tty=True) as bar:
            logger = Logger(bar,origin.joinpath(f'x{_size_}.log.yaml'))
            logger.start()
            for j in range(len(items)):
                item = items[j]
                print(f'Item {j}:')
                print(f'$ name: {item.name.replace(".json","")}')
                scene.clear()
                f = item.open('rb')
                j = json.loads(f.read())
                f.close()
                item_name = item.name.replace(".json","")
                file_name = path.joinpath(f'{item_name}.png').as_posix()
                # write error image if the process error
                image = items_error_png
                error = False
                if('parent' in j):
                    parent = str(j['parent'])
                    if(parent.startswith('minecraft:block') or parent.startswith('block')):
                        block = Block(scene,resource, j["parent"])
                        block.init()
                        block.render(clip=True)
                        block.clearTexture()
                        image = scene.readScene()
                        block_count+=1
                    elif(
                            (parent.startswith('minecraft:item') or parent.startswith('item'))
                            and not 
                            (
                                parent.startswith('minecraft:item/template') or 
                                parent.startswith('item/template') or
                                parent.startswith('item/chest')
                            )
                        ):
                        if('textures' in j):
                            # logger.print(f'{item.name} {json.dumps(j)}')
                            layer0 = j['textures']['layer0']
                            isMCMETA = Path(resource.goto('textures',layer0,'.png.mcmeta')).exists()
                            _image_ = resource.loadTexture(layer0,_size_,False)
                            if(isMCMETA):
                                image = _image_[0:_size_, 0:_size_]
                            else:
                                image = _image_
                            item_count+=1
                        else:
                            print(f'$ Failed: not found textures {item.name}')
                            print(f'$ {json.dumps(j)}')
                            fail+=1
                    elif(parent.startswith('minecraft:item/template') or parent.startswith('item/template')):
                        if(parent.endswith('spawn_egg')):
                            image = spawn_egg(resource,colors['spawn_eggs'],item_name,_size_)
                            item_count+=1
                        else:
                            print('$ ERROR: NOT LOAD item/template',resource.goto('models','item/'+item_name))
                            error = True
                    else:
                        print('$ ERROR: NOT LOAD',resource.goto('models','item/'+item_name))
                        error = True
                else:
                    print(f'$ Failed: not found textures {item.name}')
                    print(f'$ {json.dumps(j)}')
                    fail+=1
                logger.bar()
                cv2.imwrite(file_name, image)
                images.append({'name':item_name,'image':image,'status': -1 if error else 0})
            print(f'Info:')
            print(f'$ All Items: {len(items)}')
            print(f'$ Rendered: {block_count+item_count}')
            print(f'$ Block items: {block_count}')
            print(f'$ Items: {item_count}')
            print(f'$ Failed: {fail}')
            print(f'$ Complete rate: {round((item_count+block_count)*100/len(items),2)}')
            logger.stop()
        def map_image(t,size):
            image = np.zeros((16, size, size, 4))
            for o in range(len(t)): image[o] = t[o]
            return image
        def stack_meta(chunk,_y,size):
            x = np.arange(0,len(chunk)) * size
            w = x + size
            y = np.ones(len(chunk),dtype=int) * _y * size
            h = y + size
            dim = np.column_stack((x,y,w,h))
            return {
                f'{chunk[i]["name"]}':{
                    'image': dim[i].tolist(),
                    'status': chunk[i]["status"]
                }
                for i in range(len(chunk))
            }
        im = lambda x: x['image']
        chunk = np.array_split(images,np.arange(16,len(images),16))
        pre_meta_stack = [stack_meta(chunk[t],t,_size_) for t in range(len(chunk))]
        meta_stack = {}
        for item_count in pre_meta_stack: meta_stack.update(item_count)
        with open(atlas.joinpath('mapping.yaml'),'w') as f: f.write(yaml.dump(meta_stack,default_flow_style=None))
        with open(atlas.joinpath('mapping.json'),'w') as f: f.write(json.dumps(meta_stack,indent=4))
        with open(atlas.joinpath('mapping.min.json'),'w') as f: f.write(json.dumps(meta_stack))
        stack = [np.concatenate(map_image([im(i) for i in t],_size_),axis=1) for t in chunk]
        cv2.imwrite(atlas.joinpath(f'x{_size_}.png').as_posix(), np.concatenate(stack,axis=0))
if __name__ == '__main__':
    main()