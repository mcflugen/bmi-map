import re
from collections import Counter
from dataclasses import asdict
from dataclasses import astuple
from dataclasses import dataclass

VALID_INTENTS = frozenset(("in", "inout", "out"))
VALID_SCALAR_TYPES = frozenset(("int", "double", "string"))
VALID_ARRAY_TYPES = frozenset(("any", "int", "double", "string"))


@dataclass(frozen=True)
class Parameter:
    name: str
    intent: str
    type: str

    def __post_init__(self):
        object.__setattr__(self, "name", validate_name(self.name))
        object.__setattr__(self, "intent", validate_intent(self.intent))
        object.__setattr__(self, "type", validate_type(self.type))

    def asdict(self):
        return asdict(self)

    def astuple(self):
        return astuple(self)

    def isscalar(self):
        return not self.type.startswith("array")


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


def validate_one_of(
    value: str,
    *,
    allowed=(),
    name: str | None = None,
) -> str:
    name = "value" if name is None else name

    if value not in allowed:
        raise ValueError(
            f"{name} must be one of [{', '.join(sorted(map(repr, allowed)))}]"
            f" (got {value!r})"
        )
    return value


def validate_scalar(dtype: str) -> str:
    validate_one_of(dtype, allowed=VALID_SCALAR_TYPES, name="dtype")
    return dtype


def validate_array(dtype: str) -> str:
    if not dtype.startswith("array"):
        raise ValueError("not an array type ({dtype})")

    dtype, dims = split_array_type(dtype)

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
        dtype, sep, dims = match.group(1).partition(",")

        dtype = validate_one_of(dtype.strip(), allowed=VALID_ARRAY_TYPES, name="dtype")
        if not sep:
            return dtype, ()

        dims = [dim.strip() for dim in dims.split(",")]

        if any(len(dim) == 0 for dim in dims):
            raise ValueError(f"unable to parse array type ({match.group(1)!r})")

        return dtype, tuple(dims)
    else:
        raise ValueError(f"type not understood ({array_type})")
