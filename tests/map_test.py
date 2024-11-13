import pytest

from bmi_map import bmi_map


@pytest.mark.parametrize(
    "intent,expected",
    [
        ("in", "int foo(void* self, const int a);"),
        ("inout", "int foo(void* self, int* a);"),
        ("out", "int foo(void* self, int* a);"),
    ],
)
def test_c_one_parameter(intent, expected):
    params = [{"name": "a", "type": "int", "intent": intent}]
    mapped_func = bmi_map({"foo": {"params": params}}, to="c")
    assert mapped_func[0] == expected


@pytest.mark.parametrize(
    "a_intent,b_intent,expected",
    [
        ("in", "in", "int foo(void* self, const int a, const int b);"),
        ("in", "inout", "int foo(void* self, const int a, int* b);"),
        ("in", "out", "int foo(void* self, const int a, int* b);"),
        ("inout", "in", "int foo(void* self, int* a, const int b);"),
        ("out", "in", "int foo(void* self, int* a, const int b);"),
        ("out", "out", "int foo(void* self, int* a, int* b);"),
    ],
)
def test_c_two_parameter(a_intent, b_intent, expected):
    params = [
        {"name": "a", "type": "int", "intent": a_intent},
        {"name": "b", "type": "int", "intent": b_intent},
    ]
    mapped_func = bmi_map({"foo": {"params": params}}, to="c")
    assert mapped_func[0] == expected


@pytest.mark.parametrize(
    "intent,expected",
    [
        ("in", "int foo(void* self, const int* a);"),
        ("inout", "int foo(void* self, int** a);"),
        ("out", "int foo(void* self, int** a);"),
    ],
)
def test_c_array_intent(intent, expected):
    p = {"name": "a", "type": "array[int]", "intent": intent}
    mapped_func = bmi_map({"foo": {"params": [p]}}, to="c")
    assert mapped_func[0] == expected


@pytest.mark.parametrize(
    "dims,expected",
    [
        ("m", "int f(void* self, const int* a, const int m, const int* b);"),
        (
            "m,n",
            "int f(void* self, const int* a, const int m, const int n, const int* b);",
        ),
    ],
)
def test_c_array_with_dimensions(dims, expected):
    params = [
        {"name": "a", "type": f"array[int,{dims}]", "intent": "in"},
        {"name": "b", "type": "array[int]", "intent": "in"},
    ]
    mapped_func = bmi_map({"f": {"params": params}}, to="c")
    assert mapped_func[0] == expected


@pytest.mark.parametrize(
    "intent,expected",
    [
        ("in", "void Foo(const int a);"),
        ("inout", "void Foo(int* a);"),
        ("out", "int Foo();"),
    ],
)
def test_cxx_one_parameter(intent, expected):
    params = [{"name": "a", "type": "int", "intent": intent}]
    mapped_func = bmi_map({"foo": {"params": params}}, to="c++")
    assert mapped_func[0] == expected


@pytest.mark.parametrize(
    "a_intent,b_intent,expected",
    [
        ("in", "in", "void Foo(const int a, const int b);"),
        ("in", "inout", "void Foo(const int a, int* b);"),
        ("in", "out", "int Foo(const int a);"),
        ("inout", "in", "void Foo(int* a, const int b);"),
        ("out", "in", "int Foo(const int b);"),
    ],
)
def test_cxx_two_parameter(a_intent, b_intent, expected):
    params = [
        {"name": "a", "type": "int", "intent": a_intent},
        {"name": "b", "type": "int", "intent": b_intent},
    ]
    mapped_func = bmi_map({"foo": {"params": params}}, to="c++")
    assert mapped_func[0] == expected
