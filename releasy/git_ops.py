import subprocess
import re
from typing import List, Dict, Optional, Any

CONVENTIONAL_REGEX = re.compile(
    r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$"
)

class Commit:
    def __init__(self, commit_hash: str, raw_subject: str, body: str = "", author: str = ""):
        self.hash = commit_hash
        self.raw_subject = raw_subject.strip()
        self.body = body.strip()
        self.author = author.strip()
        self.type = "other"
        self.scope = None
        self.subject = self.raw_subject
        self.is_breaking = False
        self._parse_conventional()

    def _parse_conventional(self):
        m = CONVENTIONAL_REGEX.match(self.raw_subject)
        if m:
            self.type = m.group("type").lower()
            self.scope = m.group("scope")
            self.is_breaking = bool(m.group("breaking"))
            self.subject = m.group("subject").strip()
        
        # Check breaking change in footer/body
        if "BREAKING CHANGE:" in self.body or "BREAKING-CHANGE:" in self.body:
            self.is_breaking = True

    def __repr__(self):
        return f"<Commit {self.hash[:7]} [{self.type}] {self.subject}>"


def run_git(args: List[str], cwd: Optional[str] = None) -> str:
    res = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if res.returncode != 0:
        raise RuntimeError(f"Git command failed: git {' '.join(args)}\nError: {res.stderr.strip()}")
    return res.stdout.strip()


def is_git_repo(cwd: Optional[str] = None) -> bool:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return res.returncode == 0
    except Exception:
        return False


def get_latest_tag(cwd: Optional[str] = None) -> Optional[str]:
    try:
        # Get most recent reachable tag
        tag = run_git(["describe", "--tags", "--abbrev=0"], cwd=cwd)
        return tag if tag else None
    except Exception:
        return None


def get_commits_since(tag: Optional[str] = None, cwd: Optional[str] = None) -> List[Commit]:
    rev_range = f"{tag}..HEAD" if tag else "HEAD"
    # Format: hash%x1fsubject%x1fauthor%x1fbody%x1e
    log_format = "%H%x1f%s%x1f%an%x1f%b%x1e"
    try:
        raw_log = run_git(["log", rev_range, f"--pretty=format:{log_format}"], cwd=cwd)
    except Exception:
        return []

    if not raw_log:
        return []

    commits: List[Commit] = []
    entries = raw_log.split("\x1e")
    for entry in entries:
        if not entry.strip():
            continue
        parts = entry.strip().split("\x1f")
        h = parts[0] if len(parts) > 0 else ""
        subj = parts[1] if len(parts) > 1 else ""
        auth = parts[2] if len(parts) > 2 else ""
        body = parts[3] if len(parts) > 3 else ""
        if h and subj:
            commits.append(Commit(commit_hash=h, raw_subject=subj, body=body, author=auth))
    return commits


def create_tag(tag_name: str, message: str, cwd: Optional[str] = None) -> None:
    run_git(["tag", "-a", tag_name, "-m", message], cwd=cwd)


def add_and_commit(files: List[str], message: str, cwd: Optional[str] = None) -> None:
    for f in files:
        run_git(["add", f], cwd=cwd)
    run_git(["commit", "-m", message], cwd=cwd)
