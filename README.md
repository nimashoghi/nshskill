# skill-kit

Ship [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code) from Python packages with zero boilerplate.

## Why

Claude Code skills are markdown files that live in `.claude/skills/` and teach Claude how to use your library. If you maintain a Python package, you probably want users to install your skill with a single command — but wiring up the file copying, frontmatter parsing, and CLI yourself is tedious and repetitive. `skill-kit` handles all of that so you can focus on writing the skill content.

## Install

```bash
pip install skill-kit
# or
uv add skill-kit
```

Requires Python 3.10+.

## Quick start

### Option A: Let Claude do it

Install the `init-skill` skill, then invoke it in Claude Code:

```bash
skill-kit skill install          # install to current project
skill-kit skill install --global # install at user level
```

Then in Claude Code, run `/init-skill` and Claude will analyze your codebase and set up the full skill-kit integration — `_skill/` directory, `SKILL.md`, CLI wiring, and dependency.

### Option B: Manual setup

#### 1. Create a skill directory

Add a `_skill/` directory inside your package with a `SKILL.md` file:

```
src/myproject/
├── __init__.py
├── ...
└── _skill/
    ├── SKILL.md
    └── references/         # optional extra files
        └── api-cheatsheet.md
```

#### 2. Write SKILL.md with frontmatter

The file must start with YAML frontmatter containing at least a `name` field:

```markdown
---
name: using-myproject
description: Short description of when Claude should use this skill.
---

# myproject

Instructions for Claude on how to use your library go here.
```

#### 3. Add a CLI entry point

The simplest approach — a standalone CLI with just the skill command:

```python
# src/myproject/cli.py
from pathlib import Path
from skill_kit import Skill, create_skill_cli

skill = Skill.from_dir(Path(__file__).resolve().parent / "_skill")
main = create_skill_cli("myproject", skill)
```

```toml
# pyproject.toml
[project.scripts]
myproject = "myproject.cli:main"
```

Users can then run:

```bash
myproject skill install          # install to .claude/skills/using-myproject/
myproject skill install --global # install to ~/.claude/skills/using-myproject/
myproject skill uninstall        # remove it
```

## API

### `Skill`

```python
from skill_kit import Skill
```

A dataclass with two fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Skill name (used as the directory name under `.claude/skills/`) |
| `skill_dir` | `Path` | Path to the source directory containing `SKILL.md` |

#### `Skill.from_dir(skill_dir: Path) -> Skill`

Parse a `Skill` from a directory. Reads the `name` from the YAML frontmatter in `SKILL.md`. Raises `FileNotFoundError` if the directory or `SKILL.md` is missing, and `ValueError` if the frontmatter is missing or lacks a `name` field.

```python
skill = Skill.from_dir(Path(__file__).resolve().parent / "_skill")
```

#### `skill.install(target=None, *, global_=False) -> Path`

Copy the skill directory contents into `<target>/.claude/skills/<name>/`. Returns the destination path.

- If `global_=True`, installs to `~/.claude/skills/<name>/` (ignores `target`).
- If `target` is `None`, defaults to the current working directory.
- Overwrites any existing installation at the destination.
- Skips `__init__.py` and `__pycache__` when copying.

#### `skill.uninstall(target=None, *, global_=False) -> bool`

Remove an installed skill directory. Returns `True` if something was removed, `False` if the skill wasn't installed at that location.

### `add_skill_commands`

```python
from skill_kit import add_skill_commands
```

```python
def add_skill_commands(subparsers, skill: Skill) -> None
```

Add `skill install` and `skill uninstall` subcommands to an existing argparse subparsers action. Use this when your package already has a CLI and you want to add skill management alongside other commands:

```python
import argparse
from pathlib import Path
from skill_kit import Skill, add_skill_commands, dispatch_skill

def main():
    parser = argparse.ArgumentParser(prog="myproject")
    subs = parser.add_subparsers(dest="command")

    # Your other commands...
    subs.add_parser("run", help="Run the thing")

    # Add skill install/uninstall
    skill = Skill.from_dir(Path(__file__).resolve().parent / "_skill")
    add_skill_commands(subs, skill)

    args = parser.parse_args()

    if args.command == "skill":
        dispatch_skill(args)
    elif args.command == "run":
        ...
```

### `dispatch_skill`

```python
from skill_kit.cli import dispatch_skill
```

```python
def dispatch_skill(args: argparse.Namespace) -> None
```

Route a parsed `skill` subcommand to the appropriate `install`/`uninstall` method. Call this after `parse_args()` when `args.command == "skill"`.

### `create_skill_cli`

```python
from skill_kit import create_skill_cli
```

```python
def create_skill_cli(prog: str, skill: Skill) -> Callable[[], None]
```

Return a ready-to-use `main()` function for packages that only need skill commands in their CLI. The returned function parses `sys.argv` and dispatches automatically:

```python
# src/myproject/cli.py
from pathlib import Path
from skill_kit import Skill, create_skill_cli

main = create_skill_cli("myproject", Skill.from_dir(Path(__file__).resolve().parent / "_skill"))
```

## Skill directory layout

A skill directory can contain any files you want to ship to users. The only requirement is a `SKILL.md` at the root:

```
_skill/
├── SKILL.md              # required — frontmatter + skill instructions
└── references/           # optional — supplementary docs
    ├── api.md
    └── examples.md
```

To include existing docs from your repo without duplicating them, use symlinks:

```bash
ln -s ../../docs/api.md src/myproject/_skill/references/api.md
```

When installed, the entire directory tree is copied to `.claude/skills/<name>/`, preserving structure. `__init__.py` and `__pycache__` are excluded automatically.

## SKILL.md format

```markdown
---
name: using-myproject
description: When to activate this skill.
---

Your skill content in markdown. This is what Claude reads
to learn how to use your library.
```

The frontmatter must contain:
- **`name`** (required): Used as the subdirectory name under `.claude/skills/`.
- **`description`** (optional): Helps Claude decide when the skill is relevant.

## License

MIT
