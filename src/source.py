import json
import math
import re
import requests
from alive_progress import alive_bar
from pathlib import Path
import os
import zipfile
import subprocess

class VersionPath:
    def __init__(self,version,location:Path):
        location = location.joinpath(version)
        self.location = location
        self.clientJAR = location.joinpath(f'{version}.jar')
        self.resource = location.joinpath('resource')
        self.note = location.joinpath('note.txt')
    def make(self):
        self.location.mkdir(parents=True, exist_ok=True)
        self.resource.mkdir(parents=True, exist_ok=True)

class Source:
    def __init__(self,location:str) -> None:
        if location.startswith('.'):
            self.location = Path(location).resolve()
        else:
            self.location = Path(location)
        self.location.mkdir(parents=True, exist_ok=True)
        version_manifest = 'https://launchermeta.mojang.com/mc/game/version_manifest_v2.json'
        data = json.loads(requests.get(version_manifest).text)
        versions = data['versions']
        versions.sort(reverse=True, key=lambda v: v['releaseTime'])

        self.version_ids = [i['id'] for i in versions]
        with open('mcnotsupport', 'r') as f: self.notsupport = list(map(lambda x: x.replace('\n',''),f.readlines()))
        def version(v):
            versions[v]['support'] = self.version_ids[v] not in self.notsupport
            return versions[v]
        self.versions = {self.version_ids[v]: version(v) for v in range(len(self.version_ids))}

    def is_support(self,version):
        return self.versions[version]['support']

    def make(self,version):
        v = VersionPath(version,self.location)
        v.make()
        return v

    def fetch(self,version:str, chunk_size=2048):
        location = self.make(version)
        if(location.clientJAR.exists()): return
        if(version not in self.version_ids):
            return "ERROR VERSION NOT FOUND"
        if(version in self.notsupport):
            return "ERROR NOT SUPPORT VERSION"
        if(location.clientJAR.exists()):
            print(f"Found cached of client.jar from Minecraft-{version}")
            return
        print(f"Fetching Meta from Minecraft-{version}")
        data = json.loads(requests.get(self.versions[version]['url']).text)
        clientOBJ = data['downloads']['client']
        with open(location.clientJAR, 'wb') as f:
            r = requests.get(clientOBJ['url'], stream=True)
            length = int(r.headers.get('content-length'))
            r.raise_for_status()
            with alive_bar(math.ceil(length/chunk_size), title=f"Downloading client.jar", bar="filling") as bar:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    bar()
                    if chunk:
                        f.write(chunk)
                        f.flush()

    def extract_resource(self,version):
        location = self.make(version)
        extracted = False
        if(location.note.exists()):
            with open(location.note,'r') as f: extracted = f.read().find('extracted') != -1
        if(extracted): return
        with zipfile.ZipFile(location.clientJAR,'r') as jar:
            for file in jar.namelist():
                if(file.startswith('assets/minecraft/models/') or file.startswith('assets/minecraft/textures/')):
                    jar.extract(file, location.resource)
        with open(location.note,'a') as f: f.write('extracted')