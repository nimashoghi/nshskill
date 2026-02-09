from __future__ import annotations

import textwrap

import pytest

from skill_kit import Skill, add_skill_commands, create_skill_cli


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def skill_dir(tmp_path):
    """Create a minimal skill directory with SKILL.md and a reference file."""
    d = tmp_path / "_skill"
    d.mkdir()

    (d / "SKILL.md").write_text(
        textwrap.dedent("""\
            ---
            name: my-test-skill
            description: A test skill.
            ---

            # My Test Skill

            Body content here.
        """)
    )

    refs = d / "references"
    refs.mkdir()
    (refs / "extra.md").write_text("# Extra reference\n")

    return d


@pytest.fixture()
def skill(skill_dir):
    return Skill.from_dir(skill_dir)


# ---------------------------------------------------------------------------
# Skill.from_dir / __post_init__
# ---------------------------------------------------------------------------


class TestSkillFromDir:
    def test_parses_name(self, skill):
        assert skill.name == "my-test-skill"

    def test_missing_dir(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Skill directory not found"):
            Skill(name="x", skill_dir=tmp_path / "nope")

    def test_missing_skill_md(self, tmp_path):
        d = tmp_path / "empty"
        d.mkdir()
        with pytest.raises(FileNotFoundError, match="SKILL.md not found"):
            Skill(name="x", skill_dir=d)

    def test_missing_frontmatter(self, tmp_path):
        d = tmp_path / "bad"
        d.mkdir()
        (d / "SKILL.md").write_text("# No frontmatter\n")
        with pytest.raises(ValueError, match="missing YAML frontmatter"):
            Skill.from_dir(d)

    def test_missing_name_field(self, tmp_path):
        d = tmp_path / "noname"
        d.mkdir()
        (d / "SKILL.md").write_text("---\ndescription: foo\n---\n")
        with pytest.raises(ValueError, match="missing the 'name' field"):
            Skill.from_dir(d)


# ---------------------------------------------------------------------------
# Install / Uninstall
# ---------------------------------------------------------------------------


class TestInstallUninstall:
    def test_install_copies_files(self, skill, tmp_path):
        target = tmp_path / "project"
        target.mkdir()

        dest = skill.install(target)

        assert dest == target / ".claude" / "skills" / "my-test-skill"
        assert (dest / "SKILL.md").is_file()
        assert (dest / "references" / "extra.md").is_file()

    def test_install_skips_pycache_and_init(self, skill_dir, tmp_path):
        # Add files that should be skipped
        (skill_dir / "__init__.py").write_text("")
        (skill_dir / "__pycache__").mkdir()
        (skill_dir / "__pycache__" / "foo.pyc").write_text("")

        skill = Skill.from_dir(skill_dir)
        target = tmp_path / "project"
        target.mkdir()

        dest = skill.install(target)

        assert not (dest / "__init__.py").exists()
        assert not (dest / "__pycache__").exists()

    def test_install_overwrites_existing(self, skill, tmp_path):
        target = tmp_path / "project"
        target.mkdir()

        dest = skill.install(target)
        # Modify installed file
        (dest / "SKILL.md").write_text("modified")

        # Re-install should overwrite
        dest2 = skill.install(target)
        assert dest == dest2
        assert "my-test-skill" in (dest2 / "SKILL.md").read_text()

    def test_install_global(self, skill, tmp_path, monkeypatch):
        monkeypatch.setattr("pathlib.Path.home", staticmethod(lambda: tmp_path))

        dest = skill.install(global_=True)

        assert dest == tmp_path / ".claude" / "skills" / "my-test-skill"
        assert (dest / "SKILL.md").is_file()

    def test_uninstall_removes(self, skill, tmp_path):
        target = tmp_path / "project"
        target.mkdir()

        skill.install(target)
        assert skill.uninstall(target) is True
        assert not (target / ".claude" / "skills" / "my-test-skill").exists()

    def test_uninstall_not_installed(self, skill, tmp_path):
        assert skill.uninstall(tmp_path) is False


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------


class TestCLI:
    def test_add_skill_commands_install(self, skill, tmp_path):
        import argparse

        parser = argparse.ArgumentParser()
        subs = parser.add_subparsers(dest="command")
        add_skill_commands(subs, skill)

        args = parser.parse_args(["skill", "install", "--path", str(tmp_path)])
        assert args.skill_command == "install"
        assert args.path == tmp_path
        assert args.global_ is False

    def test_add_skill_commands_uninstall(self, skill, tmp_path):
        import argparse

        parser = argparse.ArgumentParser()
        subs = parser.add_subparsers(dest="command")
        add_skill_commands(subs, skill)

        args = parser.parse_args(["skill", "uninstall", "--global"])
        assert args.skill_command == "uninstall"
        assert args.global_ is True

    def test_create_skill_cli(self, skill, tmp_path, monkeypatch):
        main = create_skill_cli("testprog", skill)
        monkeypatch.setattr(
            "sys.argv", ["testprog", "skill", "install", "--path", str(tmp_path)]
        )
        main()

        assert (
            tmp_path / ".claude" / "skills" / "my-test-skill" / "SKILL.md"
        ).is_file()
