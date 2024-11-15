from collections.abc import Sequence

from bmi_map._mapper import LanguageMapper
from bmi_map._parameter import Parameter


class CMapper(LanguageMapper):
    _type_mapping = {
        "int": "int",
        "double": "double",
        "string": "char*",
    }

    def map(self, name: str, params: Sequence[Parameter]) -> str:
        return f"int {name}({self.map_params(params)});"

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
    def map_param(param: Parameter) -> str:
        c_type = CMapper.map_type(param.type)
        if param.intent.endswith("out") and param.type != "string":
            c_type = f"{c_type}*"
        if param.intent == "in" or param.type == "string":
            c_type = f"const {c_type}"
        c_param = f"{c_type} {param.name}"

        if param.type.startswith("array"):
            _, dims = Parameter.split_array_type(param.type)
            c_param = ", ".join([c_param] + [f"const int {dim}" for dim in dims])

        return c_param

    @staticmethod
    def map_params(params: Sequence[Parameter]) -> str:
        return ", ".join(["void* self"] + [CMapper.map_param(p) for p in params])
