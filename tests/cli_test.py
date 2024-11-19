import pytest
from bmi_map._main import main


def test_help():
    with pytest.raises(SystemExit):
        main(["--help"])


def test_version():
    with pytest.raises(SystemExit):
        main(["--version"])
