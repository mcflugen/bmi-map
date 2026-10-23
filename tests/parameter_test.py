import pytest
from bmi_map._parameter import Parameter


@pytest.mark.parametrize("dtype", ("int", "double", "string"))
def test_scalar_parameter_isscalar(dtype):
    assert Parameter(name="value", intent="in", type=dtype).isscalar() is True


@pytest.mark.parametrize("dtype", ("int", "double", "string", "any"))
@pytest.mark.parametrize("dims", ("", ", n", ", m, n"))
def test_array_parameter_is_not_scalar(dtype, dims):
    parameter = Parameter(name="values", intent="in", type=f"array[{dtype}{dims}]")

    assert parameter.isscalar() is False
