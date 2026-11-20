from __future__ import annotations

import json

import pytest

from pip._vendor.packaging import specifiers
from pip._vendor.packaging.markers import default_environment
from pip._vendor.packaging.requirements import Requirement

from pip._internal.utils.packaging import (
    check_requires_python,
    get_requirement,
    json_marker_environment,
)


@pytest.mark.parametrize(
    "version_info, requires_python, expected",
    [
        ((3, 6, 5), "== 3.6.4", False),
        ((3, 6, 5), "== 3.6.5", True),
        ((3, 6, 5), None, True),
    ],
)
def test_check_requires_python(
    version_info: tuple[int, int, int], requires_python: str | None, expected: bool
) -> None:
    actual = check_requires_python(requires_python, version_info)
    assert actual == expected


def test_check_requires_python__invalid() -> None:
    """
    Test an invalid Requires-Python value.
    """
    with pytest.raises(specifiers.InvalidSpecifier):
        check_requires_python("invalid", (3, 6, 5))


def test_get_or_create_caching() -> None:
    """test caching of get_or_create requirement"""
    teststr = "affinegap==1.10"
    from_helper = get_requirement(teststr)
    freshly_made = Requirement(teststr)

    # Requirement doesn't have an equality operator (yet) so test
    # equality of attribute for list of attributes
    for iattr in ["name", "url", "extras", "specifier", "marker"]:
        assert getattr(from_helper, iattr) == getattr(freshly_made, iattr)
    assert get_requirement(teststr) is not Requirement(teststr)
    assert get_requirement(teststr) is get_requirement(teststr)


def test_json_marker_environment() -> None:
    default = default_environment()
    environment = json_marker_environment()
    assert environment.keys() == default.keys()
    # PEP 780: sys_abi_info is a set, which is reported as a sorted list.
    sys_abi_info = environment.pop("sys_abi_info")
    assert isinstance(default["sys_abi_info"], frozenset)
    assert sys_abi_info == sorted(default["sys_abi_info"])
    assert {entry.split("::")[0] for entry in sys_abi_info} >= {
        "byteorder",
        "debug",
        "free_threaded",
        "pointer_bits",
    }
    # All other markers are passed through unchanged.
    assert all(environment[name] == default[name] for name in environment)
    assert json.loads(json.dumps(json_marker_environment()))["sys_abi_info"] == (
        sys_abi_info
    )
