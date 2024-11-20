from collections.abc import Sequence

from bmi_map._mapper import LanguageMapper
from bmi_map._parameter import Parameter


class PythonMapper(LanguageMapper):
    _type_mapping = {
        "int": "int",
        "double": "float",
        "string": "str",
    }

    def map(self, name: str, params: Sequence[Parameter]) -> str:
        return (
            f"def {name}({PythonMapper.map_params(params)})"
            f" -> {PythonMapper.map_returns(params)}:"
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
    def map_param(param: Parameter) -> str:
        return f"{param.name}: {PythonMapper.map_type(param.type)}"

    @staticmethod
    def map_params(params: Sequence[Parameter]) -> str:
        return ", ".join(
            ["self"]
            + [PythonMapper.map_param(p) for p in params if p.intent.startswith("in")]
        )

    @staticmethod
    def map_returns(params: Sequence[Parameter]) -> str:
        returns = [
            PythonMapper.map_type(p.type) for p in params if p.intent.endswith("out")
        ]
        if len(returns) == 0:
            return "None"
        elif len(returns) == 1:
            return returns[0]
        else:
            return f"tuple[{', '.join(returns)}]"
