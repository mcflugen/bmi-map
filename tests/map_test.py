import pytest
from bmi_map._parameter import Parameter
from bmi_map.bmi_map import bmi_map


@pytest.mark.parametrize(
    "intent,expected",
    [
        ("in", "int foo(in int a);"),
        ("inout", "int foo(inout int a);"),
        ("out", "int foo(out int a);"),
    ],
)
def test_sidl_one_parameter(intent, expected):
    params = [Parameter(name="a", type="int", intent=intent)]
    mapped_func = bmi_map("foo", params, to="sidl")
    assert mapped_func == expected


@pytest.mark.parametrize(
    "intent,expected",
    [
        ("in", "int foo(void* self, const int a);"),
        ("inout", "int foo(void* self, int* a);"),
        ("out", "int foo(void* self, int* a);"),
    ],
)
def test_c_one_parameter(intent, expected):
    params = [Parameter(name="a", type="int", intent=intent)]
    mapped_func = bmi_map("foo", params, to="c")
    assert mapped_func == expected


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
        Parameter(name="a", type="int", intent=a_intent),
        Parameter(name="b", type="int", intent=b_intent),
    ]
    mapped_func = bmi_map("foo", params, to="c")
    assert mapped_func == expected


@pytest.mark.parametrize(
    "intent,expected",
    [
        ("in", "int foo(void* self, const int* a);"),
        ("inout", "int foo(void* self, int* a);"),
        ("out", "int foo(void* self, int** a);"),
    ],
)
def test_c_array_intent(intent, expected):
    params = [Parameter(name="a", type="array[int]", intent=intent)]
    mapped_func = bmi_map("foo", params, to="c")
    assert mapped_func == expected


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
        Parameter(name="a", intent="in", type=f"array[int,{dims}]"),
        Parameter(name="b", intent="in", type="array[int]"),
    ]
    mapped_func = bmi_map("f", params, to="c")
    assert mapped_func == expected


@pytest.mark.parametrize(
    "intent,expected",
    [
        ("in", "void Foo(const int a);"),
        ("inout", "void Foo(int* a);"),
        ("out", "int Foo();"),
    ],
)
def test_cxx_one_parameter(intent, expected):
    params = [Parameter(name="a", type="int", intent=intent)]
    mapped_func = bmi_map("foo", params, to="c++")
    assert mapped_func == expected


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
        Parameter(name="a", type="int", intent=a_intent),
        Parameter(name="b", type="int", intent=b_intent),
    ]
    mapped_func = bmi_map("foo", params, to="c++")
    assert mapped_func == expected


@pytest.mark.parametrize(
    "intent,c_type",
    [("in", "const char*"), ("out", "char*"), ("inout", "char*")],
)
def test_c_string_intent(intent, c_type):
    assert bmi_map("foo", [Parameter("s", intent, "string")], to="c") == (
        f"int foo(void* self, {c_type} s);"
    )


@pytest.mark.parametrize(
    "name,signature",
    [
        ("get_component_name", "char* name"),
        ("get_grid_type", "const int grid, char* type"),
        ("get_var_units", "const char* name, char* units"),
        ("get_grid_x", "const int grid, double* x"),
        ("get_grid_shape", "const int grid, int* shape"),
        ("get_value", "const char* name, void* dest"),
        (
            "get_value_at_indices",
            "const char* name, void* dest, const int* inds, const int count",
        ),
        ("get_value_ptr", "const char* name, void** dest_ptr"),
        ("get_input_var_names", "char** names"),
        ("get_output_var_names", "char** names"),
        ("set_value", "const char* name, const void* src"),
    ],
)
def test_c_builtin_buffer_signatures(name, signature):
    from bmi_map.bmi_map import map_bmi_function

    assert map_bmi_function(name, to="c") == f"int {name}(void* self, {signature});"


@pytest.mark.parametrize(
    "dtype,cxx_type",
    [("int", "int"), ("double", "double"), ("any", "void")],
)
@pytest.mark.parametrize("dims", ("", ", n"))
@pytest.mark.parametrize("intent", ("in", "inout", "out"))
def test_cxx_array_intent(dtype, cxx_type, dims, intent):
    params = [Parameter("a", intent, f"array[{dtype}{dims}]")]
    if intent == "in":
        expected = f"void Foo(const {cxx_type}* a);"
    elif intent == "inout":
        expected = f"void Foo({cxx_type}* a);"
    else:
        expected = f"{cxx_type}* Foo();"

    assert bmi_map("foo", params, to="c++") == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("get_grid_x", "void GetGridX(const int grid, double* x);"),
        ("get_grid_shape", "void GetGridShape(const int grid, int* shape);"),
        ("get_value", "void GetValue(std::string name, void* dest);"),
        (
            "get_value_at_indices",
            "void GetValueAtIndices(std::string name, void* dest, const int* inds);",
        ),
        ("get_value_ptr", "void* GetValuePtr(std::string name);"),
    ],
)
def test_cxx_builtin_buffer_signatures(name, expected):
    from bmi_map.bmi_map import map_bmi_function

    assert map_bmi_function(name, to="c++") == expected
