# releasy ⚡

> Lightning-fast, zero-dependency CLI for conventional changelogs and automated SemVer releases.

`releasy` analyzes your Git commit history following the [Conventional Commits](https://www.conventionalcommits.org/) specification, automatically infers the next Semantic Version, compiles a structured `CHANGELOG.md`, and creates annotated tags with zero configuration required.

---

## ✨ Features

- **Zero External Dependencies**: Powered entirely by the Python standard library. Instant startup, no dependency bloat.
- **Smart SemVer Inference**: Automatically detects whether changes require a `MAJOR`, `MINOR`, or `PATCH` bump:
  - `feat!:` or `BREAKING CHANGE:` ➔ **MAJOR**
  - `feat:` ➔ **MINOR**
  - `fix:`, `perf:`, `refactor:`, etc. ➔ **PATCH**
- **Clean Grouped Changelog**: Categorizes commits with emojis and scopes into standardized markdown releases.
- **Dry-Run & Preview**: Inspect changelog output and target version before touching Git tags or files.
- **Drop-in CLI**: Works seamlessly inside local developer workflows or GitHub Actions / CI pipelines.

---

## 🚀 Quick Start

### Installation

Install via pip:

```bash
pip install releasy
```

Or clone and run locally:

```bash
git clone https://github.com/monneverera/releasy.git
cd releasy
pip install -e .
```

---

## 🛠️ Usage

### 1. Check Status
Inspect unreleased commits and see the recommended SemVer bump:

```bash
releasy
# or: releasy status
```

### 2. Preview Release Notes
Generate and preview the upcoming release changelog in your terminal without modifying anything:

```bash
releasy preview
```

### 3. Create a Release
Generate changelog, commit changes, and create the git tag:

```bash
# Automated release (interactive confirmation)
releasy release

# Non-interactive / CI release
releasy release --yes

# Dry run mode
releasy release --dry-run

# Override SemVer bump
releasy release --bump minor
```

---

## 📋 Conventional Commit Conventions

`releasy` groups your commits into clean categories:

| Prefix | Section in Changelog | SemVer Impact |
| :--- | :--- | :--- |
| `feat:` | 🚀 Features | **Minor** |
| `fix:` | 🐛 Bug Fixes | **Patch** |
| `perf:` | ⚡ Performance | **Patch** |
| `refactor:` | ♻️ Code Refactoring | **Patch** |
| `docs:` | 📝 Documentation | **Patch** |
| `chore:`, `ci:`, `test:` | 🔧 Maintenance / Tests | **Patch** |
| `*!:` or `BREAKING CHANGE:` | 💥 Breaking Changes | **Major** |

---

## 📄 License

MIT © [Remon](https://github.com/monneverera) & Orion (Lumen Lab)
