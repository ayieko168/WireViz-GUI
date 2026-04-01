"""GraphViz download workflow utilities (v2 foundation)."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path


def sha256sum(file_path: Path) -> str:
	"""Compute SHA256 checksum for a file."""
	digest = hashlib.sha256()
	with file_path.open("rb") as file_handle:
		for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
			digest.update(chunk)
	return digest.hexdigest()


def download_file(url: str, destination: Path) -> Path:
	"""Download URL to destination path."""
	destination.parent.mkdir(parents=True, exist_ok=True)
	with urllib.request.urlopen(url) as response, destination.open("wb") as output_file:
		output_file.write(response.read())
	return destination


def verify_sha256(file_path: Path, expected_sha256: str) -> bool:
	"""Verify file checksum against expected SHA256 hex string."""
	return sha256sum(file_path).lower() == expected_sha256.lower()
