from __future__ import annotations

import tomllib
from collections.abc import Sequence
from typing import Any
from typing import BinaryIO

from bmi_map.mappers.c import CMapper
from bmi_map.mappers.cxx import CxxMapper
from bmi_map.mappers.python import PythonMapper
from bmi_map.mappers.sidl import SidlMapper


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
