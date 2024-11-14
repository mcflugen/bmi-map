from __future__ import annotations

import tomllib
from collections.abc import Sequence
from typing import Any
from typing import BinaryIO

from bmi_map._mapper import LanguageMapper
from bmi_map._parameter import Parameter
from bmi_map.mappers.c import CMapper
from bmi_map.mappers.cxx import CxxMapper


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


class PythonMapper(LanguageMapper):
    _type_mapping = {
        "int": "int",
        "double": "float",
        "string": "str",
    }

    def map(self):
        return (
            f"def {self._name}({PythonMapper.map_params(self._params)})"
            f" -> {PythonMapper.map_returns(self._params)}:"
        )

    @staticmethod
    def map_type(dtype: str) -> str:
        if dtype.startswith("array"):
            array_type, _ = Parameter.split_array_type(dtype)
            if array_type == "any":
                py_type = "Any"
            elif array_type == "string":
                py_type = "tuple[str, ...]"
            else:
                py_type = PythonMapper.map_type(array_type)

            if array_type != "string":
                py_type = f"NDArray[{py_type}]"
        else:
            py_type = PythonMapper._type_mapping[dtype]
        return py_type

    @staticmethod
    def map_params(params: Sequence[tuple[str, str, str]]) -> str:
        py_params = ["self"] + [
            f"{name}: {PythonMapper.map_type(dtype)}"
            for name, intent, dtype in params
            if intent.startswith("in")
        ]
        return ", ".join(py_params)

    @staticmethod
    def map_returns(params: Sequence[tuple[str, str, str]]):
        returns = [
            PythonMapper.map_type(dtype)
            for _, intent, dtype in params
            if intent.endswith("out")
        ]
        if len(returns) == 0:
            return "None"
        elif len(returns) == 1:
            return returns[0]
        else:
            return f"tuple[{', '.join(returns)}]"
