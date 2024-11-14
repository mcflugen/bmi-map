import re
from collections import Counter


class Parameter:
    valid_intents = frozenset(("in", "inout", "out"))
    valid_scalar_types = frozenset(("int", "double", "string"))
    valid_array_types = frozenset(("any", "int", "double", "string"))

    def __init__(self, name: str, intent: str, type: str):
        self._name = self.validate_name(name)
        self._intent = self.validate_intent(intent)
        self._type = self.validate_type(type)

    def _astuple(self) -> tuple[str, str, str]:
        return (self.name, self.intent, self.type)

    @property
    def name(self) -> str:
        return self._name

    @property
    def intent(self) -> str:
        return self._intent

    @property
    def type(self) -> str:
        return self._type

    def isscalar(self):
        return not self._type.startswith("array")

    @staticmethod
    def validate_name(name: str) -> str:
        name = name.strip()
        if not name.isidentifier():
            raise ValueError(f"name is not valid ({name})")
        return name

    @staticmethod
    def validate_intent(intent: str) -> str:
        intent = intent.strip()
        if intent not in Parameter.valid_intents:
            raise ValueError(
                f"intent not understood ({intent} not one of"
                f" {', '.join(repr(v) for v in sorted(Parameter.valid_intents))})"
            )
        return intent

    @staticmethod
    def validate_scalar(dtype: str) -> str:
        if dtype not in Parameter.valid_scalar_types:
            raise ValueError(
                f"type not understood ({dtype!r} not one of"
                f" {', '.join(repr(t) for t in sorted(Parameter.valid_scalar_types))})"
            )
        return dtype

    @staticmethod
    def validate_array(dtype: str) -> str:
        if not dtype.startswith("array"):
            raise ValueError("not an array type ({dtype})")

        dtype, dims = Parameter.split_array_type(dtype)
        if dtype not in Parameter.valid_array_types:
            raise ValueError(
                f"array type not understood ({dtype} not one of"
                f" {', '.join(repr(t) for t in sorted(Parameter.valid_array_types))})"
            )
        repeated_dims = [dim for dim, count in Counter(dims).items() if count > 1]
        if repeated_dims:
            raise ValueError(
                f"repeated dimension{'s' if len(repeated_dims) > 1 else ''}"
                f" ({', '.join(repeated_dims)})"
            )

        return f"array[{', '.join((dtype,) + dims)}]"

    @staticmethod
    def validate_type(dtype: str) -> str:
        if dtype.startswith("array"):
            return Parameter.validate_array(dtype)
        else:
            return Parameter.validate_scalar(dtype)

    @staticmethod
    def split_array_type(array_type: str) -> tuple[str, tuple[str, ...]]:
        match = re.match(r"^array\[(.*?)\]$", array_type)
        if match:
            parts = match.group(1).split(",")

            dtype = parts[0].strip()
            try:
                dims = tuple(part.strip() for part in parts[1:])
            except IndexError:
                dims = ()
            return dtype, dims
        else:
            raise ValueError(f"type not understood ({array_type})")
