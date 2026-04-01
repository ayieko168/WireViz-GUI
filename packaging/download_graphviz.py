"""Download and verify GraphViz archive for CI packaging jobs.

Usage:
  ./venv/Scripts/python.exe packaging/download_graphviz.py \
    --url <archive-url> \
    --sha256 <expected-checksum> \
    --output bundled_graphviz/windows/graphviz.zip
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from wireviz_studio.graphviz_manager.download import download_file, verify_sha256


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and verify GraphViz archive")
    parser.add_argument("--url", required=True, help="GraphViz archive URL")
    parser.add_argument("--sha256", required=True, help="Expected SHA256 checksum")
    parser.add_argument("--output", required=True, help="Destination archive path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    destination = Path(args.output)

    print(f"Downloading: {args.url}")
    print(f"Destination: {destination}")
    download_file(args.url, destination)

    print("Verifying SHA256...")
    if not verify_sha256(destination, args.sha256):
        print("Checksum verification failed.")
        return 1

    print("Checksum verification succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())