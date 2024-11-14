from collections.abc import Sequence

from bmi_map._parameter import Parameter


class LanguageMapper:
    def __init__(self, name: str, params: Sequence[dict[str, str]] | None = None):
        params = () if params is None else params

        if not name.isidentifier():
            raise ValueError("bad name ({name})")

        self._name = name
        self._params = tuple(Parameter(**param)._astuple() for param in params)

    def __str__(self) -> str:
        return self.map()

    def map(self) -> str:
        raise NotImplementedError("map")
