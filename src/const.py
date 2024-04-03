from typing import Literal

from src.types import IDistribution
from src.utils.common import load_or_create_json

STORE_PATHS: dict[Literal['mods', 'resources', 'files'], str] = {
    'mods': './store/mods',
    'resources': './store/resources',
    'files': './store/files'
}

DISTRIBUTION: IDistribution = load_or_create_json('./distribution.json') # type: ignore

