# Cross-platform installation

Install only the tiers the project needs. Prefer one package manager per toolchain and verify versions in a fresh shell.

Official sources:

- ripgrep: <https://github.com/BurntSushi/ripgrep>
- ripgrep-all: <https://github.com/phiresky/ripgrep-all>
- tgrep: <https://github.com/microsoft/tgrep>
- QMD: <https://github.com/tobi/qmd>

## Requirements

- `rg`: required baseline.
- tgrep: optional trigram-indexed regex tier for repeatedly searched large
  codebases; it does not replace `rg` for live or one-off searches.
- `rga` plus Poppler/Pandoc: optional binary-document tier.
- QMD: optional BM25/semantic/hybrid tier.
- LangExtract: optional source-grounded structured extraction after retrieval;
  it is not an index or a replacement for `rg`/QMD.
- QMD currently requires Node.js 22+ or Bun; verify the repository before pinning a runtime version.
- QMD semantic/hybrid modes download local GGUF models on first use. Treat network, disk, RAM, and GPU use as an explicit machine-level decision.

## Windows

Recommended supported combinations:

```powershell
# exact search
winget install BurntSushi.ripgrep.MSVC

# rga with adapters/dependencies: use one
choco install ripgrep-all -y
# or
scoop install rga

# QMD runtime and package
winget install OpenJS.NodeJS.LTS --exact --scope user
npm install -g @tobilu/qmd
```

Install tgrep without administrator privileges through the bundled installer:

```powershell
python .\scripts\install_tgrep_userspace.py --check
python .\scripts\install_tgrep_userspace.py --install --version vX.Y.Z
```

The default destination is `%LOCALAPPDATA%\Programs\tgrep\tgrep.exe`. The
installer verifies the official release checksum but does not edit PATH. Add
`%LOCALAPPDATA%\Programs\tgrep` to the user PATH through Windows Settings, or
with a reviewed user-scope PowerShell command; open a new terminal afterward.

The ripgrep-all project recommends Chocolatey or Scoop on Windows because a manually downloaded `rga` binary does not include adapter dependencies such as Poppler.

After installation, open a new terminal. If an existing agent session has stale `PATH`, reconstruct it:

```powershell
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [Environment]::GetEnvironmentVariable("Path", "User")
```

Common QMD global-bin location is `%APPDATA%\npm`; confirm with `Get-Command qmd`, not a hard-coded version directory.

## macOS

```bash
brew install ripgrep tgrep rga pandoc poppler ffmpeg node sqlite
npm install -g @tobilu/qmd
```

Homebrew QMD dependencies may resolve under `/opt/homebrew` on Apple Silicon and `/usr/local` on Intel. Use `command -v`, `brew --prefix`, and a new shell rather than hard-coding either prefix.

If Homebrew itself fails before installing tgrep, do not repair or upgrade the
whole package manager merely for this optional tier. Use the matching official
prebuilt release after verifying its published SHA-256 checksum, or continue
with `rg`.

For a strictly userspace installation, use:

```bash
python3 scripts/install_tgrep_userspace.py --check
python3 scripts/install_tgrep_userspace.py --install --version vX.Y.Z
```

This installs to `~/.local/bin` without changing shell startup files.

QMD documents Homebrew SQLite as a macOS requirement for extension support.

## Linux

Install exact and adapter dependencies from the distribution when sufficiently current:

```bash
sudo apt-get update
sudo apt-get install ripgrep pandoc poppler-utils ffmpeg
```

Install `rga` from the distribution, Homebrew/Linuxbrew, Nix, Cargo, or an official release as appropriate. Ensure Node is 22+ before installing QMD:

```bash
node --version
npm install -g @tobilu/qmd
```

Install the matching official musl tgrep binary to `~/.local/bin` without root:

```bash
python3 scripts/install_tgrep_userspace.py --check
python3 scripts/install_tgrep_userspace.py --install --version vX.Y.Z
```

Ensure `~/.local/bin` is on the user's PATH, then open a fresh shell. The
installer does not modify shell profiles or start a tgrep server.

Distribution Node packages may be older than QMD's requirement. Use a maintained Node version manager or official distribution instead of forcing QMD into an incompatible runtime.

## Verification

```bash
rg --version
rga --version
rga --rga-list-adapters
pdftotext -v
node --version
qmd --version
qmd doctor
qmd skills get qmd --full
python scripts/local_search_tools.py doctor
python scripts/local_search_tools.py tgrep-smoke
python scripts/install_tgrep_userspace.py --check
python scripts/local_search_tools.py qmd-capabilities
```

Binary presence is not an adapter test. Run `rga-smoke` against a known real text-layer PDF.

## LangExtract (optional post-retrieval extraction)

Install it in the project environment only when a task needs structured fields
grounded to text already located by the retrieval ladder. In the dedicated
Conda environment used in this workspace:

```bash
python -m pip install langextract
python -c 'import langextract; print("langextract import OK")'
```

The package supports cloud providers and local inference. Installing it does
not transmit corpus text. Do not configure a cloud key or use a cloud provider
for restricted material without explicit authorization; use a local provider
instead. Read `references/langextract.md` before running extraction.

## Updates and removal of stale assumptions

- Do not pin a path such as `node-v22.23.1` or a temporary `qmd-node24-clean` folder in shared instructions.
- Do not assume `pandoc` is required for plain Markdown search.
- Do not assume Office adapters succeed on every zip-based Office file; keep canonical text mirrors where search reliability matters.
- Do not assume a QMD index syncs across machines. Rebuild it from the shared corpus recipe.
- Check official repositories before changing package names, minimum runtimes, or QMD query syntax.
- Upgrade QMD deliberately with `npm install -g @tobilu/qmd@latest`, then rerun capability detection and project smoke queries before relying on new flags.
- Check tgrep releases with `install_tgrep_userspace.py --check`. When an update
  is justified, review release notes, install an explicit tag, run
  `tgrep-smoke`, compare representative queries with `rg`, and rebuild each
  per-machine index before reuse.
