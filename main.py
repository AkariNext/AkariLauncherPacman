from argparse import ArgumentParser
import asyncio
import json
import os

from src.modpack import ModPackManager



parser = ArgumentParser()
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
    if all([args.name, args.version, args.mc_version]) is False:
        raise Exception('ModPackの名前、バージョン、Minecraftのバージョンは必須です')
    print('ModPackを作成します')


    os.makedirs(f'./tmp_modpacks/{args.name}', exist_ok=True)
    for i in MODPACK_BASE_FOLDERS:
        os.makedirs(f'./tmp_modpacks/{args.name}/{i}', exist_ok=True)
    with open(f'./tmp_modpacks/{args.name}/modpack.json', 'w') as f:
        json.dump({
            'name': args.name,
            'version': args.version,
            'description': args.description
        }, f, ensure_ascii=False, indent=4)
    modpack_manager = ModPackManager(args.name, args.mc_version)
    await modpack_manager.create(args.version)

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



async def main():
    if args.n:
        await create_modpack()
    elif args.r:
        await release_modpack()
    elif args.e:
        await edit_modpack_version()

if __name__ == '__main__':
    asyncio.run(main())