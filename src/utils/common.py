import json
import os
from typing import Any, TypedDict


def load_or_create_json(path: str, defaukltValue: list | dict[Any, Any] | None = None):
    if defaukltValue is None:
        defaukltValue = {} # type: ignore
    dir_path = os.path.dirname(path)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        os.makedirs(dir_path, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(defaukltValue, f, ensure_ascii=False, indent=4)
        return defaukltValue

class GetFileResult(TypedDict):
    file_name: str
    relative_path: str

async def get_files(path: str):
    files: list[GetFileResult] = []
    for i in os.listdir(path):
        if i in ['.index']:
            continue
        if os.path.isdir(f'{path}/{i}'):
            files.extend(await get_files(f'{path}/{i}'))
        else:
            files.append({'file_name': i, 'relative_path': f'{path}/{i}'})
    return files