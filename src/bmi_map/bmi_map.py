from __future__ import annotations

import tomllib
from collections.abc import Sequence
from typing import Any
from typing import BinaryIO

from bmi_map._bmi import BMI
from bmi_map._parameter import Parameter
from bmi_map.mappers.c import CMapper
from bmi_map.mappers.cxx import CxxMapper
from bmi_map.mappers.fortran import FortranMapper
from bmi_map.mappers.python import PythonMapper
from bmi_map.mappers.sidl import SidlMapper


def bmi_map(name: str, params: Sequence[Parameter], to: str = "sidl") -> str:
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
        "fortran": FortranMapper,
        "python": PythonMapper,
        "sidl": SidlMapper,
    }

    mapper = LANGUAGE_MAPPER[to]()

    return mapper.map(name, params)


def map_bmi_function(name: str, to: str) -> str:
    return bmi_map(name, BMI[name], to=to)


def load(stream: BinaryIO) -> dict[str, tuple[Parameter, ...]]:
    return _spec_to_dict(tomllib.load(stream)["bmi"])


def loads(s: str) -> dict[str, tuple[Parameter, ...]]:
    return _spec_to_dict(tomllib.loads(s)["bmi"])


def _spec_to_dict(funcs: dict[str, dict[str, Any]]) -> dict[str, tuple[Parameter, ...]]:
    return {
        name: tuple(Parameter(**param) for param in signature["params"])
        for name, signature in funcs.items()
    }
