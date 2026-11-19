#!/usr/bin/env python3
"""Entry point for the 19 November 2026 news-image entry.

The graded image is entry.png, sitting next to this file: a newspaper
front page drawn for Thursday 19 November 2026 (built locally by
generate.py from stories.json). All this program does is place an exact
copy of that PNG at $MAKEFUN_OUTPUT_DIR/entry.png, so the graded run is
byte-for-byte identical every time it runs. Standard library only.
"""

import os
import shutil

SOURCE_NAME = "entry.png"


def resolve_output_dir():
    """Where the grader wants the image; /output when unset."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    target_dir = resolve_output_dir()
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, SOURCE_NAME)
    shutil.copyfile(source, target)
    print("copied", source, "->", target, os.path.getsize(target), "bytes")


if __name__ == "__main__":
    main()
