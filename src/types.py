from typing import Literal, TypedDict


class IManifestServer(TypedDict):
    serverHost: str
    serverPort: int


class IManifestModLoader(TypedDict):
    modLoaderType: str
    modLoaderVersion: str


class IManifest(TypedDict):
    name: str
    server: IManifestServer
    gameVersion: str
    modLoader: IManifestModLoader
    versions: list[str]

class IDistribution(TypedDict):
    name: str
    modpacks: list[str]
    repository_type: Literal['github', 's3']
    format_version: str
    base_url: str

