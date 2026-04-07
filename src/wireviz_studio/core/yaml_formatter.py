"""Formatting helpers for user-authored YAML documents."""

from __future__ import annotations

from io import StringIO

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from wireviz_studio.core.exceptions import YAMLParseError


def format_yaml_text(text: str, indent_spaces: int = 2) -> str:
    """Normalize YAML indentation while preserving comments and key order."""
    if not text.strip():
        return text

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    yaml.indent(
        mapping=indent_spaces,
        sequence=indent_spaces,
        offset=indent_spaces,
    )
    yaml.compact(seq_seq=False, seq_map=True)

    try:
        data = yaml.load(text)
    except YAMLError as exc:
        raise YAMLParseError(str(exc)) from exc

    buffer = StringIO()
    yaml.dump(data, buffer)
    return buffer.getvalue()