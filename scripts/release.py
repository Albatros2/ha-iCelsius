from __future__ import annotations

import json
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path


def next_version(today: date, tags: list[str]) -> str:
    base = f"{today.year}.{today.month}.{today.day}"
    if f"v{base}" not in tags:
        return base

    prefix = f"v{base}."
    suffixes = [
        int(tag.removeprefix(prefix))
        for tag in tags
        if tag.startswith(prefix) and tag.removeprefix(prefix).isdigit()
    ]
    return f"{base}.{max(suffixes, default=0) + 1}"


def main() -> None:
    repository = Path(__file__).resolve().parents[1]
    tag_output = subprocess.check_output(
        ["git", "-C", str(repository), "tag", "--list"], text=True
    )
    version = next_version(
        datetime.now(timezone.utc).date(), tag_output.splitlines()
    )

    manifest_path = repository / "custom_components/icelsius/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = version
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(version)


if __name__ == "__main__":
    main()