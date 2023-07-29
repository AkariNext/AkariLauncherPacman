from typing import Literal, TypedDict


class IManifestServer(TypedDict):
    serverHost: str
    serverPort: int


class IManifestModLoader(TypedDict):
    modLoaderType: Literal["forge", "fabric"]
    modLoaderVersion: str


class IManifest(TypedDict):
    name: str
    server: IManifestServer
    gameVersion: str
    modLoader: IManifestModLoader
    versions: list[str]
