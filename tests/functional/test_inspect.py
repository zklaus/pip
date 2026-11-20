import json

import pytest

from tests.lib import PipTestEnvironment, ScriptFactory, TestData


@pytest.fixture
def simple_script(
    tmpdir_factory: pytest.TempPathFactory,
    script_factory: ScriptFactory,
    shared_data: TestData,
) -> PipTestEnvironment:
    tmpdir = tmpdir_factory.mktemp("pip_test_package")
    script = script_factory(tmpdir.joinpath("workspace"))
    script.pip(
        "install",
        "-f",
        shared_data.find_links,
        "--no-index",
        "simplewheel==1.0",
    )
    return script


def test_inspect_basic(simple_script: PipTestEnvironment) -> None:
    """
    Test default behavior of inspect command.
    """
    result = simple_script.pip("inspect")
    report = json.loads(result.stdout)
    installed_by_name = {i["metadata"]["name"]: i for i in report["installed"]}
    # Coverage is only installed if test coverage is being collected.
    installed_by_name.pop("coverage", None)
    assert len(installed_by_name) == 3
    assert installed_by_name.keys() == {
        "pip",
        "setuptools",
        "simplewheel",
    }
    assert installed_by_name["simplewheel"]["metadata"]["version"] == "1.0"
    assert installed_by_name["simplewheel"]["requested"] is True
    assert installed_by_name["simplewheel"]["installer"] == "pip"
    assert "environment" in report
    # PEP 780: the only marker that is not a string is a sorted array of strings.
    sys_abi_info = report["environment"]["sys_abi_info"]
    assert sys_abi_info == sorted(sys_abi_info)
    assert {entry.split("::")[0] for entry in sys_abi_info} >= {
        "byteorder",
        "debug",
        "free_threaded",
        "pointer_bits",
    }


def test_inspect_rejects_extra_argument(
    simple_script: PipTestEnvironment,
) -> None:
    result = simple_script.pip("inspect", "unexpected_arg", expect_error=True)
    assert "ERROR: Too many arguments" in result.stderr
    assert result.returncode != 0
