from __future__ import annotations

import argparse
import re
import sys
import tomllib
from collections.abc import Sequence
from functools import partial
from typing import Any
from typing import BinaryIO

try:
    import pygments
    import pygments.lexers
    from pygments.formatters import TerminalTrueColorFormatter

    with_pygments = True
except ImportError:
    with_pygments = False


__version__ = "0.1.0"


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--to",
        help="language for which to generate mappings",
        choices=("c", "c++", "fortran", "python", "sidl"),
        default="sidl",
    )
    parser.add_argument("--include", default=".*", help="Functions to include")
    parser.add_argument(
        "--color",
        choices=("always", "auto", "never"),
        default="auto",
        help="When to use syntax highlighting.",
    )

    args = parser.parse_args(argv)

    color = args.color if with_pygments else "never"

    funcs = _filter_keys(
        _load_interface_definition(sys.stdin.buffer), include=args.include
    )

    mapped_funcs = bmi_map(funcs, to=args.to)

    if color == "always" or (color == "auto" and sys.stdout.isatty()):
        highlight = Highlighter(args.to)
        mapped_funcs = [highlight(mapped_func) for mapped_func in mapped_funcs]

    print("\n".join(mapped_funcs))

    return 0


def bmi_map(
    funcs: dict[str, dict[str, Sequence[dict[str, str]]]], to="sidl"
) -> list[str]:
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


def _filter_keys(d: dict[str, Any], include: str = ".*") -> dict[str, Any]:
    pattern = re.compile(include)
    return {k: v for k, v in d.items() if pattern.search(k)}


class Highlighter:
    def __init__(self, language: str):
        if language == "sidl":
            language = "java"

        self._highlight = partial(
            pygments.highlight,
            lexer=pygments.lexers.find_lexer_class_by_name(language)(ensurenl=False),
            formatter=TerminalTrueColorFormatter(),
        )

    def __call__(self, line: str) -> str:
        return self._highlight(line)


class Parameter:
    valid_intents = frozenset(("in", "inout", "out"))
    valid_scalar_types = frozenset(("int", "double", "string"))
    valid_array_types = frozenset(("any", "int", "double", "string"))

    def __init__(self, name: str, intent: str, type: str):
        self._name = self.validate_name(name)
        self._intent = self.validate_intent(intent)
        self._type = self.validate_type(type)

    def _astuple(self) -> tuple[str, str, str]:
        return (self.name, self.intent, self.type)

    @property
    def name(self) -> str:
        return self._name

    @property
    def intent(self) -> str:
        return self._intent

    @property
    def type(self) -> str:
        return self._type

    def isscalar(self):
        return not self._type.startswith("array")

    @staticmethod
    def validate_name(name: str) -> str:
        name = name.strip()
        if not name.isidentifier():
            raise ValueError(f"name is not valid ({name})")
        return name

    @staticmethod
    def validate_intent(intent: str) -> str:
        intent = intent.strip()
        if intent not in Parameter.valid_intents:
            raise ValueError(
                f"intent not understood ({intent} not one of"
                f" {', '.join(repr(v) for v in sorted(Parameter.valid_intents))})"
            )
        return intent

    @staticmethod
    def validate_scalar(dtype: str) -> str:
        if dtype not in Parameter.valid_scalar_types:
            raise ValueError(
                f"type not understood ({dtype!r} not one of"
                f" {', '.join(repr(t) for t in sorted(Parameter.valid_scalar_types))})"
            )
        return dtype

    @staticmethod
    def validate_array(dtype: str) -> str:
        if not dtype.startswith("array"):
            raise ValueError("not an array type ({dtype})")

        rank, dtype = Parameter.split_array_type(dtype)
        if dtype not in Parameter.valid_array_types:
            raise ValueError(
                f"array type not understood ({dtype} not one of"
                f" {', '.join(repr(t) for t in sorted(Parameter.valid_array_types))})"
            )

        return f"array[{rank!s}, {dtype}]"

    @staticmethod
    def validate_type(dtype: str) -> str:
        if dtype.startswith("array"):
            return Parameter.validate_array(dtype)
        else:
            return Parameter.validate_scalar(dtype)

    @staticmethod
    def split_array_type(array_type: str) -> tuple[int, str]:
        match = re.match(r"^array\[(.*?)\]$", array_type)
        if match:
            rank, dtype = match.group(1).split(",")
            return int(rank), dtype.strip()
        else:
            raise ValueError(f"type not understood ({array_type})")


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


class SidlMapper(LanguageMapper):
    def map(self) -> str:
        return f"int {self._name}({SidlMapper.map_params(self._params)});"

    @staticmethod
    def map_type(dtype: str) -> str:
        if dtype.startswith("array"):
            rank, dtype = Parameter.split_array_type(dtype)
            if dtype == "any":
                dtype = ""
            return f"array<{dtype.strip()}, {rank}>"
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
            _, array_type = Parameter.split_array_type(dtype)
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
            _, array_type = Parameter.split_array_type(dtype)
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
            _, array_type = Parameter.split_array_type(dtype)
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


if __name__ == "__main__":
    SystemExit(main())
