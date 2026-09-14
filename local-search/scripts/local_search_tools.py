#!/usr/bin/env python3
"""Cross-platform diagnostics and fallbacks for the local-search ladder."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


TOOLS = ("rg", "tgrep", "rga", "pdftotext", "pandoc", "node", "npm", "bun", "qmd")

QMD_CAPABILITY_MARKERS = {
    "batch_get": "qmd multi-get <pattern>",
    "bounded_get": "qmd get <file>[:from[:count]]",
    "runtime_skill": "qmd skills list/get/path",
    "mcp": "qmd mcp",
    "benchmark": "qmd bench <fixture.json>",
    "project_local_index": "qmd init",
    "named_index": "--index <name>",
    "structured_query": "lex:..\\nvec:",
    "score_explain": "--explain",
    "full_path": "--full-path",
    "ast_chunking": "--chunk-strategy <auto|regex>",
}


def unique_existing(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    output: list[Path] = []
    for path in paths:
        try:
            key = str(path.resolve()).lower() if os.name == "nt" else str(path.resolve())
        except OSError:
            continue
        if path.exists() and key not in seen:
            output.append(path)
            seen.add(key)
    return output


def candidates(name: str) -> list[Path]:
    paths: list[Path] = []
    found = shutil.which(name)
    if found:
        paths.append(Path(found))

    home = Path.home()
    if os.name == "nt":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        roaming = Path(os.environ.get("APPDATA", ""))
        program_files = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
        suffix = ".cmd" if name in {"qmd", "npm"} else ".exe"
        paths.extend(
            [
                roaming / "npm" / f"{name}{suffix}",
                home / "scoop" / "shims" / f"{name}{suffix}",
                Path("C:/ProgramData/chocolatey/bin") / f"{name}{suffix}",
                program_files / "nodejs" / f"{name}{suffix}",
            ]
        )
        paths.extend(
            (local / "Microsoft/WinGet/Packages").glob(f"**/{name}{suffix}")
        )
    else:
        for prefix in (
            home / ".local/bin",
            home / ".npm-global/bin",
            Path("/opt/homebrew/bin"),
            Path("/usr/local/bin"),
            Path("/usr/bin"),
        ):
            paths.append(prefix / name)
        for pattern in (
            home / ".nvm/versions/node",
            home / ".asdf/installs/nodejs",
            home / ".local/share/mise/installs/node",
        ):
            paths.extend(pattern.glob(f"*/bin/{name}"))
    return unique_existing(paths)


def command_env() -> dict[str, str]:
    env = os.environ.copy()
    node_hits = candidates("node")
    if node_hits:
        env["PATH"] = str(node_hits[0].parent) + os.pathsep + env.get("PATH", "")
    return env


def version(path: Path) -> str:
    name = path.stem.lower()
    flag = "-v" if name in {"node", "pdftotext"} else "--version"
    try:
        completed = subprocess.run(
            [str(path), flag],
            capture_output=True,
            text=True,
            timeout=15,
            env=command_env(),
        )
        lines = ((completed.stdout or "") + (completed.stderr or "")).strip().splitlines()
        return lines[0] if lines else f"exit={completed.returncode}"
    except Exception as exc:
        return f"unusable: {exc}"


def major_version(text: str) -> int | None:
    match = re.search(r"(?:^|[^0-9])v?([0-9]+)(?:\.|$)", text)
    return int(match.group(1)) if match else None


def run_text(command: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=command_env(),
    )


def inspect_qmd(timeout: int = 30) -> dict[str, object]:
    hits = candidates("qmd")
    if not hits:
        return {
            "status": "MISSING",
            "path": None,
            "version": None,
            "capabilities": {name: False for name in QMD_CAPABILITY_MARKERS},
        }

    path = hits[0]
    try:
        completed = run_text([str(path), "--help"], timeout)
        help_text = (completed.stdout or "") + (completed.stderr or "")
        status = "OK" if completed.returncode == 0 else "UNUSABLE"
        error = None if completed.returncode == 0 else f"help exit={completed.returncode}"
    except Exception as exc:
        help_text = ""
        status = "UNUSABLE"
        error = str(exc)
    record: dict[str, object] = {
        "status": status,
        "path": str(path),
        "version": version(path),
        "capabilities": {
            name: marker in help_text for name, marker in QMD_CAPABILITY_MARKERS.items()
        },
    }
    if error:
        record["error"] = error
    return record


def qmd_capabilities(args: argparse.Namespace) -> int:
    record = inspect_qmd(args.timeout)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record["status"] == "OK" else 1


def pdftotext_flavor(path: Path) -> str:
    try:
        completed = subprocess.run(
            [str(path), "-v"], capture_output=True, text=True, timeout=15
        )
        text = ((completed.stdout or "") + (completed.stderr or "")).lower()
    except Exception:
        return "unknown"
    if "poppler" in text:
        return "poppler"
    if "glyph & cog" in text or "xpdf" in text:
        return "xpdf"
    return "unknown"


def doctor(args: argparse.Namespace) -> int:
    records: list[dict[str, object]] = []
    for name in TOOLS:
        hits = candidates(name)
        resolved = hits[0] if hits else None
        record: dict[str, object] = {
            "tool": name,
            "status": "OK" if resolved else "MISSING",
            "path": str(resolved) if resolved else None,
            "version": version(resolved) if resolved else None,
        }
        if name == "node" and resolved:
            major = major_version(str(record["version"]))
            if major is not None and major < 22:
                record["status"] = "OUTDATED"
                record["note"] = "QMD requires Node.js 22+"
        records.append(record)

    qmd_record = inspect_qmd(args.timeout)
    records.append(
        {
            "tool": "qmd-capabilities",
            "status": qmd_record["status"],
            "version": qmd_record["version"],
            "capabilities": qmd_record["capabilities"],
            "note": qmd_record.get("error"),
        }
    )

    pdf_hits = candidates("pdftotext")
    records.append(
        {
            "tool": "rga-pdf-adapter",
            "status": "CHECK" if candidates("rga") else "UNAVAILABLE",
            "pdftotext_flavor": pdftotext_flavor(pdf_hits[0]) if pdf_hits else "absent",
            "note": "Run rga-smoke with a known real text-layer PDF.",
        }
    )
    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        for record in records:
            path = f" [{record['path']}]" if record.get("path") else ""
            detail = record.get("version") or record.get("note") or ""
            print(f"{record['status']:<11} {record['tool']:<18} {detail}{path}")
            if record["tool"] == "qmd-capabilities" and record["status"] == "OK":
                capabilities = record["capabilities"]
                enabled = ", ".join(name for name, value in capabilities.items() if value)
                print(f"{'':<31} enabled: {enabled or 'none detected'}")
        print()
        print("Baseline usable." if candidates("rg") else "Baseline NOT usable: install rg.")
        if not candidates("rga"):
            print("Binary tier unavailable: use text search and pdfgrep until rga is installed.")
        if not candidates("tgrep"):
            print("Indexed-regex tier unavailable: rg remains the exact-search baseline.")
        if not candidates("qmd"):
            print("Ranked/semantic tiers unavailable: exact and binary tiers remain usable.")
    return 0 if candidates("rg") else 1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_excluded(relative: Path, patterns: list[str]) -> bool:
    posix = relative.as_posix()
    return any(fnmatch.fnmatch(posix, pattern) for pattern in patterns)


def write_staged_corpus(
    root: Path,
    output: Path,
    include: list[str],
    exclude: list[str],
    replace: bool,
) -> int:
    if root == output or root in output.parents or output in root.parents:
        raise SystemExit("output must be outside and not an ancestor of the project")
    if output.exists() and not replace:
        raise SystemExit(f"output exists: {output}; pass --replace deliberately")

    selected: dict[Path, Path] = {}
    for pattern in include:
        for source in root.glob(pattern):
            if not source.is_file() or source.suffix.lower() != ".md":
                continue
            relative = source.relative_to(root)
            if not is_excluded(relative, exclude):
                selected[relative] = source

    temporary = output.parent / f".{output.name}.stage-{os.getpid()}"
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir(parents=True)
    manifest_files: list[dict[str, object]] = []
    try:
        for relative, source in sorted(selected.items()):
            destination = temporary / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            manifest_files.append(
                {
                    "path": relative.as_posix(),
                    "sha256": sha256(source),
                    "bytes": source.stat().st_size,
                }
            )
        manifest = {
            "source_root": str(root),
            "count": len(manifest_files),
            "include": include,
            "exclude": exclude,
            "files": manifest_files,
        }
        (temporary / "_local_search_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if output.exists():
            shutil.rmtree(output)
        temporary.rename(output)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    print(f"STAGED count={len(manifest_files)} output={output}")
    return 0


def stage(args: argparse.Namespace) -> int:
    return write_staged_corpus(
        Path(args.project).resolve(),
        Path(args.output).resolve(),
        args.include,
        args.exclude,
        args.replace,
    )


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise SystemExit("collection name must contain letters or digits")
    return slug


def init_policy(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    output = Path(args.output).resolve()
    if not root.is_dir():
        raise SystemExit(f"project directory not found: {root}")
    if output.exists() and not args.force:
        raise SystemExit(f"policy exists: {output}; pass --force deliberately")
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise SystemExit("policy output must be inside the project") from exc

    always_candidates = (
        "AGENTS.md",
        "CLAUDE.md",
        "README.md",
        "STATE.md",
        "PROJECT_OPERATIONS.md",
        "PROJECT_WIKI.md",
    )
    always_context = [name for name in always_candidates if (root / name).is_file()]
    include_candidates = (
        ("docs", "docs/**/*.md"),
        ("planning", "planning/**/*.md"),
        ("sources", "sources/**/*.md"),
        ("notes", "notes/**/*.md"),
        ("references", "references/**/*.md"),
        ("research", "research/**/*.md"),
        ("lecture_notes", "lecture_notes/**/*.md"),
        ("src", "src/**/*.md"),
    )
    include = [pattern for directory, pattern in include_candidates if (root / directory).is_dir()]
    include.extend(always_context)
    if not include:
        include = ["**/*.md"]

    policy = {
        "schema_version": 1,
        "project_root": ".",
        "collection_name": slugify(args.name),
        "context": (
            f"Canonical documents staged from {root.name}; search results are locators "
            "and must be reopened at the source."
        ),
        "always_context": always_context,
        "include": include,
        "exclude": [
            ".git/**",
            ".claude/**",
            ".codex/**",
            "**/__pycache__/**",
            "**/.cache/**",
            "**/node_modules/**",
            "generated/**",
            "**/generated/**",
            "build/**",
            "**/build/**",
            "dist/**",
            "**/dist/**",
            "archive/**",
            "**/archive/**",
            "tmp/**",
            "**/tmp/**",
            "temp/**",
            "**/temp/**",
            "logs/**",
            "**/logs/**",
        ],
        "restricted": [
            "credentials and secrets",
            "personal data",
            "answer keys and hidden evaluation truth",
        ],
        "qmd": {
            "recommended": True,
            "required": False,
            "index_location": "per-machine",
            "activate_when": [
                "ranked retrieval is repeatedly useful",
                "the correct file is often unknown",
                "cross-language or semantic retrieval matters",
            ],
        },
        "tgrep": {
            "recommended": False,
            "required": False,
            "index_location": "per-machine-outside-project",
            "activate_when": [
                "the same large codebase receives repeated regex searches",
                "measured rg latency justifies persistent index cost",
            ],
        },
        "review_required": True,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(policy, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"POLICY_CREATED {output}")
    print("Review include/exclude/restricted before stage-policy.")
    print("QMD recommended=true required=false; rg remains the baseline.")
    return 0


def stage_policy(args: argparse.Namespace) -> int:
    policy_path = Path(args.policy).resolve()
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    required = {"schema_version", "project_root", "include", "exclude", "qmd"}
    missing = required - set(policy)
    if missing:
        raise SystemExit(f"policy missing fields: {', '.join(sorted(missing))}")
    root_value = Path(policy["project_root"])
    root = root_value.resolve() if root_value.is_absolute() else (policy_path.parent / root_value).resolve()
    return write_staged_corpus(
        root,
        Path(args.output).resolve(),
        list(policy["include"]),
        list(policy["exclude"]),
        args.replace,
    )


def pdfgrep(args: argparse.Namespace) -> int:
    hits = candidates("pdftotext")
    if not hits:
        raise SystemExit("pdftotext not found; install Poppler or Xpdf")
    flags = 0 if args.case_sensitive else re.IGNORECASE
    pattern = re.compile(args.pattern, flags)
    pdfs: list[Path] = []
    for raw in args.path:
        target = Path(raw)
        if target.is_file() and target.suffix.lower() == ".pdf":
            pdfs.append(target)
        elif target.is_dir():
            pdfs.extend(sorted(target.rglob("*.pdf")))
    matched = 0
    for pdf in pdfs:
        try:
            completed = subprocess.run(
                [str(hits[0]), str(pdf), "-"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=args.timeout,
            )
        except Exception as exc:
            print(f"SKIP {pdf}: {exc}", file=sys.stderr)
            continue
        lines = [
            (number, line.strip())
            for number, line in enumerate(completed.stdout.splitlines(), start=1)
            if pattern.search(line)
        ]
        if lines:
            matched += 1
            print(f"== {pdf} ==")
            for number, line in lines[: args.max_lines]:
                print(f"{number}: {line}")
    print(f"PDFGREP matched={matched} total={len(pdfs)} pattern={args.pattern!r}")
    return 0


def rga_smoke(args: argparse.Namespace) -> int:
    hits = candidates("rga")
    if not hits:
        raise SystemExit("rga not found")
    completed = subprocess.run(
        [
            str(hits[0]),
            "--rga-no-cache",
            "-n",
            "-m",
            str(args.max_lines),
            args.term,
            str(Path(args.pdf)),
        ],
        text=True,
        capture_output=True,
        timeout=args.timeout,
        env=command_env(),
    )
    print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")
    if completed.returncode not in (0, 1):
        return completed.returncode
    print(f"RGA_SMOKE {'PASS' if completed.returncode == 0 else 'ZERO_RESULT'}")
    return 0


def tgrep_smoke(args: argparse.Namespace) -> int:
    """Compare indexed tgrep output with live rg on a controlled text corpus."""
    tgrep_hits = candidates("tgrep")
    rg_hits = candidates("rg")
    if not tgrep_hits:
        raise SystemExit("tgrep not found")
    if not rg_hits:
        raise SystemExit("rg not found; cannot establish equivalence")

    with tempfile.TemporaryDirectory(prefix="local-search-tgrep-smoke-") as name:
        root = Path(name)
        corpus = root / "corpus"
        index = root / "index"
        corpus.mkdir()
        (corpus / "alpha.py").write_text(
            "def alpha():\n    return 'needle-alpha'\n", encoding="utf-8"
        )
        (corpus / "beta.rs").write_text(
            "fn beta() { println!(\"needle-beta\"); }\n", encoding="utf-8"
        )
        (corpus / "zero.md").write_text("no target here\n", encoding="utf-8")

        built = run_text(
            [str(tgrep_hits[0]), "index", str(corpus), "--index-path", str(index)],
            args.timeout,
        )
        if built.returncode != 0:
            print(built.stdout, end="")
            print(built.stderr, file=sys.stderr, end="")
            return built.returncode

        pattern = r"needle-(alpha|beta)"
        shared_flags = ["--no-heading", "--color", "never", "-n"]
        rg_result = run_text([str(rg_hits[0]), *shared_flags, pattern, str(corpus)], args.timeout)
        tgrep_result = run_text(
            [
                str(tgrep_hits[0]),
                *shared_flags,
                "--index-path",
                str(index),
                pattern,
                str(corpus),
            ],
            args.timeout,
        )
        if rg_result.returncode != 0 or tgrep_result.returncode != 0:
            print(rg_result.stderr, file=sys.stderr, end="")
            print(tgrep_result.stderr, file=sys.stderr, end="")
            return rg_result.returncode or tgrep_result.returncode

        rg_lines = sorted(line for line in rg_result.stdout.splitlines() if line)
        tgrep_lines = sorted(line for line in tgrep_result.stdout.splitlines() if line)
        if rg_lines != tgrep_lines:
            print(json.dumps({"rg": rg_lines, "tgrep": tgrep_lines}, indent=2))
            return 1
        if any(path.name.startswith(".tgrep") for path in corpus.iterdir()):
            print("tgrep smoke failed: index material appeared inside corpus", file=sys.stderr)
            return 1

        report = {
            "status": "PASS",
            "tgrep_version": version(tgrep_hits[0]),
            "matches": len(tgrep_lines),
            "index_outside_corpus": True,
            "non_claim": "Equivalence on this fixture does not prove a project index is fresh or complete.",
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def qmd_smoke(args: argparse.Namespace) -> int:
    hits = candidates("qmd")
    if not hits:
        raise SystemExit("qmd not found")
    prefix = [str(hits[0])]
    if args.index:
        prefix.extend(["--index", args.index])
    commands = [prefix + ["collection", "list"]]
    if args.query:
        command = prefix + [
            "search",
            args.query,
            "-n",
            str(args.limit),
            "--format",
            "json",
        ]
        if args.collection:
            command.extend(["-c", args.collection])
        commands.append(command)
    for command in commands:
        completed = subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=args.timeout,
            env=command_env(),
        )
        print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")
        if completed.returncode != 0:
            return completed.returncode
    print("QMD_SMOKE PASS")
    return 0


def classify_claim_context(path: Path, lines: list[str], line_number: int) -> list[str]:
    start = max(0, line_number - 4)
    end = min(len(lines), line_number + 3)
    context = " ".join(lines[start:end]).lower()
    name = path.name.lower()
    roles: list[str] = []
    if re.search(r"definition|criteria|meaning|means|termination|contract", context):
        roles.append("definition")
    if name in {"state.md", "project_hub.md", "live_monitor.md"} or re.search(
        r"current|living|disposition|frontier", context
    ):
        roles.append("current")
    if re.search(r"terminal|finalizer|validator|immutable|completed", context):
        roles.append("terminal")
    if re.search(r"correction|superseded|legacy|historical|history|archive", context):
        roles.append("history")
    return roles or ["usage"]


def claim_bundle(args: argparse.Namespace) -> int:
    """Collect bounded definition/current/terminal/history contexts for one term."""
    root = Path(args.project).resolve()
    patterns = args.include or ["**/*.md"]
    excludes = args.exclude or [
        ".git/**",
        "**/.git/**",
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/generated/**",
    ]
    selected: dict[Path, Path] = {}
    for pattern in patterns:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if not is_excluded(relative, excludes):
                selected[relative] = path

    matcher = re.compile(re.escape(args.term), 0 if args.case_sensitive else re.IGNORECASE)
    hits: list[dict[str, object]] = []
    for relative, path in sorted(selected.items()):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for index, line in enumerate(lines, 1):
            if not matcher.search(line):
                continue
            start = max(1, index - args.context)
            end = min(len(lines), index + args.context)
            excerpt = [
                {"line": number, "text": lines[number - 1]}
                for number in range(start, end + 1)
            ]
            hits.append(
                {
                    "path": relative.as_posix(),
                    "line": index,
                    "roles": classify_claim_context(relative, lines, index),
                    "excerpt": excerpt,
                }
            )
            if len(hits) >= args.max_results:
                break
        if len(hits) >= args.max_results:
            break

    role_counts: dict[str, int] = {}
    for hit in hits:
        for role in hit["roles"]:
            role_counts[role] = role_counts.get(role, 0) + 1
    report = {
        "tool": "local-search-claim-bundle",
        "project": str(root),
        "term": args.term,
        "case_sensitive": args.case_sensitive,
        "files_scanned": len(selected),
        "result_count": len(hits),
        "role_counts": role_counts,
        "hits": hits,
        "non_claim": "Hits are locators. Reopen canonical owners and immutable witnesses before resolving meaning.",
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return 0 if hits else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--json", action="store_true")
    doctor_parser.add_argument("--timeout", type=int, default=30)
    doctor_parser.set_defaults(func=doctor)

    capabilities_parser = subparsers.add_parser("qmd-capabilities")
    capabilities_parser.add_argument("--timeout", type=int, default=30)
    capabilities_parser.set_defaults(func=qmd_capabilities)

    stage_parser = subparsers.add_parser("stage")
    stage_parser.add_argument("project")
    stage_parser.add_argument("output")
    stage_parser.add_argument("--include", action="append", required=True)
    stage_parser.add_argument("--exclude", action="append", default=[])
    stage_parser.add_argument("--replace", action="store_true")
    stage_parser.set_defaults(func=stage)

    policy_parser = subparsers.add_parser("init-policy")
    policy_parser.add_argument("project")
    policy_parser.add_argument("--name", required=True)
    policy_parser.add_argument("--output", required=True)
    policy_parser.add_argument("--force", action="store_true")
    policy_parser.set_defaults(func=init_policy)

    stage_policy_parser = subparsers.add_parser("stage-policy")
    stage_policy_parser.add_argument("policy")
    stage_policy_parser.add_argument("output")
    stage_policy_parser.add_argument("--replace", action="store_true")
    stage_policy_parser.set_defaults(func=stage_policy)

    pdf_parser = subparsers.add_parser("pdfgrep")
    pdf_parser.add_argument("pattern")
    pdf_parser.add_argument("path", nargs="+")
    pdf_parser.add_argument("--case-sensitive", action="store_true")
    pdf_parser.add_argument("--max-lines", type=int, default=8)
    pdf_parser.add_argument("--timeout", type=int, default=120)
    pdf_parser.set_defaults(func=pdfgrep)

    rga_parser = subparsers.add_parser("rga-smoke")
    rga_parser.add_argument("--pdf", required=True)
    rga_parser.add_argument("--term", required=True)
    rga_parser.add_argument("--max-lines", type=int, default=3)
    rga_parser.add_argument("--timeout", type=int, default=120)
    rga_parser.set_defaults(func=rga_smoke)

    tgrep_parser = subparsers.add_parser("tgrep-smoke")
    tgrep_parser.add_argument("--timeout", type=int, default=120)
    tgrep_parser.set_defaults(func=tgrep_smoke)

    qmd_parser = subparsers.add_parser("qmd-smoke")
    qmd_parser.add_argument("--index")
    qmd_parser.add_argument("--collection")
    qmd_parser.add_argument("--query")
    qmd_parser.add_argument("--limit", type=int, default=5)
    qmd_parser.add_argument("--timeout", type=int, default=120)
    qmd_parser.set_defaults(func=qmd_smoke)

    claim_parser = subparsers.add_parser("claim-bundle")
    claim_parser.add_argument("project")
    claim_parser.add_argument("term")
    claim_parser.add_argument("--include", action="append")
    claim_parser.add_argument("--exclude", action="append")
    claim_parser.add_argument("--context", type=int, default=2)
    claim_parser.add_argument("--max-results", type=int, default=40)
    claim_parser.add_argument("--case-sensitive", action="store_true")
    claim_parser.add_argument("--output")
    claim_parser.set_defaults(func=claim_bundle)
    return parser


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
