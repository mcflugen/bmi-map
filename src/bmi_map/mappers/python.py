from collections.abc import Sequence

from bmi_map._mapper import LanguageMapper
from bmi_map._parameter import Parameter


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
