from __future__ import annotations

import tomllib
from collections.abc import Sequence
from typing import Any
from typing import BinaryIO

from bmi_map._mapper import LanguageMapper
from bmi_map._parameter import Parameter
from bmi_map.mappers.c import CMapper
from bmi_map.mappers.cxx import CxxMapper
from bmi_map.mappers.python import PythonMapper


def bmi_map(
    funcs: dict[str, dict[str, Sequence[dict[str, str]]]], to="sidl"
) -> list[str]:
    """Map a BMI to a given language.

    Parameters
    ----------
    funcs : dict
        Interface definitions of BMI functions.
    to : str, optional
        Language to which to map the interface.

    Examples
    --------
    >>> from bmi_map.bmi_map import bmi_map
    >>> funcs = {
    ...     "get_component_name": {
    ...         "params": [dict(name="name", intent="in", type="string")]
    ...     }
    ... }
    >>> bmi_map(funcs, to="c")
    ['int get_component_name(void* self, const char* name);']
    """
    LANGUAGE_MAPPER = {
        "c": CMapper,
        "c++": CxxMapper,
        "python": PythonMapper,
        "sidl": SidlMapper,
    }

    mapper = LANGUAGE_MAPPER[to]

    return [
        mapper(name, params=func["params"]).map()
        for name, func in sorted(funcs.items())
    ]


def _load_interface_definition(file: BinaryIO) -> dict[str, dict[str, Any]]:
    return tomllib.load(file)["bmi"]


class SidlMapper(LanguageMapper):
    def map(self) -> str:
        return f"int {self._name}({SidlMapper.map_params(self._params)});"

    @staticmethod
    def map_type(dtype: str) -> str:
        if dtype.startswith("array"):
            dtype, dims = Parameter.split_array_type(dtype)
            if dtype == "any":
                dtype = ""
            if dims:
                return f"array<{dtype.strip()}, {len(dims)}>"
            else:
                return f"array<{dtype.strip()},>"
        else:
            return dtype

    @staticmethod
    def map_params(params: Sequence[tuple[str, str, str]]) -> str:
        return ", ".join(
            [
                f"{name} {intent} {SidlMapper.map_type(dtype)}"
                for name, intent, dtype in params
            ]
        )
