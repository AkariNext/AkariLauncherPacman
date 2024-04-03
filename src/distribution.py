import json
from src.types import IDistribution
from src.utils.common import load_or_create_json
from src.utils.read import Read


class DistributionManager:
    def __init__(self) -> None:
        self.distribution:IDistribution = load_or_create_json('./distribution.json')  # type: ignore

    async def init(self):
        name = Read('リポジトリ名を入力してください').read().value
        repository_type = Read('リポジトリの種類を指定してください').enum(['s3', 'github']).read().value
        base_url = Read('ベースURLを指定してください。GitHubの場合はrawのブランチを指定').read().value
        self.distribution = {  # type: ignore
            'name': name,
            'modpacks': [],
            'repository_type': repository_type, # type: ignore
            'format_version': '1.0.0',
            'base_url': base_url
        }
        await self.save()

    async def add_modpack(self, name: str):
        """ModPackを追加します"""
        self.distribution['modpacks'].append(name)

    async def get_modpacks(self):
        """存在するModPackの一覧を返します"""
        return self.distribution['modpacks']

    async def save(self):
        with open('./distribution.json', mode='w', encoding='utf-8') as f:
            json.dump(self.distribution, f, ensure_ascii=False, indent=4)
