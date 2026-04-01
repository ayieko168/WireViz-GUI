from pathlib import Path

from wireviz_studio.graphviz_manager.bundled import find_bundled_dot
from wireviz_studio.graphviz_manager.detect import verify_dot


def test_find_bundled_dot_none_for_missing_root(tmp_path):
    fake_root = tmp_path / "no-bundle-here"
    fake_root.mkdir(parents=True)

    dot_path = find_bundled_dot(app_root=fake_root)

    assert dot_path is None


def test_verify_dot_false_for_missing_file(tmp_path):
    missing_dot = tmp_path / "dot_missing.exe"

    assert verify_dot(Path(missing_dot)) is False