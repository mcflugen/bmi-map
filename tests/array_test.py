import pytest
from bmi_map._parameter import split_array_type
from bmi_map._parameter import validate_array


@pytest.mark.parametrize("array_type", ("int", "double", "string", "any"))
@pytest.mark.parametrize("dims", ("", "m", "m,n", " m, n , o"))
def test_array_is_valid(array_type, dims):
    array_spec = f"{array_type},{dims}" if dims else array_type
    actual_type, actual_dims = split_array_type(validate_array(f"array[{array_spec}]"))

    expected_dims = tuple(dim.strip() for dim in dims.split(",")) if dims else ()

    assert actual_type == array_type
    assert actual_dims == expected_dims


@pytest.mark.parametrize("array_type", ("int", "double", "string", "any"))
@pytest.mark.parametrize("dims", ("", ", n"))
def test_array_type_whitespace(array_type, dims):
    array_spec = f"{array_type} {dims}"

    expected_dims = ("n",) if dims else ()

    assert split_array_type(f"array[ {array_spec}]") == (array_type, expected_dims)


@pytest.mark.parametrize("array_type", ("int", "double", "string", "any"))
@pytest.mark.parametrize("dims", ("", " ", "n,", ",n", "m,,n", "m, ,n"))
@pytest.mark.parametrize("parse", (split_array_type, validate_array))
def test_array_with_empty_dimension(array_type, dims, parse):
    with pytest.raises(ValueError):
        parse(f"array[{array_type},{dims}]")


@pytest.mark.parametrize("array_type", ("long", "float", "boolean", ""))
def test_array_with_bad_type(array_type):
    with pytest.raises(ValueError):
        validate_array(f"array[{array_type}]")


@pytest.mark.parametrize("dims", ("m,m", "m,n,m"))
def test_array_with_repeated_dims(dims):
    with pytest.raises(ValueError):
        validate_array(f"array[any, {dims}]")
