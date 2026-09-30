import re
from typing import Tuple, Optional

SEMVER_REGEX = re.compile(
    r"^v?(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

class Version:
    def __init__(self, major: int = 0, minor: int = 1, patch: int = 0, prefix: str = "v"):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prefix = prefix

    @classmethod
    def parse(cls, version_str: str) -> "Version":
        raw = version_str.strip()
        prefix = "v" if raw.startswith("v") else ""
        m = SEMVER_REGEX.match(raw)
        if not m:
            raise ValueError(f"Invalid SemVer string: {version_str}")
        return cls(
            major=int(m.group("major")),
            minor=int(m.group("minor")),
            patch=int(m.group("patch")),
            prefix=prefix,
        )

    def bump_patch(self) -> "Version":
        return Version(self.major, self.minor, self.patch + 1, self.prefix)

    def bump_minor(self) -> "Version":
        return Version(self.major, self.minor + 1, 0, self.prefix)

    def bump_major(self) -> "Version":
        return Version(self.major + 1, 0, 0, self.prefix)

    def __str__(self) -> str:
        return f"{self.prefix}{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return f"<Version {self}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other: "Version") -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
