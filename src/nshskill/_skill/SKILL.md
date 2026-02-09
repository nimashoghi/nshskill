---
name: init-skill
description: Initialize a Claude Code skill for a Python package using nshskill. Use when setting up a new skill for a library, creating SKILL.md for a package, wiring CLI install/uninstall commands, or adding nshskill integration to a Python project.
disable-model-invocation: true
skills:
  - creating-skills
---

# Initialize Package Skill

Analyze this codebase and create a Claude Code skill for it using `nshskill`. Follow the `creating-skills` skill for all SKILL.md authoring guidance (description format, naming, content quality, progressive disclosure).

## Process

1. **Understand the project**: Read `pyproject.toml`, `README.md`, `CLAUDE.md`, and key source files to identify the library's purpose, public API, import conventions, and coding patterns.

2. **Create skill directory** at `src/<package_name>/_skill/`.

3. **Write `SKILL.md`** following `creating-skills` guidelines:

   ```markdown
   ---
   name: using-<package-name>
   description: <What it does in ~10 words>. Use when <scenario 1>, <scenario 2>, <scenario 3>, or <scenario 4>.
   ---

   # <package-name>

   <Concise instructions for Claude — import conventions, key APIs, patterns, rules.>
   ```

4. **Add `nshskill` dependency** to `pyproject.toml`:

   ```toml
   dependencies = [
       ...,
       "nshskill",
   ]
   ```

5. **Wire up the CLI**:

   **No existing CLI** — create a standalone one:

   ```python
   # src/<package>/cli.py
   from pathlib import Path
   from nshskill import Skill, create_skill_cli

   skill = Skill.from_dir(Path(__file__).resolve().parent / "_skill")
   main = create_skill_cli("<package-name>", skill)
   ```

   ```toml
   # pyproject.toml
   [project.scripts]
   <package-name> = "<package>.cli:main"
   ```

   **Existing CLI with argparse subparsers** — integrate:

   ```python
   from nshskill import Skill, add_skill_commands, dispatch_skill

   skill = Skill.from_dir(Path(__file__).resolve().parent / "_skill")
   add_skill_commands(subparsers, skill)
   # in dispatch:
   if args.command == "skill":
       dispatch_skill(args)
   ```

6. **Optionally add `references/`** for detailed docs. Prefer symlinks to existing docs:

   ```bash
   ln -s ../../docs/api.md src/<package>/_skill/references/api.md
   ```

7. **Update `CLAUDE.md`** (if it exists) to document the `<package> skill install` command.

## Checklist

- [ ] SKILL.md passes the `creating-skills` quality checklist
- [ ] `nshskill` is in project dependencies
- [ ] CLI works: `<package> skill install` and `<package> skill install --global`
