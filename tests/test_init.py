"""Test smarter_types: the package's public names, and what importing it loads."""

import subprocess
import sys

import smarter_types


def test_public_names():
    """Every name in __all__ is importable from the top-level package."""
    for name in smarter_types.__all__:
        assert hasattr(smarter_types, name), name


def test_import_loads_no_framework():
    """Importing the package loads neither Django nor Pydantic, so that any project can depend on it."""
    code = (
        "import sys, smarter_types; "
        "loaded = [m for m in ('django', 'pydantic') if m in sys.modules]; "
        "print(','.join(loaded))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == ""
