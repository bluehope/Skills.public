# Skills (public)

Agent skills for evidence-grounded computational research, local search, and scientific figure making. Each folder is a self-contained skill (`SKILL.md` + references/scripts/assets) that works with Codex, Claude Code, and other SKILL.md-aware agents.

## Install

Copy a skill folder into your agent's skill root, e.g. `~/.codex/skills/<name>/` or `~/.claude/skills/<name>/`. With the Codex skill installer: `install-skill-from-github.py --repo <owner>/<repo> --path <name>`.

Skills reference each other by name (`$name`). Some mention optional sibling skills that are not published here (`rehearse-lecture-delivery`, `computational-lecture-workflow`, `edit-phys-exam-figures`, `generate-lecture-figures`, `crop-figure-panels`, `extract-source-figures`, `qa-figure-assets`, `select-figure-evidence`, `hpc-skills`, `dft-skills`, `build-lecture-notes`, `ssh-skills`, `skill-librarian`); those references are informational.

Commands are written for a plain `python` in a working environment; substitute your own interpreter or environment.

## Skills

| skill | description |
|---|---|
| `llm-handover-skills` | Prepare hash-bound multi-worker dispatches or reconcile independent LLM receipts; not ordinary handoff notes or single-session summaries. |
| `research-skills` | Plan/audit scientific decisions and authorized research execution, durable records or handoff. Ordinary project file lookup or edits do not trigger research man… |
| `local-search` | Resolve broad, conflicting or binary local-source retrieval; manage requested indexes and search diagnostics. Plain known-path or filename lookup uses direct re… |
| `scientific-figure-making` | Route mixed scientific figure workflows or unresolved figure-production choices. A known static, trajectory or plot-style task uses its specialist directly. |
| `figures4papers-style` | Style and export publication Matplotlib plots using the pinned figures4papers reference, preserving data and license boundaries. |
| `atom-visualize` | Render static/interactive atomic structures, relaxation comparisons and provenance-backed spins. Geometry-only views need no DFT or figure-umbrella workflow. |
| `atom-trajectory-visualize` | Render multi-frame atomic trajectories and comparison movies with matched identity, provenance and camera; not static-only views or quantitative physics claims. |

## Attribution and third-party notices

- `figures4papers-style` references https://github.com/ChenLiu-1996/figures4papers (CC BY-NC 4.0) as a pinned external style reference; no upstream code is included.
- `local-search` describes optional external tools (ripgrep, ripgrep-all, tgrep, QMD, LangExtract) under their own licenses; none are bundled.

## License

MIT. See `LICENSE`.

Exported from a private canonical library; see `PUBLISH_LEDGER.json` for source tree hashes.
