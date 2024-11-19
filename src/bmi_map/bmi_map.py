from __future__ import annotations

import tomllib
from collections.abc import Sequence
from typing import Any
from typing import BinaryIO

from bmi_map._mapper import LanguageMapper
from bmi_map._parameter import Parameter


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


class CMapper(LanguageMapper):
    _type_mapping = {
        "int": "int",
        "double": "double",
        "string": "char*",
    }

    def map(self) -> str:
        return f"int {self._name}({self.map_params(self._params)});"

    @staticmethod
    def map_type(dtype: str) -> str:
        if dtype.startswith("array"):
            array_type, _ = Parameter.split_array_type(dtype)
            if array_type == "any":
                c_type = "void"
            else:
                c_type = CMapper.map_type(array_type)

            if array_type != "string":
                c_type += "*"
        else:
            c_type = CMapper._type_mapping[dtype]
        return c_type

    @staticmethod
    def map_params(params: Sequence[tuple[str, str, str]]) -> str:
        c_params = ["void* self"]
        for name, intent, dtype in params:
            c_type = CMapper.map_type(dtype)
            if intent.endswith("out") and dtype != "string":
                c_type = f"{c_type}*"
            if intent == "in" or dtype == "string":
                c_type = f"const {c_type}"
            c_params.append(f"{c_type} {name}")

            if dtype.startswith("array"):
                _, dims = Parameter.split_array_type(dtype)
                c_params += [f"const int {dim}" for dim in dims]

        return ", ".join(c_params)


class CxxMapper(LanguageMapper):
    _type_mapping = {
        "int": "int",
        "double": "double",
        "string": "std::string",
    }

    def __init__(self, name: str, params: Sequence[dict[str, str]] | None = None):
        name = "".join(part.title() for part in name.split("_"))
        super().__init__(name, params)

    def map(self) -> str:
        return (
            f"{self.map_returns(self._params)}"
            f" {self._name}({self.map_params(self._params)});"
        )

    @staticmethod
    def map_type(dtype: str) -> str:
        if dtype.startswith("array"):
            array_type, _ = Parameter.split_array_type(dtype)
            if array_type == "any":
                cxx_type = "void"
            elif array_type == "string":
                cxx_type = "std::vector<std::string>"
            else:
                cxx_type = CxxMapper.map_type(array_type)

            if dtype != "string":
                cxx_type += "*"
        else:
            cxx_type = CxxMapper._type_mapping[dtype]

        return cxx_type

    @staticmethod
    def map_params(params: Sequence[tuple[str, str, str]]) -> str:
        cxx_params = []
        for name, intent, dtype in params:
            cxx_type = CxxMapper.map_type(dtype)
            if dtype != "string":
                if intent == "in":
                    cxx_type = f"const {cxx_type}"
                elif intent.endswith("out"):
                    cxx_type = f"{cxx_type}*"
            if intent.startswith("in"):
                cxx_params.append(f"{cxx_type} {name}")
        return ", ".join(cxx_params)

    @staticmethod
    def map_returns(params: Sequence[tuple[str, str, str]]):
        returns = [
            CxxMapper.map_type(dtype) for _, intent, dtype in params if intent == "out"
        ]

        if len(returns) == 0:
            return "void"
        elif len(returns) == 1:
            return returns[0]
        else:
            raise ValueError("multiple return types not allowed")


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
