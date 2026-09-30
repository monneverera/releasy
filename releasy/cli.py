import argparse
import sys
import os
from releasy import __version__
from releasy.git_ops import is_git_repo, get_latest_tag, get_commits_since, create_tag, add_and_commit
from releasy.semver import Version
from releasy.changelog import determine_bump_type, generate_release_notes, update_changelog_file

# ANSI color formatting
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
DIM = "\033[2m"

def print_banner():
    print(f"{CYAN}{BOLD}releasy{RESET} {DIM}v{__version__} — Zero-friction SemVer & Changelog engine{RESET}\n")

def get_current_and_next_version(latest_tag: str, bump_override: str, commits: list) -> tuple:
    if latest_tag:
        try:
            curr_ver = Version.parse(latest_tag)
        except ValueError:
            curr_ver = Version(0, 1, 0, prefix="v")
    else:
        curr_ver = Version(0, 0, 0, prefix="v")

    bump = bump_override
    if bump == "auto":
        bump = determine_bump_type(commits)

    if curr_ver.major == 0 and curr_ver.minor == 0 and curr_ver.patch == 0:
        next_ver = Version(0, 1, 0, prefix=curr_ver.prefix)
    elif bump == "major":
        next_ver = curr_ver.bump_major()
    elif bump == "minor":
        next_ver = curr_ver.bump_minor()
    else:
        next_ver = curr_ver.bump_patch()

    return curr_ver, next_ver, bump

def cmd_status(args):
    print_banner()
    if not is_git_repo():
        print(f"{RED}Error: Not inside a valid git repository.{RESET}")
        sys.exit(1)

    latest_tag = get_latest_tag()
    commits = get_commits_since(latest_tag)
    curr_ver, next_ver, bump_type = get_current_and_next_version(latest_tag, "auto", commits)

    print(f"Current Tag     : {YELLOW}{latest_tag if latest_tag else '(none)'}{RESET}")
    print(f"Commits Pending : {BOLD}{len(commits)}{RESET}")
    print(f"Detected Bump   : {MAGENTA}{bump_type.upper()}{RESET}")
    print(f"Suggested Next  : {GREEN}{BOLD}{next_ver}{RESET}\n")

    if not commits:
        print(f"{DIM}No new commits since {latest_tag or 'initial commit'}. Working tree is clean.{RESET}")
        return

    print(f"{BOLD}Pending Conventional Commits:{RESET}")
    for c in commits:
        scope = f"({c.scope})" if c.scope else ""
        breaking = f" {RED}[BREAKING]{RESET}" if c.is_breaking else ""
        print(f"  {CYAN}{c.type}{scope}{RESET}: {c.subject}{breaking} {DIM}({c.hash[:7]}){RESET}")

def cmd_preview(args):
    if not is_git_repo():
        print(f"{RED}Error: Not inside a valid git repository.{RESET}")
        sys.exit(1)

    latest_tag = get_latest_tag()
    commits = get_commits_since(latest_tag)
    if not commits:
        print(f"{YELLOW}No commits to release since {latest_tag or 'start'}.{RESET}")
        return

    curr_ver, next_ver, _ = get_current_and_next_version(latest_tag, args.bump, commits)
    notes = generate_release_notes(str(next_ver), commits)
    print(f"{BOLD}Release Notes Preview for {GREEN}{next_ver}{RESET}:\n")
    print(notes)

def cmd_release(args):
    print_banner()
    if not is_git_repo():
        print(f"{RED}Error: Not inside a valid git repository.{RESET}")
        sys.exit(1)

    latest_tag = get_latest_tag()
    commits = get_commits_since(latest_tag)
    if not commits:
        print(f"{YELLOW}No new commits found since tag {latest_tag or 'repository start'}. Release skipped.{RESET}")
        return

    curr_ver, next_ver, bump_type = get_current_and_next_version(latest_tag, args.bump, commits)
    notes = generate_release_notes(str(next_ver), commits)

    print(f"Current Version : {YELLOW}{curr_ver if latest_tag else '0.0.0'}{RESET}")
    print(f"Target Version  : {GREEN}{BOLD}{next_ver}{RESET} ({bump_type})")
    print(f"Changelog File  : {args.changelog}")
    print(f"Tag Commit      : {'Yes' if not args.no_tag else 'No'}")
    print(f"Git Commit      : {'Yes' if not args.no_commit else 'No'}\n")

    if args.dry_run:
        print(f"{YELLOW}[DRY RUN] No files or git tags will be modified.{RESET}\n")
        print(f"{BOLD}Generated Release Notes:{RESET}\n")
        print(notes)
        return

    if not args.yes:
        confirm = input(f"Proceed with release {GREEN}{next_ver}{RESET}? [y/N]: ").strip().lower()
        if confirm != "y":
            print(f"{RED}Release aborted by user.{RESET}")
            return

    # 1. Update changelog
    print(f"-> Writing release notes to {args.changelog}...")
    update_changelog_file(args.changelog, notes)

    # 2. Commit changelog if enabled
    if not args.no_commit:
        commit_msg = f"chore(release): {next_ver}"
        print(f"-> Committing changes ({commit_msg})...")
        add_and_commit([args.changelog], commit_msg)

    # 3. Create tag if enabled
    if not args.no_tag:
        tag_msg = f"Release {next_ver}"
        print(f"-> Tagging release {next_ver}...")
        create_tag(str(next_ver), tag_msg)

    print(f"\n{GREEN}{BOLD}Successfully released {next_ver}!{RESET} 🎉")


def main():
    parser = argparse.ArgumentParser(
        prog="releasy",
        description="A lightning-fast micro CLI for conventional changelogs and SemVer releases."
    )
    parser.add_argument("--version", "-v", action="version", version=f"releasy {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Status
    sub_status = subparsers.add_parser("status", help="Show current version and unreleased commits")
    sub_status.set_defaults(func=cmd_status)

    # Preview
    sub_prev = subparsers.add_parser("preview", help="Preview generated changelog without writing")
    sub_prev.add_argument("--bump", choices=["auto", "patch", "minor", "major"], default="auto", help="SemVer bump type")
    sub_prev.set_defaults(func=cmd_preview)

    # Release
    sub_rel = subparsers.add_parser("release", help="Bump version, update CHANGELOG.md, and create git tag")
    sub_rel.add_argument("--bump", choices=["auto", "patch", "minor", "major"], default="auto", help="SemVer bump type (default: auto)")
    sub_rel.add_argument("--changelog", default="CHANGELOG.md", help="Path to changelog file (default: CHANGELOG.md)")
    sub_rel.add_argument("--no-tag", action="store_true", help="Do not create a git tag")
    sub_rel.add_argument("--no-commit", action="store_true", help="Do not commit the changelog file")
    sub_rel.add_argument("--dry-run", action="store_true", help="Simulate release without modifying git or disk")
    sub_rel.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    sub_rel.set_defaults(func=cmd_release)

    args = parser.parse_args()

    if not args.command:
        # Default behavior: status
        cmd_status(args)
    else:
        args.func(args)

if __name__ == "__main__":
    main()
