import pytest

from bmi_map import Parameter


@pytest.mark.parametrize("array_type", ("int", "double", "string", "any"))
@pytest.mark.parametrize("dims", ("", "m", "m,n", " m, n , o"))
def test_array_is_valid(array_type, dims):
    array_type, actual_dims = Parameter.split_array_type(
        Parameter.validate_array(f"array[{','.join([array_type, dims])}]")
    )

    assert array_type == array_type
    assert actual_dims == tuple(dim.strip() for dim in dims.split(","))


@pytest.mark.parametrize("array_type", ("long", "float", "boolean", ""))
def test_array_with_bad_type(array_type):
    with pytest.raises(ValueError):
        Parameter.validate_array(f"array[{array_type}]")


@pytest.mark.parametrize("dims", ("m,m", "m,n,m"))
def test_array_with_repeated_dims(dims):
    with pytest.raises(ValueError):
        Parameter.validate_array(f"array[any, {dims}]")
