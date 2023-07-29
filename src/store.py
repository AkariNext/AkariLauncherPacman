import hashlib
import json
import os
import shutil
from typing import TypedDict

from src.const import STORE_PATHS
from src.utils.common import load_or_create_json


class IFile(TypedDict):
    original_name: str
    hash: str
    to: str


IFileStoreType = dict[str, IFile]

class FileStore:
    def __init__(self) -> None:
        self.files: IFileStoreType = load_or_create_json(f'{STORE_PATHS["files"]}/files.json', {})  # type: ignore
    
    async def add_file(self, name: str, path: str, to: str, *, dry_run: bool = False):
        file_hash = hashlib.sha256(open(path, 'rb').read()).hexdigest()

        if os.path.exists(f'{STORE_PATHS["files"]}/{file_hash}') or dry_run:
            return file_hash
        self.files[file_hash] = {
            'original_name': name,
            'hash': file_hash,
            'to': to,
        }
        shutil.move(path, f'{STORE_PATHS["files"]}/{name}')
        os.rename(f'{STORE_PATHS["files"]}/{name}', f'{STORE_PATHS["files"]}/{file_hash}')
        await self.save_file()
        return file_hash
    
    async def get_file(self, key: str):
        return self.files[key]

    async def delete_file(self, key: str):
        self.files.pop(key)
        os.remove(f'{STORE_PATHS["files"]}/{key}')
        await self.save_file()

    async def save_file(self):
        with open(f'{STORE_PATHS["files"]}/files.json', 'w', encoding='utf-8') as f:
            json.dump(self.files, f, ensure_ascii=False, indent=4)

class ModStore:
    def __init__(self) -> None:
        self.mods: IFileStoreType = load_or_create_json(f'{STORE_PATHS["mods"]}/mods.json', {})  # type: ignore
        self.resources: IFileStoreType = load_or_create_json(f'{STORE_PATHS["resources"]}/resources.json', {})  # type: ignore

    async def check_already_exist(self, name: str) -> bool:
        if name in self.mods:
            return True
        else:
            return False

    async def get_mod(self, key: str):
        return self.mods[key]
    
    async def get_resource(self, key: str):
        return self.resources[key]
    
    async def delete_mod(self, key: str):
        self.mods.pop(key)
        await self.save_mod()
        os.remove(f'{STORE_PATHS["mods"]}/{key}')
    
    async def delete_resource(self, key: str):
        self.resources.pop(key)
        await self.save_resource()
        os.remove(f'{STORE_PATHS["resources"]}/{key}')

    async def check_hash(self, path: str):
        hashlib.sha256()

    async def get_original_file_name(self, name: str, version: str):
        return f'{name}-{version}'

    async def add(self, name: str, version: str, path: str, to: str):
        original_file_name = await self.get_original_file_name(name, version)
        self.mods[original_file_name] = {
            'original_name': name,
            'hash': hashlib.sha256(open(path, 'rb').read()).hexdigest(),
            'to': to,
        }
        if os.path.exists(f'{STORE_PATHS["mods"]}/{original_file_name}'):
            return original_file_name
        shutil.move(path, f'{STORE_PATHS["mods"]}/{name}')
        os.rename(f'{STORE_PATHS["mods"]}/{name}', f'{STORE_PATHS["mods"]}/{original_file_name}')
        await self.save_mod()
        return original_file_name

    async def add_resource(self, name: str, modpack_name: str, modpack_version: str, path: str, to: str):
        file_hash = hashlib.sha256(open(path, 'rb').read()).hexdigest()
        root, ext = os.path.splitext(name)

        if os.path.exists(f'{STORE_PATHS["resources"]}/{file_hash}'):
            return file_hash
        self.resources[file_hash] = {
            'original_name': name,
            'hash': file_hash,
            'to': to,
        }
        shutil.move(path, f'{STORE_PATHS["resources"]}/{name}')
        os.rename(f'{STORE_PATHS["resources"]}/{name}', f'{STORE_PATHS["resources"]}/{file_hash}')
        await self.save_resource()

        return file_hash

    async def save_resource(self):
        with open(f'{STORE_PATHS["resources"]}/resources.json', 'w', encoding='utf-8') as f:
            json.dump(self.resources, f, ensure_ascii=False, indent=4)

    async def save_mod(self):
        with open(f'{STORE_PATHS["mods"]}/mods.json', 'w', encoding='utf-8') as f:
            json.dump(self.mods, f, ensure_ascii=False, indent=4)
