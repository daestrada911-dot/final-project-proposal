#!/usr/bin/env python3
"""
add-commit-push.py
Automates: git add -A, git commit -m "<msg>", git push

Usage:
  python add-commit-push.py -m "your message"
  python add-commit-push.py -m "your message" -f   # skip confirm
  python add-commit-push.py                         # will prompt for message
"""

import argparse
import subprocess
import sys
from datetime import datetime

def run_and_print(cmd: list[str]) -> int:
    """Print the command, blank line, then execute and print results."""
    # Pretty print the command as a shell-like string for readability
    printable = " ".join(
        f'"{c}"' if (" " in c and not c.startswith("-")) else c for c in cmd
    )
    print(f"$ {printable}\n")
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        # print stderr last so users see errors even if stdout is long
        sys.stdout.flush()
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode

def get_branch_name() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
        ).strip()
        return out
    except subprocess.CalledProcessError:
        return None

def has_upstream() -> bool:
    try:
        subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "@{u}"],
            stderr=subprocess.STDOUT,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False

def ensure_git_repo_or_exit():
    try:
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], text=True)
    except subprocess.CalledProcessError:
        print("Error: This directory is not a Git repository.", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Add, commit, push helper.")
    parser.add_argument("-m", "--message", help="Commit message (optional)")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Skip confirmation prompt")
    args = parser.parse_args()

    ensure_git_repo_or_exit()

    # Requirement 2: print 'git status:' and the results on the next line
    print("git status:")
    rc = run_and_print(["git", "status"])
    if rc != 0:
        print("Aborting because `git status` failed.", file=sys.stderr)
        sys.exit(rc)

    # Determine commit message (optional -m). If missing, prompt once.
    commit_msg = args.message
    if not commit_msg:
        try:
            commit_msg = input('Commit message (leave blank for "update"): ').strip()
        except EOFError:
            commit_msg = ""
        if not commit_msg:
            commit_msg = f"update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    branch = get_branch_name() or "<unknown-branch>"
    push_cmd = ["git", "push"]
    if not has_upstream():
        # If no upstream configured, set it on first push
        push_cmd = ["git", "push", "-u", "origin", branch]

    # Queue the commands
    queued = [
        ["git", "add", "-A"],
        ["git", "commit", "-m", commit_msg],
        push_cmd,
    ]

    # Requirement 2: print the queued commands and ask for confirmation
    print("\nQueued commands:")
    for c in queued:
        printable = " ".join(
            f'"{x}"' if (" " in x and not x.startswith("-")) else x for x in c
        )
        print(f"  {printable}")

    if not args.force:
        confirm = input('\nRun these now? Type "y" to continue: ').strip().lower()
        if confirm != "y":
            print("Canceled.")
            sys.exit(0)

    # Requirement 4: use ONE function (run_and_print) to print command, blank, then results
    failures = 0
    for c in queued:
        code = run_and_print(c)
        print()  # extra spacing between steps
        if code != 0:
            failures += 1
            # If add or commit fails, you can break here; we’ll break on commit failure
            if c[0] == "git" and c[1] == "commit":
                print("Commit failed. Stopping before push.", file=sys.stderr)
                break

    if failures == 0:
        print("✅ Done.")
    else:
        print(f"⚠️ Completed with {failures} error(s).", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
