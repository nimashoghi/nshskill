# CLAUDE.md

## Project Overview

`skill-kit` is a small library that eliminates boilerplate for shipping Claude Code skills from Python packages. It handles SKILL.md frontmatter parsing, file copying to `.claude/skills/<name>/`, and argparse CLI wiring.

## Build & Development Commands

Package manager is **uv**. Build backend is `uv_build`.

```bash
uv sync --all-groups
uv run pytest -v
uv run ruff check
uv run ruff format --check
uv run basedpyright
```

## Code Architecture

```
src/skill_kit/
├── __init__.py    # re-exports: Skill, add_skill_commands, create_skill_cli, dispatch_skill
├── skill.py       # Skill dataclass + install/uninstall logic
├── cli.py         # argparse helpers: add_skill_commands(), create_skill_cli()
├── _cli.py        # skill-kit's own CLI entry point (dogfoods create_skill_cli)
└── _skill/
    └── SKILL.md   # init-skill: Claude Code skill for bootstrapping skill-kit integrations
```

- **`skill.py`** — `Skill` dataclass with `name` and `skill_dir`. `from_dir()` parses YAML frontmatter from SKILL.md. `install()` copies skill files to `.claude/skills/<name>/`, `uninstall()` removes them.
- **`cli.py`** — `add_skill_commands()` adds `skill install/uninstall` subcommands to an existing argparse subparsers action. `create_skill_cli()` returns a standalone `main()` callable for use as a `[project.scripts]` entry point.
- **`_cli.py`** — skill-kit's own CLI entry point, exposed as `skill-kit` command. Dogfoods `create_skill_cli()`.
- **`_skill/SKILL.md`** — The `init-skill` skill. When installed and invoked via `/init-skill`, instructs Claude to analyze a codebase and set up a full skill-kit integration.

## Claude Code Skill

skill-kit ships an `init-skill` skill for bootstrapping skill-kit integrations:

```bash
skill-kit skill install            # install to current project
skill-kit skill install --global   # install at user level
```

Then invoke `/init-skill` in Claude Code to have Claude set up the `_skill/` directory, SKILL.md, CLI wiring, and dependency for the current project.

## Code Conventions

- `from __future__ import annotations` in every file.
- `ruff format` for formatting, `basedpyright` standard mode for type checking.
- Modern type syntax: `X | None`, `list[int]`, `collections.abc`.
