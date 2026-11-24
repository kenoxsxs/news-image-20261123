#!/usr/bin/env python3
"""main.py — news-image-20261123 v3 entrypoint (standard library only).

Copies the pre-rendered entry.png (committed in this repository) to
/output/entry.png.  The copy is byte-identical on every run: no randomness,
no clock, no network, no fonts, no PIL, no other files read.

The image itself was rendered offline by draw.py (PIL + DejaVu vector
fonts, supersampled 3072x3072 then downscaled to 1024x1024 with LANCZOS).
draw.py is kept in this repo so the picture can be reproduced; the graded
program only copies the finished PNG.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not os.path.exists(SRC):
        print("missing source image: %s" % SRC, file=sys.stderr)
        return 1
    with open(SRC, "rb") as f:
        if f.read(8) != b"\x89PNG\r\n\x1a\n":
            print("source is not a PNG file: %s" % SRC, file=sys.stderr)
            return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    src_hash, dst_hash = _sha256(SRC), _sha256(dst)
    if src_hash != dst_hash:
        print("copy hash mismatch", file=sys.stderr)
        return 1
    print("wrote %s (%d bytes, sha256 %s)" % (dst, os.path.getsize(dst), dst_hash))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
