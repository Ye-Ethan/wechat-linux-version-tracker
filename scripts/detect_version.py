#!/usr/bin/env python3
"""Detect the version of the WeChat Linux client.

The official .deb package is a Unix `ar` archive whose second member is a
`control.tar.*` file containing the Debian `control` metadata. Instead of
downloading the whole ~200MB package, this script uses HTTP Range requests to
fetch only the ar headers and the small `control` member (a few KB), then
extracts the `Version:` field.

Usage:
    python3 detect_version.py            # prints the version to stdout
"""
import io
import re
import subprocess
import sys
import tempfile
import urllib.request

URL = "https://dldir1v6.qq.com/weixin/Universal/Linux/WeChatLinux_x86_64.deb"


def fetch_range(url: str, start: int, end: int) -> bytes:
    """Fetch bytes [start, end] (inclusive) via an HTTP Range request."""
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def find_control_member(url: str):
    """Parse the ar archive headers and return (data_start, size) of control.tar.*"""
    head = fetch_range(url, 0, 4095)
    if head[:8] != b"!<arch>\n":
        raise RuntimeError("Not a valid ar/deb archive")
    pos = 8
    while pos + 60 <= len(head):
        header = head[pos:pos + 60]
        name = header[0:16].decode(errors="replace").strip().rstrip("/")
        size = int(header[48:58].decode().strip())
        data_start = pos + 60
        if name.startswith("control.tar"):
            return data_start, size
        # ar members are 2-byte aligned
        pos = data_start + size + (size % 2)
    raise RuntimeError("control member not found in ar headers")


def extract_version(control_blob: bytes) -> str:
    """Extract the Version field from a compressed control.tar.* blob."""
    with tempfile.TemporaryDirectory() as tmp:
        archive = f"{tmp}/control.tar"
        with open(archive, "wb") as f:
            f.write(control_blob)
        # tar auto-detects the compression (xz/gz/zstd) on modern systems.
        subprocess.run(
            ["tar", "-xf", archive, "-C", tmp],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        with open(f"{tmp}/control", "r", encoding="utf-8") as f:
            content = f.read()
    match = re.search(r"^Version:\s*(.+)$", content, re.MULTILINE)
    if not match:
        raise RuntimeError("Version field not found in control file")
    return match.group(1).strip()


def main() -> int:
    data_start, size = find_control_member(URL)
    blob = fetch_range(URL, data_start, data_start + size - 1)
    if len(blob) != size:
        raise RuntimeError(
            f"Range request not honored (got {len(blob)} bytes, expected {size})"
        )
    version = extract_version(blob)
    print(version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
