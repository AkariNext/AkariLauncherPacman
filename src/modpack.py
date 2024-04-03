import json
import os
import shutil
from typing import Literal, TypedDict
from src.const import DISTRIBUTION, STORE_PATHS
from src.store import FileStore
from src.types import IManifest

from src.utils.common import get_files, load_or_create_json

MODPACK_BASE_FOLDERS = ['requiredMods', 'manualMods', 'recommendedMods', 'resources']

class IVersion(TypedDict):
    kind: Literal['mod', 'resource']
    type: str
    key: str


async def get_pack_manifest(name: str):
    data: IManifest = load_or_create_json(f'./modpacks/{name}/manifest.json', {}) # type: ignore
    return data


async def get_pack_mc_version(name: str):
    data: IManifest = load_or_create_json(f'./modpacks/{name}/manifest.json', {}) # type: ignore
    return data['gameVersion']

async def get_all_packs():
    return [ModPackManager(i, await get_pack_mc_version(i)) for i in DISTRIBUTION['modpacks']]


class ModPackVersionManager:
    def __init__(self, name: str, game_version: str, modpack_version: str) -> None:
        self.name = name
        self.game_version = game_version
        self.modpack_version = modpack_version
        self.base_path = f'./modpacks/{self.name}'
        self.mod_version_file: dict[str, IVersion] = load_or_create_json(f'{self.base_path}/versions/{self.modpack_version}.json',
                                                          [])  # type: ignore
        self.file_dependencies: dict[str, list[dict[str, str|int]]] | None = None


    async def sync_files(self, dry_run: bool = False):
        _data: dict[str,IVersion] = {}
        file_store = FileStore()
        for folder in ['mods', 'resources']:
            files = await get_files(f'./tmp_modpacks/{self.name}/{folder}')
            for file in files:
                key = await file_store.add_file(file['file_name'], file['relative_path'], file['relative_path'].replace(f"./tmp_modpacks/{self.name}/", '').replace('resources/', ''), dry_run=dry_run)
                data: IVersion = {
                    'kind': folder[:-1],
                    'type': 'file',
                    'key': key
                }
                _data[key] = data
        if dry_run is False:
            self.mod_version_file = _data
            await self.save()
        return _data

    @property
    def files(self):
        return self.mod_version_file

    async def save(self):
        with open(f'{self.base_path}/versions/{self.modpack_version}.json', mode='w', encoding='utf-8') as f:
            json.dump(self.mod_version_file, f, ensure_ascii=False, indent=4)

    async def create_modpack_dependencies(self):
        packs = await get_all_packs()
        self.file_dependencies = {}
        for pack in packs:
            for version in pack.pack_manifest['versions']:
                version_manager = ModPackVersionManager(pack.name, pack.game_version, version)
                pack_mods = version_manager.mod_version_file
                pack_mods = [i['key'] for i in pack_mods.values()]
                for i in pack_mods:
                    if i not in self.file_dependencies:
                        self.file_dependencies[i] = []
                    self.file_dependencies[i].append({'pack_name':pack.name, 'pack_version': version})
                    print(self.file_dependencies)
        return self.file_dependencies

    async def is_using_other_modpack(self, key: str, pack_name: str, pack_version: str):
        if self.file_dependencies is None:
            file_dependencies = await self.create_modpack_dependencies()
        else:
            file_dependencies = self.file_dependencies
        hit_file = file_dependencies[key]
        hit_count = 0
        for i in hit_file:
            if i['pack_name'] == pack_name and i['pack_version'] == pack_version:
                hit_count += 1
            hit_count += 1
        return hit_count != 0

    async def delete_file(self, key: str):
        file_store = FileStore()
        for file_value in list(self.mod_version_file.values()):
            if file_value['key'] == key:
                self.mod_version_file.pop(key)  # mod version fileから削除
                
                # 他のModPackで使用されていないか確認
                if await self.is_using_other_modpack(file_value['key'], self.name, self.modpack_version) is True:
                    continue

                await file_store.delete_file(key)
        await self.save()


class ModPackManager:
    def __init__(self, name: str, game_version: str) -> None:
        self.name = name
        self.game_version = game_version
        self.base_path = f'./modpacks/{self.name}'
        self.manifest_path = f'{self.base_path}/manifest.json'
        self.pack_manifest: IManifest = load_or_create_json(self.manifest_path)  # type: ignore

    async def create(self, modpack_version: str):
        """
        ModPackを作成します

        Parameters
        ----------
        modpack_version : str
            Minecraftのバージョン
        """
        self.pack_manifest['name'] = self.name
        self.pack_manifest['server'] = {
            'serverHost': 'localhost',
            'serverPort': 25565,
        }
        self.pack_manifest['gameVersion'] = self.game_version
        self.pack_manifest['modLoader'] = {
            'modLoaderType': 'forge',
            'modLoaderVersion': '36.1.0'
        }
        self.pack_manifest['versions'] = []
        await self.save_manifest()
        await self.add_version(modpack_version)

    async def add_version(self, version: str):
        """バージョンを追加します

        Parameters
        ----------
        version : str
            バージョン
        
        """

        # manifestにバージョンを追加
        is_exists = len([i for i in self.pack_manifest['versions'] if i == version]) > 0
        if is_exists is True:
            raise Exception(f'{version} すでに存在するバージョンです')

        self.pack_manifest['versions'].append(version)
        await self.save_manifest()

        # バージョンフォルダを作成
        os.makedirs(f'{self.base_path}/versions', exist_ok=True)

        # バージョンフォルダにバージョンファイルを作成

        modpack_version_manager = ModPackVersionManager(self.name, self.game_version, version)
        await modpack_version_manager.sync_files()

    async def save_manifest(self):
        with open(self.manifest_path, mode='w', encoding='utf-8') as f:
            json.dump(self.pack_manifest, f, ensure_ascii=False, indent=4)

    async def edit_version(self, version: str):
        file_store = FileStore()
        modpack_version_manager = ModPackVersionManager(self.name, self.game_version, version)
        await modpack_version_manager.create_modpack_dependencies()
        files = modpack_version_manager.files
        for mod in files.values():
            file = await file_store.get_file(mod['key'])
            os.makedirs(os.path.dirname(f'./tmp_modpacks/{self.name}/{file["to"]}'), exist_ok=True)
            shutil.copy(f'{STORE_PATHS["files"]}/{mod["key"]}', f'./tmp_modpacks/{self.name}/{file["to"]}')
        with open('./edit_version.json', 'w') as f:
            json.dump({'pack_name':self.name, 'version': version, 'files': modpack_version_manager.mod_version_file}, f, ensure_ascii=False, indent=4)

    async def apply_change(self, version: str):
        modpack_version_manager = ModPackVersionManager(self.name, self.game_version, version)
        if os.path.exists('./edit_version.json') is False:
            raise Exception('edit_version.jsonが存在しません。-eを付けて一度編集を実行してください')
        with open('./edit_version.json', 'r') as f:
            edit_files = json.load(f)

        files = await modpack_version_manager.sync_files(dry_run=True)
        edit_file_keys = [i['key'] for i in edit_files['files'].values()]
        files_keys = [i['key'] for i in files.values()]

        remove_target_keys = list(set(edit_file_keys) - set(files_keys))
        for key in remove_target_keys:
            await modpack_version_manager.delete_file(key)
        await modpack_version_manager.sync_files()
        os.remove('./edit_version.json')
