"""GraphViz binary resolution for WireViz Studio.

Resolution order follows Phase 2 plan:
1) bundled binary
2) system-installed binary
3) error
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from wireviz_studio.graphviz_manager.bundled import configure_bundled_dot
from wireviz_studio.graphviz_manager.detect import configure_system_dot, dot_version


def resolve_dot_binary(app_root: Optional[Path] = None) -> Path:
    """Resolve and configure GraphViz dot executable using bundled/system fallback."""
    bundled_dot = configure_bundled_dot(app_root=app_root)
    if bundled_dot:
        return bundled_dot

    system_dot = configure_system_dot()
    if system_dot:
        return system_dot

    raise FileNotFoundError(
        "No GraphViz dot executable found. Checked bundled_graphviz first, then system PATH/common locations."
    )


def resolve_dot_version(app_root: Optional[Path] = None) -> Optional[str]:
    """Resolve dot and return version information when available."""
    dot_path = resolve_dot_binary(app_root=app_root)
    return dot_version(dot_path)
