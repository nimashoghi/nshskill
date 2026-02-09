from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Extract YAML frontmatter from a markdown file's text content."""
    if not text.startswith("---"):
        raise ValueError("SKILL.md is missing YAML frontmatter (must start with '---')")

    end = text.index("---", 3)
    return yaml.safe_load(text[3:end])


# Files/dirs to skip when copying the skill directory.
_SKIP = {"__init__.py", "__pycache__"}


@dataclass
class Skill:
    name: str
    skill_dir: Path

    def __post_init__(self) -> None:
        if not self.skill_dir.is_dir():
            raise FileNotFoundError(f"Skill directory not found: {self.skill_dir}")
        if not (self.skill_dir / "SKILL.md").is_file():
            raise FileNotFoundError(
                f"SKILL.md not found in skill directory: {self.skill_dir}"
            )

    @classmethod
    def from_dir(cls, skill_dir: Path) -> Skill:
        """Create a Skill by parsing the name from SKILL.md frontmatter."""
        skill_dir = skill_dir.resolve()
        text = (skill_dir / "SKILL.md").read_text()
        meta = _parse_frontmatter(text)

        name = meta.get("name")
        if not name:
            raise ValueError("SKILL.md frontmatter is missing the 'name' field")

        return cls(name=name, skill_dir=skill_dir)

    # ------------------------------------------------------------------
    # Install / Uninstall
    # ------------------------------------------------------------------

    def _resolve_target(self, target: Path | None, *, global_: bool) -> Path:
        """Return the concrete skill destination directory."""
        if global_:
            base = Path.home()
        elif target is not None:
            base = target
        else:
            base = Path.cwd()
        return base / ".claude" / "skills" / self.name

    def install(self, target: Path | None = None, *, global_: bool = False) -> Path:
        """Copy skill_dir contents to ``<target>/.claude/skills/<name>/``.

        Returns the destination path.
        """
        dest = self._resolve_target(target, global_=global_)

        # Clean previous installation
        if dest.exists():
            shutil.rmtree(dest)

        dest.mkdir(parents=True, exist_ok=True)

        for item in self.skill_dir.iterdir():
            if item.name in _SKIP:
                continue
            if item.is_file():
                shutil.copy2(item, dest / item.name)
            elif item.is_dir():
                shutil.copytree(item, dest / item.name)

        print(f"Installed skill '{self.name}' to {dest}")
        return dest

    def uninstall(self, target: Path | None = None, *, global_: bool = False) -> bool:
        """Remove an installed skill. Returns True if something was removed."""
        dest = self._resolve_target(target, global_=global_)

        if not dest.exists():
            print(
                f"Skill '{self.name}' is not installed at {dest}",
                file=sys.stderr,
            )
            return False

        shutil.rmtree(dest)
        print(f"Uninstalled skill '{self.name}' from {dest}")
        return True
