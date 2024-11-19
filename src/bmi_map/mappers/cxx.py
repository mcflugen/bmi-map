from collections.abc import Sequence

from bmi_map._mapper import LanguageMapper
from bmi_map._parameter import Parameter


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
