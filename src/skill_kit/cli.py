from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from skill_kit.skill import Skill


def add_skill_commands(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    skill: Skill,
) -> None:
    """Add ``skill install`` and ``skill uninstall`` subcommands."""
    skill_parser = subparsers.add_parser("skill", help="Manage Claude Code skill")
    skill_subs = skill_parser.add_subparsers(dest="skill_command")

    # -- install --------------------------------------------------------
    install_p = skill_subs.add_parser(
        "install", help=f"Install the {skill.name} skill for Claude Code"
    )
    install_p.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Target directory (default: current working directory)",
    )
    install_p.add_argument(
        "--global",
        dest="global_",
        action="store_true",
        default=False,
        help="Install at user level (~/.claude/skills/) instead of project level",
    )

    # -- uninstall ------------------------------------------------------
    uninstall_p = skill_subs.add_parser(
        "uninstall", help=f"Uninstall the {skill.name} skill"
    )
    uninstall_p.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Target directory (default: current working directory)",
    )
    uninstall_p.add_argument(
        "--global",
        dest="global_",
        action="store_true",
        default=False,
        help="Uninstall from user level (~/.claude/skills/)",
    )

    # Store references so dispatch can use them
    install_p.set_defaults(_skill=skill, _skill_action="install")
    uninstall_p.set_defaults(_skill=skill, _skill_action="uninstall")
    skill_parser.set_defaults(_skill_parser=skill_parser)


def dispatch_skill(args: argparse.Namespace) -> None:
    """Dispatch a parsed skill sub-command. Call after ``parse_args()``."""
    action = getattr(args, "_skill_action", None)
    if action == "install":
        args._skill.install(args.path, global_=args.global_)
    elif action == "uninstall":
        args._skill.uninstall(args.path, global_=args.global_)
    elif hasattr(args, "_skill_parser"):
        args._skill_parser.print_help()


def create_skill_cli(prog: str, skill: Skill) -> Callable[[], None]:
    """Return a ``main()`` function that exposes only skill commands.

    Useful as a ``[project.scripts]`` entry point::

        [project.scripts]
        myproject = "myproject._cli:main"

        # _cli.py
        from skill_kit import Skill, create_skill_cli
        main = create_skill_cli("myproject", Skill.from_dir(...))
    """

    def main() -> None:
        parser = argparse.ArgumentParser(prog=prog)
        subs = parser.add_subparsers(dest="command")
        add_skill_commands(subs, skill)

        args = parser.parse_args()

        if args.command == "skill":
            dispatch_skill(args)
        else:
            parser.print_help()

    return main
