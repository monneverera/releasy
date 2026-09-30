import os
from datetime import date
from typing import List, Dict
from releasy.git_ops import Commit

SECTION_TITLES = {
    "breaking": "💥 Breaking Changes",
    "feat": "🚀 Features",
    "fix": "🐛 Bug Fixes",
    "perf": "⚡ Performance",
    "refactor": "♻️ Code Refactoring",
    "docs": "📝 Documentation",
    "chore": "🔧 Chores & Maintenance",
    "test": "🧪 Tests",
    "ci": "🤖 CI/CD",
    "build": "📦 Build System",
    "other": "📌 Other Changes",
}

SECTION_ORDER = [
    "breaking",
    "feat",
    "fix",
    "perf",
    "refactor",
    "docs",
    "chore",
    "test",
    "ci",
    "build",
    "other",
]


def determine_bump_type(commits: List[Commit]) -> str:
    """Mendeteksi apakah butuh major, minor, atau patch."""
    if not commits:
        return "patch"
    for c in commits:
        if c.is_breaking:
            return "major"
    for c in commits:
        if c.type == "feat":
            return "minor"
    return "patch"


def generate_release_notes(version_tag: str, commits: List[Commit], release_date: str = "") -> str:
    if not release_date:
        release_date = date.today().isoformat()

    grouped: Dict[str, List[Commit]] = {k: [] for k in SECTION_ORDER}

    for c in commits:
        if c.is_breaking:
            grouped["breaking"].append(c)
        elif c.type in grouped:
            grouped[c.type].append(c)
        else:
            grouped["other"].append(c)

    lines: List[str] = [f"## [{version_tag}] - {release_date}\n"]

    for sec in SECTION_ORDER:
        sec_commits = grouped.get(sec, [])
        if not sec_commits:
            continue
        title = SECTION_TITLES.get(sec, sec.capitalize())
        lines.append(f"### {title}\n")
        for c in sec_commits:
            scope_prefix = f"**{c.scope}:** " if c.scope else ""
            short_hash = c.hash[:7] if c.hash else ""
            hash_suffix = f" (`{short_hash}`)" if short_hash else ""
            lines.append(f"- {scope_prefix}{c.subject}{hash_suffix}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def update_changelog_file(changelog_path: str, new_entry: str) -> None:
    header = "# Changelog\n\nAll notable changes to this project will be documented in this file.\nSee [Conventional Commits](https://www.conventionalcommits.org/) for commit guidelines.\n\n"

    if not os.path.exists(changelog_path):
        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write(header + new_entry)
        return

    with open(changelog_path, "r", encoding="utf-8") as f:
        existing_content = f.read()

    # If header exists, insert right after the header or at the top
    if "# Changelog" in existing_content:
        parts = existing_content.split("# Changelog", 1)
        # Check if there is an intro line before the first ## release
        intro_part = parts[1]
        first_release_idx = intro_part.find("\n## ")
        if first_release_idx != -1:
            intro = intro_part[:first_release_idx]
            rest = intro_part[first_release_idx:]
            updated = f"# Changelog{intro}\n\n{new_entry}\n{rest.lstrip()}"
        else:
            updated = f"# Changelog\n\n{new_entry}\n{intro_part.lstrip()}"
    else:
        updated = header + new_entry + "\n" + existing_content

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(updated)
