from collections.abc import Sequence

from bmi_map._parameter import Parameter


class LanguageMapper:
    def map(self, name: str, params: Sequence[Parameter]) -> str:
        raise NotImplementedError("map")
