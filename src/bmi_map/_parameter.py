import re
from collections import Counter
from dataclasses import asdict
from dataclasses import astuple
from dataclasses import dataclass

VALID_INTENTS = frozenset(("in", "inout", "out"))
VALID_SCALAR_TYPES = frozenset(("int", "double", "string"))
VALID_ARRAY_TYPES = frozenset(("any", "int", "double", "string"))


@dataclass
class Parameter:
    name: str
    intent: str
    type: str

    def __post_init__(self):
        self.name = validate_name(self.name)
        self.intent = validate_intent(self.intent)
        self.type = validate_type(self.type)

    def asdict(self):
        return asdict(self)

    def astuple(self):
        return astuple(self)

    def isscalar(self):
        return not self._type.startswith("array")


def validate_name(name: str) -> str:
    name = name.strip()
    if not name.isidentifier():
        raise ValueError(f"name is not valid ({name})")
    return name


def validate_intent(intent: str) -> str:
    intent = intent.strip()
    if intent not in VALID_INTENTS:
        raise ValueError(
            f"intent not understood ({intent} not one of"
            f" {', '.join(repr(v) for v in sorted(VALID_INTENTS))})"
        )
    return intent


def validate_scalar(dtype: str) -> str:
    if dtype not in VALID_SCALAR_TYPES:
        raise ValueError(
            f"type not understood ({dtype!r} not one of"
            f" {', '.join(repr(t) for t in sorted(VALID_SCALAR_TYPES))})"
        )
    return dtype


def validate_array(dtype: str) -> str:
    if not dtype.startswith("array"):
        raise ValueError("not an array type ({dtype})")

    dtype, dims = split_array_type(dtype)
    if dtype not in VALID_ARRAY_TYPES:
        raise ValueError(
            f"array type not understood ({dtype} not one of"
            f" {', '.join(repr(t) for t in sorted(VALID_ARRAY_TYPES))})"
        )
    repeated_dims = [dim for dim, count in Counter(dims).items() if count > 1]
    if repeated_dims:
        raise ValueError(
            f"repeated dimension{'s' if len(repeated_dims) > 1 else ''}"
            f" ({', '.join(repeated_dims)})"
        )

    return f"array[{', '.join((dtype,) + dims)}]"


def validate_type(dtype: str) -> str:
    if dtype.startswith("array"):
        return validate_array(dtype)
    else:
        return validate_scalar(dtype)


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
