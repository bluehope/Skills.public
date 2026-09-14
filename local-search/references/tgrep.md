# tgrep Indexed Regex Tier

Status: `EXPERIMENTAL`. tgrep is an optional optimization for repeated regex
searches in a large, mostly textual codebase. It uses a trigram index and can
serve multiple clients while watching changes. It does not search inside PDF or
Office containers, rank by meaning, understand syntax, or replace canonical-file
verification. The upstream project and current CLI are documented at
<https://github.com/microsoft/tgrep>.

## Activation gate

Keep `rg` when the lookup is one-off, the scope is already narrow, or scan time
is acceptable. Consider tgrep only when all of these hold:

- the same codebase receives repeated regex or literal searches;
- measured `rg` latency is material to the workflow;
- the include/exclude scope is stable enough to index safely;
- a per-machine index can live outside the repository, Dropbox, and deliverables.

Benchmark representative queries before retaining an index. Upstream benchmark
numbers describe their fixtures and prebuilt indexes; they are not a guarantee
for a local repository.

## Safe index setup

Use an explicit per-machine index path:

```bash
tgrep index /path/to/project \
  --index-path /path/to/per-machine-index \
  --exclude node_modules --exclude build --exclude generated
tgrep status /path/to/project --index-path /path/to/per-machine-index
tgrep -n -m 20 --index-path /path/to/per-machine-index "pattern" /path/to/project
```

Do not put index files under the source tree or a synced directory. Treat index
metadata as derived from the source's confidentiality class: restrict access and
delete it through the machine's normal data-retention process when no longer
needed. Review restricted paths and generated outputs before indexing.

The flags controlling membership and file size must match between `index` and
`serve`. tgrep defaults to a 64 MiB per-file cap. In a directory without `.git`,
`.gitignore` is not applied unless `--no-require-git` is used; inspect
`tgrep --files` and file counts before trusting coverage.

## Userspace installation

The bundled standard-library-only installer supports Windows x86-64/ARM64,
Linux x86-64/ARM64, and macOS Intel/Apple Silicon official release assets. It
does not require conda, root, or administrator privileges:

```bash
python scripts/install_tgrep_userspace.py --check
python scripts/install_tgrep_userspace.py --install --version vX.Y.Z
```

Default destinations are `~/.local/bin/tgrep` on Linux/macOS and
`%LOCALAPPDATA%\Programs\tgrep\tgrep.exe` on Windows. The installer:

- selects the OS/architecture-specific official GitHub asset;
- downloads `checksums.txt` and blocks on SHA-256 mismatch;
- stages the binary and replaces it atomically;
- preserves the existing destination as `tgrep.previous-VERSION` when possible;
- verifies `tgrep --version` after installation;
- does not edit PATH, start a server, or create an index.

Add the destination directory to the user PATH separately and verify it in a
fresh shell. Read [installation.md](installation.md) for platform-specific PATH
notes. An explicit `--install-dir` may be used for another user-owned path.

## Release tracking and update gate

Run the non-mutating check before a new-machine install, during deliberate tool
maintenance, or when a known upstream fix is needed:

```bash
python scripts/install_tgrep_userspace.py --check
```

The JSON report records installed path/version, latest tag and publication
time, selected asset, release URL, and `update_available`. Do not poll GitHub on
every search and do not auto-install `latest`. When an update is available:

1. inspect the linked release notes and choose an explicit tag;
2. stop any tgrep server using the old binary;
3. run `--install --version vX.Y.Z`;
4. run `local_search_tools.py tgrep-smoke`;
5. compare representative project queries with live `rg`;
6. rebuild per-machine indexes before trusting them with the new binary;
7. record old/new versions, asset checksum, date, smoke result, and residual
   warnings in the local runtime receipt.

If validation fails, restore the preserved `tgrep.previous-VERSION` binary or
continue with `rg`. A newer release is not itself evidence that index format,
watcher behavior, or search results remain compatible.

## Server policy and freshness

An index-only search is a snapshot. A watching `tgrep serve` process maintains
a live overlay and periodically reconciles the tree, but a watcher or server is
still operational state. Start it only for an active repeated-search workflow,
with the same scope and index flags, and record how it will be stopped. Do not
configure a login service or persistent daemon merely because tgrep is present.

Before a consequential claim:

1. inspect `tgrep status` and the indexed file scope;
2. rerun a narrow live `rg` query or `tgrep --no-index` when freshness matters;
3. reopen the canonical file and cite it, not the index output.

If index and live results differ, classify `INDEX`, preserve the mismatch in the
search receipt, and rebuild or refresh before using tgrep again.

## Validation and fallback

Run:

```bash
python scripts/local_search_tools.py doctor
python scripts/local_search_tools.py tgrep-smoke
python scripts/install_tgrep_userspace.py --check
```

The smoke test builds a disposable external index and compares tgrep results to
`rg` on a controlled corpus. It proves basic binary usability and output
equivalence for that fixture only. If tgrep is missing, fails, or offers no
measured benefit, continue with `rg` without weakening the search claim.
