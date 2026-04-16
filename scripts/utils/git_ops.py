"""Git operations for automated commits."""

import subprocess
from pathlib import Path


def git_commit_and_push(root: Path, message: str, paths: list[str] | None = None) -> bool:
    """Stage specified paths (or data/ + images/), commit, and push.

    Returns True if a commit was made, False if nothing to commit.
    """
    cwd = str(root)
    targets = paths or ["data/", "images/"]

    for t in targets:
        subprocess.run(["git", "add", t], cwd=cwd, check=True)

    diff = subprocess.run(
        ["git", "diff", "--staged", "--quiet"],
        cwd=cwd,
    )
    if diff.returncode == 0:
        print("No changes to commit.")
        return False

    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=cwd,
        check=True,
    )
    subprocess.run(
        ["git", "push"],
        cwd=cwd,
        check=True,
    )
    print(f"Pushed: {message}")
    return True
