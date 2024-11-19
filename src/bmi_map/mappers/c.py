from collections.abc import Sequence

from bmi_map._mapper import LanguageMapper
from bmi_map._parameter import Parameter


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
