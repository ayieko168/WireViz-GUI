import pytest

from wireviz_studio.core.exceptions import GraphVizNotFoundError, RenderError
from wireviz_studio.core.harness import Harness
from wireviz_studio.core.models import Metadata, Options, Tweak
from wireviz_studio.core.parser import parse_yaml


def _make_harness() -> Harness:
    return Harness(metadata=Metadata(), options=Options(), tweak=Tweak())


def test_bom_is_cached(monkeypatch):
    harness = _make_harness()
    calls = {"count": 0}

    def fake_generate_bom(_):
        calls["count"] += 1
        return [{"id": 1, "description": "stub"}]

    monkeypatch.setattr("wireviz_studio.core.harness.generate_bom", fake_generate_bom)

    first = harness.bom()
    second = harness.bom()

    assert first == second
    assert calls["count"] == 1


def test_render_svg_maps_missing_dot_to_graphviz_error(monkeypatch):
    harness = _make_harness()

    def fail_resolve():
        raise FileNotFoundError("dot not found")

    monkeypatch.setattr("wireviz_studio.core.harness.resolve_dot_binary", fail_resolve)

    with pytest.raises(GraphVizNotFoundError):
        harness.render_svg()


def test_render_svg_maps_unexpected_failures_to_render_error(monkeypatch):
    harness = _make_harness()

    monkeypatch.setattr("wireviz_studio.core.harness.resolve_dot_binary", lambda: None)

    def broken_svg(_self):
        raise RuntimeError("render pipeline failed")

    monkeypatch.setattr(Harness, "svg", property(broken_svg))

    with pytest.raises(RenderError):
        harness.render_svg()


def test_create_graph_supports_numeric_pinlabels_and_wirelabels():
    harness = parse_yaml(
        {
            "connectors": {
                "X1": {
                    "type": "DJ7091Y",
                    "subtype": "female",
                    "pinlabels": [17, 20, 19, 18, 16, 15, 12, 14, 13],
                },
                "X2": {
                    "pincount": 3,
                },
            },
            "cables": {
                "W1": {
                    "wirecount": 3,
                    "wirelabels": [101, 102, 103],
                    "length": 1,
                },
            },
            "connections": [
                [
                    {"X1": [7, 5, 6]},
                    {"W1": ["1-3"]},
                    {"X2": [1, 2, 3]},
                ]
            ],
        }
    )

    graph = harness.create_graph()
    body = "\n".join(graph.body)

    assert "X1:7:12" in body
    assert "1:101" in body
