# -*- coding: utf-8 -*-
"""
Make scripts/publish.py tolerant of files saved on Windows: strip a UTF-8 BOM
and normalise CRLF line endings before the article is parsed.

Without this, a file whose first line is "\ufeff### Article title (English)"
loses its title field and the workflow fails with "missing required field(s)".
"""
import io
import os
import re
import sys

ROOT = os.getcwd()
TARGET = os.path.join(ROOT, "scripts", "publish.py")

HELPER = '''
def _clean_env_body(text):
    """Strip a UTF-8 BOM and normalise Windows line endings."""
    if not text:
        return text
    return text.replace("\\ufeff", "").replace("\\r\\n", "\\n").replace("\\r", "\\n")


def main():'''


def main():
    if not os.path.isfile(TARGET):
        print("ERROR: scripts/publish.py not found")
        return 1
    s = io.open(TARGET, encoding="utf-8").read()

    if "_clean_env_body" in s:
        print("already BOM-safe, nothing to do")
        return 0

    # 1. insert the helper just before main()
    if s.count("\ndef main():") != 1:
        print("ERROR: could not locate 'def main():' exactly once")
        return 1
    s = s.replace("\ndef main():", HELPER, 1)

    # 2. wrap the environment read
    old = 'body = os.environ.get("ISSUE_BODY", "")'
    if old not in s:
        print("ERROR: could not locate the ISSUE_BODY read")
        return 1
    s = s.replace(old, 'body = _clean_env_body(os.environ.get("ISSUE_BODY", ""))', 1)

    io.open(TARGET, "w", encoding="utf-8", newline="\n").write(s)
    print("publish.py patched: BOM and CRLF are now normalised")
    return 0


if __name__ == "__main__":
    sys.exit(main())
