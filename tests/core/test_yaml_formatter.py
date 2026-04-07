from wireviz_studio.core.exceptions import YAMLParseError
from wireviz_studio.core.yaml_formatter import format_yaml_text


def test_format_yaml_text_normalizes_indentation_and_preserves_comments():
    source = """connectors:\n  X1:\n      # connector comment\n      type: DJ7091Y\n      pinlabels:\n      - 17\n      - 20\n"""

    formatted = format_yaml_text(source, indent_spaces=2)

    assert "# connector comment" in formatted
    assert "  X1:" in formatted
    assert "    type: DJ7091Y" in formatted
    assert "    pinlabels:" in formatted
    assert "      - 17" in formatted


def test_format_yaml_text_raises_yaml_parse_error_for_invalid_yaml():
    source = "connectors:\n\tX1:\n    type: bad\n"

    try:
        format_yaml_text(source, indent_spaces=2)
    except YAMLParseError as exc:
        assert "cannot start any token" in str(exc)
    else:
        raise AssertionError("Expected YAMLParseError")


def test_format_yaml_text_keeps_nested_connections_on_separate_lines():
    source = (
        "connections:\n"
        "  -\n"
        "    - X1: [7, 5, 6]\n"
        "    - W1: [1-3]\n"
        "    - X2: [1-3]\n"
    )

    formatted = format_yaml_text(source, indent_spaces=2)

    assert "connections:\n  -\n    - X1: [7, 5, 6]" in formatted
    assert "\n  -   - X1" not in formatted
    assert "\n      - X1" not in formatted