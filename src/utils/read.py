from typing import Self
from src.utils.common import MISSING, Missing


class Read:
    def __init__(self, title: str, default: str=MISSING, ) -> None:
        self.title = title
        self.default: str = default
        self.value: str
        self._enum: list[str] = []
    
    def read(self) -> Self:
        print(self.title)
        if self._enum:
            print(f'この項目には以下の値のみが使用できます\n- {"\n- ".join(self._enum)}\n')
        text = input('>')
        
        if len(text) == 0:
            if isinstance(self.default, Missing):
                return self.read()
            self.value = self.default
        self.value = text

        if self._enum:
            self.valid_enum()
        return self

    def enum(self, allow_value: list[str]) -> Self:
        """enumを設定します。readより前に呼び出してください"""
        self._enum = allow_value
        return self
    
    def valid_enum(self):
        if self.value not in self._enum:
            return self.read()

    def optional(self) -> str | None:
        """readより後に呼び出すことで、文字列が0文字の場合Noneに変換します"""
        if len(self.value) == 0:
            return None
        return self.value
