#!/usr/bin/env python3
"""Hide / reveal / remove an invisible string in text using zero-width characters.

Encoding: UTF-8 bytes -> bits; 0 = U+200B, 1 = U+200C.
Payload wrapped as U+2060 <bits> U+2063 so it can be found again.

Usage:
  zwmark.py embed   -t "標記字串" [-i in.md] [-o out.md] [--mode paragraphs|first|end|at:N]
  zwmark.py extract [-i in.md]
  zwmark.py strip   [-i in.md] [-o out.md] [--all]
  zwmark.py inspect [-i in.md]
Without -i reads stdin; without -o writes stdout.
"""
import argparse
import re
import sys

ZERO, ONE = "​", "‌"
START, END = "⁠", "⁣"
PAYLOAD_RE = re.compile(START + "([" + ZERO + ONE + "]+)" + END)
ALL_INVISIBLE_RE = re.compile("[​‌‍⁠⁡⁢⁣⁤﻿­᠎]")
NAMES = {
    "​": "ZERO WIDTH SPACE", "‌": "ZERO WIDTH NON-JOINER",
    "‍": "ZERO WIDTH JOINER", "⁠": "WORD JOINER",
    "⁡": "FUNCTION APPLICATION", "⁢": "INVISIBLE TIMES",
    "⁣": "INVISIBLE SEPARATOR", "⁤": "INVISIBLE PLUS",
    "﻿": "ZERO WIDTH NO-BREAK SPACE (BOM)", "­": "SOFT HYPHEN",
    "᠎": "MONGOLIAN VOWEL SEPARATOR",
}


def encode(s):
    bits = "".join(f"{b:08b}" for b in s.encode("utf-8"))
    return START + bits.replace("0", ZERO).replace("1", ONE) + END


def decode(zw):
    bits = zw.replace(ZERO, "0").replace(ONE, "1")
    if len(bits) % 8:
        raise ValueError("bit length not multiple of 8")
    data = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
    return data.decode("utf-8")


def read_input(path):
    if path:
        with open(path, encoding="utf-8-sig", newline="") as f:
            return f.read()
    return sys.stdin.buffer.read().decode("utf-8-sig")


def write_output(path, text):
    if path:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
    else:
        sys.stdout.buffer.write(text.encode("utf-8"))


def eligible_paragraph_ends(text):
    """Offsets where the mark can go: end of each prose paragraph.

    Skips fenced code blocks, tables, horizontal rules, HTML-only lines and
    blank lines, so Markdown rendering is not broken.
    """
    ends = []
    in_fence = False
    lines = text.splitlines(keepends=True)
    pos = 0
    para_end = None  # offset just before newline of last prose line in current paragraph
    for line in lines:
        body = line.rstrip("\r\n")
        stripped = body.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            if para_end is not None:
                ends.append(para_end)
                para_end = None
        elif in_fence:
            pass
        elif not stripped:
            if para_end is not None:
                ends.append(para_end)
                para_end = None
        elif (stripped.startswith("|") or re.fullmatch(r"[-*_=\s]{3,}", stripped)
              or (stripped.startswith("<") and stripped.endswith(">"))):
            if para_end is not None:
                ends.append(para_end)
                para_end = None
        else:
            para_end = pos + len(body)
        pos += len(line)
    if para_end is not None:
        ends.append(para_end)
    return ends


def embed(text, secret, mode):
    mark = encode(secret)
    if mode == "end":
        stripped = text.rstrip("\r\n")
        return stripped + mark + text[len(stripped):], 1
    if mode.startswith("at:"):
        n = int(mode[3:])
        n = max(0, min(n, len(text)))
        return text[:n] + mark + text[n:], 1
    ends = eligible_paragraph_ends(text)
    if not ends:
        return text + mark, 1
    if mode == "first":
        ends = ends[:1]
    elif mode != "paragraphs":
        sys.exit(f"unknown mode: {mode}")
    for off in reversed(ends):
        text = text[:off] + mark + text[off:]
    return text, len(ends)


def main():
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("embed"); p.add_argument("-t", "--text", required=True)
    p.add_argument("-i"); p.add_argument("-o"); p.add_argument("--mode", default="paragraphs")
    p = sub.add_parser("extract"); p.add_argument("-i")
    p = sub.add_parser("strip"); p.add_argument("-i"); p.add_argument("-o")
    p.add_argument("--all", action="store_true", help="remove every invisible char, not only our marks")
    p = sub.add_parser("inspect"); p.add_argument("-i")
    a = ap.parse_args()

    text = read_input(a.i)
    if a.cmd == "embed":
        out, n = embed(text, a.text, a.mode)
        write_output(a.o, out)
        print(f"[zwmark] inserted {n} mark(s), {len(encode(a.text))} invisible chars each", file=sys.stderr)
    elif a.cmd == "extract":
        found = {}
        for m in PAYLOAD_RE.finditer(text):
            try:
                s = decode(m.group(1))
            except (ValueError, UnicodeDecodeError):
                s = "<corrupted>"
            found[s] = found.get(s, 0) + 1
        if not found:
            print("NO MARK FOUND")
            sys.exit(1)
        out = "".join(f"{s}\t(x{c})\n" for s, c in found.items())
        sys.stdout.buffer.write(out.encode("utf-8"))
    elif a.cmd == "strip":
        rx = ALL_INVISIBLE_RE if a.all else PAYLOAD_RE
        out, n = rx.subn("", text)
        write_output(a.o, out)
        print(f"[zwmark] removed {n} {'char(s)' if a.all else 'mark(s)'}", file=sys.stderr)
    elif a.cmd == "inspect":
        counts = {}
        for ch in ALL_INVISIBLE_RE.findall(text):
            counts[ch] = counts.get(ch, 0) + 1
        marks = len(PAYLOAD_RE.findall(text))
        lines = [f"visible length: {len(ALL_INVISIBLE_RE.sub('', text))}",
                 f"invisible chars: {sum(counts.values())}",
                 f"zwmark payloads: {marks}"]
        lines += [f"  U+{ord(c):04X} {NAMES[c]}: {n}" for c, n in sorted(counts.items())]
        sys.stdout.buffer.write(("\n".join(lines) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
