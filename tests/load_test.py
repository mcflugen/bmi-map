from bmi_map._parameter import Parameter
from bmi_map.bmi_map import loads


def test_loads_one_parameter():
    content = """\
[bmi.foo]
params = [
    { name = "a", intent = "in", type = "double" }
]
"""
    spec = loads(content)
    assert spec == {"foo": (Parameter(name="a", intent="in", type="double"),)}


def test_loads_two_parameters():
    content = """\
[bmi.foo]
params = [
    { name = "a", intent = "in", type = "double" },
    { name = "b", intent = "inout", type = "array[int, n]" },
]
"""
    spec = loads(content)
    assert spec == {
        "foo": (
            Parameter(name="a", intent="in", type="double"),
            Parameter(name="b", intent="inout", type="array[int, n]"),
        )
    }


def test_loads_empty():
    content = """\
[bmi]
"""
    spec = loads(content)
    assert spec == {}
