from argparse import ArgumentParser
import asyncio
import json
import os
from typing import Literal, Self, TypeGuard

from src.distribution import DistributionManager
from src.utils.common import MISSING, Missing
from src.modpack import ModPackManager
from src.utils.read import Read



parser = ArgumentParser()
parser.add_argument('--init', help='リポジトリの初期化を行います', action='store_true')
parser.add_argument('--name', type=str, help='ModPackの名前など')
parser.add_argument('--version', type=str, help='ModPackのバージョンなど')
parser.add_argument('--mc-version', type=str, help='ModPackのバージョンなど')
parser.add_argument('--description', type=str, help='ModPackの説明')
parser.add_argument('-n',  help='ModPackを新規作成する際のフラグ', action='store_true')
parser.add_argument('-r', help='ModPackをリリースする際のフラグ', action='store_true')
parser.add_argument('-e', help='ModPackを編集する際のフラグ', action='store_true')
parser.add_argument('--apply', help='変更を適応します', action='store_true')

args = parser.parse_args()

MODPACK_BASE_FOLDERS = ['mods', 'resources']
    

async def create_modpack():
    modpack_name = args.name or Read('ModPack名を入力してください').read().value
    modpack_version = args.version or Read('ModPackのバージョンを入力してください').read().value
    minecraft_version = args.mc_version or Read('Minecraftのバージョンを入力してください').read().value
    description = args.description or Read('ModPackの概要を入力してください (default=None)', '').read().optional()



    if all([modpack_name, modpack_version, minecraft_version]) is False:
        raise Exception('ModPackの名前、バージョン、Minecraftのバージョンは必須です')
    print('ModPackを作成します')


    os.makedirs(f'./tmp_modpacks/{modpack_name}', exist_ok=True)
    for i in MODPACK_BASE_FOLDERS:
        os.makedirs(f'./tmp_modpacks/{modpack_name}/{i}', exist_ok=True)
    with open(f'./tmp_modpacks/{modpack_name}/modpack.json', 'w', encoding='utf-8') as f:
        json.dump({
            'name': modpack_name,
            'version': modpack_version,
            'description': description
        }, f, ensure_ascii=False, indent=4)
    modpack_manager = ModPackManager(modpack_name, minecraft_version)
    await modpack_manager.create(modpack_version)

async def edit_modpack_version():
    if [args.name, args.version] is None:
        raise Exception('ModPackの名前、バージョンは必須です')
    modpack_manager = ModPackManager(args.name, args.mc_version)
    if args.apply is False:
        await modpack_manager.edit_version(args.version)
        print('編集を行うため、元のフォルダーにModsやリソースを復元しました。 --applyフラグをつけることで変更を適応できます')
    else:
        await modpack_manager.apply_change(args.version)

async def release_modpack():
    if args.name is None:
        raise Exception('ModPackの名前は必須です')
    modpack_manager = ModPackManager(args.name, args.mc_version)
    await modpack_manager.add_version(args.version)



async def switch_action(action: Literal['n', 'e', 'r'] | None=None):
    if args.n or action == 'n':
        await create_modpack()
    elif args.r or action == 'r':
        await release_modpack()
    elif args.e or action == 'e':
        await edit_modpack_version()
    else:
        print('''何を実行しますか?
n: modpackを新規に作成します
e: 既存のmodpackを編集します
r: modpackをリリースします。
''')
        _action = input(">")
        await switch_action(_action)



async def main():
    if args.init:
        await DistributionManager().init()
    await switch_action()

if __name__ == '__main__':
    asyncio.run(main())