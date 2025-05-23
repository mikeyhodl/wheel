from __future__ import annotations

from pathlib import Path

import pytest

from wheel._metadata import pkginfo_to_metadata


def test_pkginfo_to_metadata(tmp_path: Path) -> None:
    expected_metadata = [
        ("Metadata-Version", "2.1"),
        ("Name", "spam"),
        ("Version", "0.1"),
        ("Requires-Dist", "pip@ https://github.com/pypa/pip/archive/1.3.1.zip"),
        ("Requires-Dist", 'pywin32; sys_platform == "win32"'),
        ("Requires-Dist", 'foo@ http://host/foo.zip ; sys_platform == "win32"'),
        ("Provides-Extra", "signatures"),
        (
            "Requires-Dist",
            'pyxdg; sys_platform != "win32" and extra == "signatures"',
        ),
        ("Provides-Extra", "empty_extra"),
        ("Provides-Extra", "extra"),
        ("Requires-Dist", 'bar@ http://host/bar.zip ; extra == "extra"'),
        ("Provides-Extra", "faster-signatures"),
        ("Requires-Dist", 'ed25519ll; extra == "faster-signatures"'),
        ("Provides-Extra", "rest"),
        ("Requires-Dist", 'docutils>=0.8; extra == "rest"'),
        ("Requires-Dist", 'keyring; extra == "signatures"'),
        ("Requires-Dist", 'keyrings.alt; extra == "signatures"'),
        ("Provides-Extra", "test"),
        ("Requires-Dist", 'pytest>=3.0.0; extra == "test"'),
        ("Requires-Dist", 'pytest-cov; extra == "test"'),
    ]

    pkg_info = tmp_path.joinpath("PKG-INFO")
    pkg_info.write_text(
        """\
Metadata-Version: 0.0
Name: spam
Version: 0.1
Provides-Extra: empty+extra
Provides-Extra: test
Provides-Extra: reST
Provides-Extra: signatures
Provides-Extra: Signatures
Provides-Extra: faster-signatures""",
        encoding="utf-8",
    )

    egg_info_dir = tmp_path.joinpath("test.egg-info")
    egg_info_dir.mkdir(exist_ok=True)
    egg_info_dir.joinpath("requires.txt").write_text(
        """\
pip@https://github.com/pypa/pip/archive/1.3.1.zip

[extra]
bar @ http://host/bar.zip

[empty+extra]

[:sys_platform=="win32"]
pywin32
foo @http://host/foo.zip

[faster-signatures]
ed25519ll

[reST]
docutils>=0.8

[signatures]
keyring
keyrings.alt

[Signatures:sys_platform!="win32"]
pyxdg

[test]
pytest>=3.0.0
pytest-cov""",
        encoding="utf-8",
    )

    message = pkginfo_to_metadata(
        egg_info_path=str(egg_info_dir), pkginfo_path=str(pkg_info)
    )
    assert message.items() == expected_metadata


def test_metadata_deprecated() -> None:
    with pytest.warns(DeprecationWarning, match="has been made private"):
        from wheel import metadata

        assert hasattr(metadata, "pkginfo_to_metadata")
