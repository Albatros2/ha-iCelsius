from __future__ import annotations

import json
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path


def next_version(
    today: date, tags: list[str], current_version: str | None = None
) -> str:
    base = f"{today.year}.{today.month}.{today.day}"
    prefix = f"{base}."
    suffixes = [
        int(tag.removeprefix(f"v{prefix}"))
        for tag in tags
        if tag.startswith(f"v{prefix}")
        and tag.removeprefix(f"v{prefix}").isdigit()
    ]
    current_suffix = (
        current_version.removeprefix(prefix)
        if current_version and current_version.startswith(prefix)
        else None
    )
    if current_suffix and current_suffix.isdigit():
        suffixes.append(int(current_suffix))

    has_base_version = (
        f"v{base}" in tags or current_version == base or bool(suffixes)
    )
    if not has_base_version:
        return base
    return f"{base}.{max(suffixes, default=0) + 1}"


def main() -> None:
    repository = Path(__file__).resolve().parents[1]
    tag_output = subprocess.check_output(
        ["git", "-C", str(repository), "tag", "--list"], text=True
    )
    manifest_path = repository / "custom_components/icelsius/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    version = next_version(
        datetime.now(timezone.utc).date(),
        tag_output.splitlines(),
        manifest.get("version"),
    )
    manifest["version"] = version
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(version)


if __name__ == "__main__":
    main()