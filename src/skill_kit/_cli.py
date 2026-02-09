from __future__ import annotations

from pathlib import Path

from skill_kit import Skill, create_skill_cli

skill = Skill.from_dir(Path(__file__).resolve().parent / "_skill")
main = create_skill_cli("skill-kit", skill)

if __name__ == "__main__":
    main()
