#!/usr/bin/env python3
"""Check or install an official tgrep release in a user-owned directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile
import urllib.request
import zipfile


REPOSITORY = "microsoft/tgrep"
API_ROOT = f"https://api.github.com/repos/{REPOSITORY}/releases"
USER_AGENT = "local-search-tgrep-userspace-installer"


def request_bytes(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def release_metadata(version: str, metadata_file: str | None, timeout: int) -> dict[str, object]:
    if metadata_file:
        return json.loads(Path(metadata_file).read_text(encoding="utf-8"))
    endpoint = f"{API_ROOT}/latest" if version == "latest" else f"{API_ROOT}/tags/{version}"
    return json.loads(request_bytes(endpoint, timeout).decode("utf-8"))


def target_triple() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arm = machine in {"arm64", "aarch64"}
    x64 = machine in {"x86_64", "amd64"}
    if system == "darwin" and arm:
        return "aarch64-apple-darwin"
    if system == "darwin" and x64:
        return "x86_64-apple-darwin"
    if system == "linux" and arm:
        return "aarch64-unknown-linux-musl"
    if system == "linux" and x64:
        return "x86_64-unknown-linux-musl"
    if system == "windows" and arm:
        return "aarch64-pc-windows-msvc"
    if system == "windows" and x64:
        return "x86_64-pc-windows-msvc"
    raise SystemExit(f"unsupported tgrep release target: system={system} machine={machine}")


def default_install_dir() -> Path:
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA")
        return Path(local) / "Programs" / "tgrep" if local else Path.home() / ".local" / "bin"
    return Path.home() / ".local" / "bin"


def release_assets(metadata: dict[str, object]) -> list[dict[str, object]]:
    assets = metadata.get("assets")
    if not isinstance(assets, list):
        raise SystemExit("release metadata has no assets list")
    return [asset for asset in assets if isinstance(asset, dict)]


def select_asset(metadata: dict[str, object], target: str) -> tuple[dict[str, object], dict[str, object]]:
    binary = None
    checksums = None
    for asset in release_assets(metadata):
        name = str(asset.get("name", ""))
        if name == "checksums.txt":
            checksums = asset
        elif target in name and (name.endswith(".tar.gz") or name.endswith(".zip")):
            binary = asset
    if not binary or not checksums:
        raise SystemExit(f"release lacks binary/checksum asset for {target}")
    return binary, checksums


def semver(text: str | None) -> tuple[int, int, int] | None:
    if not text:
        return None
    match = re.search(r"(?:^|[^0-9])(\d+)\.(\d+)\.(\d+)(?:[^0-9]|$)", text)
    return tuple(int(value) for value in match.groups()) if match else None


def installed_record(override: str | None, install_dir: Path) -> dict[str, object]:
    executable = "tgrep.exe" if os.name == "nt" else "tgrep"
    found = shutil.which("tgrep")
    candidate = Path(found) if found else install_dir / executable
    text = override
    if text is None and candidate.is_file():
        completed = subprocess.run(
            [str(candidate), "--version"], capture_output=True, text=True, timeout=15
        )
        text = ((completed.stdout or "") + (completed.stderr or "")).strip()
    return {
        "path": str(candidate) if candidate.is_file() else None,
        "version_text": text,
        "version": semver(text),
    }


def report_for(
    metadata: dict[str, object], install_dir: Path, installed_version: str | None
) -> dict[str, object]:
    tag = str(metadata.get("tag_name", ""))
    latest = semver(tag)
    if latest is None:
        raise SystemExit(f"release tag is not semantic version: {tag!r}")
    target = target_triple()
    binary, checksums = select_asset(metadata, target)
    installed = installed_record(installed_version, install_dir)
    current = installed["version"]
    return {
        "repository": REPOSITORY,
        "target": target,
        "installed": {
            "path": installed["path"],
            "version": ".".join(map(str, current)) if current else None,
            "version_text": installed["version_text"],
        },
        "latest": {
            "tag": tag,
            "version": ".".join(map(str, latest)),
            "published_at": metadata.get("published_at"),
            "release_url": metadata.get("html_url"),
            "asset": binary.get("name"),
            "asset_url": binary.get("browser_download_url"),
            "checksums_url": checksums.get("browser_download_url"),
        },
        "update_available": current < latest if current else None,
        "install_dir": str(install_dir),
        "mutation": "none",
    }


def expected_checksum(checksums: str, asset_name: str) -> str:
    for line in checksums.splitlines():
        fields = line.strip().split()
        if len(fields) >= 2 and fields[-1].lstrip("*") == asset_name:
            return fields[0].lower()
    raise SystemExit(f"checksum not found for {asset_name}")


def extract_binary(archive: Path, destination: Path) -> None:
    wanted = "tgrep.exe" if os.name == "nt" else "tgrep"
    if archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as package:
            members = [name for name in package.namelist() if Path(name).name == wanted]
            if len(members) != 1:
                raise SystemExit(f"expected one {wanted} in archive, found {len(members)}")
            with package.open(members[0]) as source, destination.open("wb") as output:
                shutil.copyfileobj(source, output)
    else:
        with tarfile.open(archive, "r:gz") as package:
            members = [member for member in package.getmembers() if Path(member.name).name == wanted]
            if len(members) != 1 or not members[0].isfile():
                raise SystemExit(f"expected one regular {wanted} in archive")
            source = package.extractfile(members[0])
            if source is None:
                raise SystemExit(f"cannot extract {wanted}")
            with source, destination.open("wb") as output:
                shutil.copyfileobj(source, output)
    destination.chmod(destination.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def install(report: dict[str, object], timeout: int) -> dict[str, object]:
    latest = report["latest"]
    if not isinstance(latest, dict):
        raise SystemExit("invalid release report")
    asset_name = str(latest["asset"])
    asset_url = str(latest["asset_url"])
    checksums_url = str(latest["checksums_url"])
    install_dir = Path(str(report["install_dir"]))
    executable = "tgrep.exe" if os.name == "nt" else "tgrep"
    destination = install_dir / executable

    with tempfile.TemporaryDirectory(prefix="tgrep-userspace-install-") as name:
        temporary = Path(name)
        archive = temporary / asset_name
        archive.write_bytes(request_bytes(asset_url, timeout))
        checksum_text = request_bytes(checksums_url, timeout).decode("utf-8")
        expected = expected_checksum(checksum_text, asset_name)
        actual = hashlib.sha256(archive.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"checksum mismatch for {asset_name}: expected {expected}, got {actual}")

        install_dir.mkdir(parents=True, exist_ok=True)
        staged = install_dir / f".{executable}.new-{os.getpid()}"
        if staged.exists():
            raise SystemExit(f"staged install path already exists: {staged}")
        try:
            extract_binary(archive, staged)
            if destination.exists():
                installed = report.get("installed")
                current_text = (
                    str(installed.get("version") or "unknown")
                    if isinstance(installed, dict)
                    else "unknown"
                )
                backup = install_dir / f"{executable}.previous-{current_text}"
                suffix = 1
                while backup.exists():
                    backup = install_dir / f"{executable}.previous-{current_text}-{suffix}"
                    suffix += 1
                destination.replace(backup)
            staged.replace(destination)
        finally:
            if staged.exists():
                staged.unlink()

    completed = subprocess.run(
        [str(destination), "--version"], capture_output=True, text=True, timeout=15
    )
    if completed.returncode != 0:
        raise SystemExit(f"installed binary failed: {completed.stderr.strip()}")
    report["mutation"] = "installed"
    report["installed_after"] = {
        "path": str(destination),
        "version_text": completed.stdout.strip(),
        "archive_sha256": actual,
        "checksum_verified": True,
    }
    report["path_note"] = "Installer does not edit PATH or start a server."
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="check latest release without mutation")
    action.add_argument("--install", action="store_true", help="install/update after checksum verification")
    parser.add_argument("--version", default="latest", help="latest or a tag such as v1.0.4")
    parser.add_argument("--install-dir", type=Path, default=default_install_dir())
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--metadata-file", help=argparse.SUPPRESS)
    parser.add_argument("--installed-version", help=argparse.SUPPRESS)
    args = parser.parse_args()

    metadata = release_metadata(args.version, args.metadata_file, args.timeout)
    report = report_for(metadata, args.install_dir.resolve(), args.installed_version)
    if args.install:
        report = install(report, args.timeout)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
