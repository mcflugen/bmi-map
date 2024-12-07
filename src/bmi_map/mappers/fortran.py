from collections.abc import Sequence

from bmi_map._mapper import LanguageMapper
from bmi_map._parameter import Parameter


class FortranMapper(LanguageMapper):
    _type_mapping = {
        "int": "int",
        "double": "double precision",
        "string": "character(len=*)",
    }

    def map(self, name: str, params: Sequence[Parameter]) -> str:
        return f"function {name}({self.map_params(params)}) result(bmi_status)"

    @staticmethod
    def map_params(params: Sequence[Parameter]) -> str:
        return ", ".join(["this"] + [p.name for p in params])
