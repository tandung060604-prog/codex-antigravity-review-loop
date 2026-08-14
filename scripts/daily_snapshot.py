"""Print a compact, read-only daily repository snapshot."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        return f"UNKNOWN (git {args[0]} failed: {result.stderr.strip()})"
    return result.stdout.strip() or "NONE"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".", help="repository directory")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists():
        raise SystemExit(f"not a Git repository: {repo}")

    print(f"REPO: {repo}")
    print("BRANCH:")
    print(run_git(repo, "status", "--short", "--branch"))
    print("DIFF_STAT:")
    print(run_git(repo, "diff", "--stat", "HEAD"))
    print("RECENT_COMMITS:")
    print(run_git(repo, "log", "-5", "--oneline", "--decorate"))
    print("STATE_FILES:")
    state_dir = repo / "docs" / "agent"
    if state_dir.is_dir():
        for name in ("PROJECT_STATE.md", "BACKLOG.md", "HANDOFF.md"):
            path = state_dir / name
            print(f"- {name}: {'PRESENT' if path.is_file() else 'MISSING'}")
    else:
        print("- docs/agent: MISSING (create only when using codex-longrun)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
