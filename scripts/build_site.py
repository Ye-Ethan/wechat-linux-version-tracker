#!/usr/bin/env python3
"""Build the gh-pages output (latest.json) for the version tracker.

Reads the detected version from argv[1]. Optionally reads the previously
published latest.json (argv[2]) to preserve the original `updateTime` when the
version has not changed.

Writes the result to argv[3] (defaults to public/latest.json).
"""
import datetime
import json
import os
import sys


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print("usage: build_site.py <version> [prev.json] [out.json]", file=sys.stderr)
        return 1

    version = sys.argv[1].strip()
    prev_path = sys.argv[2] if len(sys.argv) > 2 else ""
    out_path = sys.argv[3] if len(sys.argv) > 3 else "public/latest.json"

    prev_version = ""
    prev_update = ""
    if prev_path and os.path.isfile(prev_path):
        try:
            with open(prev_path, "r", encoding="utf-8") as f:
                prev = json.load(f)
            prev_version = str(prev.get("currentVersion", ""))
            prev_update = str(prev.get("updateTime", ""))
        except (ValueError, OSError):
            pass

    if version == prev_version and prev_update:
        update_time = prev_update
    else:
        update_time = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {"currentVersion": version, "updateTime": update_time},
            f,
            ensure_ascii=False,
        )
        f.write("\n")

    print(f"currentVersion={version} updateTime={update_time}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
