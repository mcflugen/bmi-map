from collections.abc import Sequence

from bmi_map._mapper import LanguageMapper
from bmi_map._parameter import Parameter


class CxxMapper(LanguageMapper):
    _type_mapping = {
        "int": "int",
        "double": "double",
        "string": "std::string",
    }

    def map(self, name: str, params: Sequence[Parameter]) -> str:
        name = "".join(part.title() for part in name.split("_"))
        return f"{self.map_returns(params)} {name}({self.map_params(params)});"

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
    def map_param(param: Parameter) -> str:
        cxx_type = CxxMapper.map_type(param.type)
        if param.type != "string":
            if param.intent == "in":
                cxx_type = f"const {cxx_type}"
            elif param.intent.endswith("out"):
                cxx_type = f"{cxx_type}*"
        return f"{cxx_type} {param.name}"

    @staticmethod
    def map_params(params: Sequence[Parameter]) -> str:
        return ", ".join(
            CxxMapper.map_param(param)
            for param in params
            if param.intent.startswith("in")
        )

    @staticmethod
    def map_returns(params: Sequence[Parameter]) -> str:
        returns = [CxxMapper.map_type(p.type) for p in params if p.intent == "out"]

        if len(returns) == 0:
            return "void"
        elif len(returns) == 1:
            return returns[0]
        else:
            raise ValueError("multiple return types not allowed")
