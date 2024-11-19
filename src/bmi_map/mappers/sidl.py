from collections.abc import Sequence

from bmi_map._mapper import LanguageMapper
from bmi_map._parameter import Parameter
from bmi_map._parameter import split_array_type


class SidlMapper(LanguageMapper):
    def map(self, name: str, params: Sequence[Parameter]) -> str:
        return f"int {name}({SidlMapper.map_params(params)});"

    @staticmethod
    def map_type(dtype: str) -> str:
        if dtype.startswith("array"):
            dtype, dims = split_array_type(dtype)
            if dtype == "any":
                dtype = ""
            if dims:
                return f"array<{dtype.strip()}, {len(dims)}>"
            else:
                return f"array<{dtype.strip()},>"
        else:
            return dtype

    @staticmethod
    def map_param(param: Parameter) -> str:
        return f"{param.name} {param.intent} {SidlMapper.map_type(param.type)}"

    @staticmethod
    def map_params(params: Sequence[Parameter]) -> str:
        return ", ".join(SidlMapper.map_param(p) for p in params)
