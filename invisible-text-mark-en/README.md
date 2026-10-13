# Invisible Text Mark (English Edition): User Guide

Hide a string of your choice inside an article as **zero-width characters**. Readers see nothing, the article looks and reads exactly the same, but the string is still there and can be read back later.

Typical uses:

- Tag your own articles with an author name, date or version number
- Give each recipient a different tracking code, so a leaked or reposted copy tells you where it came from
- Check whether a piece of text someone sent you contains hidden characters, and clean them out

> Chinese edition: [`../invisible-text-mark`](../invisible-text-mark/README.md). Each edition only triggers on requests in its own language, so you can install both.

---

## Quick start

In Claude Code:

```
/invisible-text-mark-en hide "Author: Alex #2026-001" in ~/drafts/post.md
```

Claude writes `post.marked.md` next to the original, reads the mark back to verify it, and tells you how many copies were inserted.

You can also just ask:

- "Add an invisible watermark `client-A` to this article"
- "Does this text have any invisible characters in it?"
- "Read the hidden mark in `leaked.txt`"
- "Strip all invisible characters from this file"

---

## How it works

Each byte of the string (UTF-8) becomes 8 bits. A `0` is written as U+200B (ZERO WIDTH SPACE) and a `1` as U+200C (ZERO WIDTH NON-JOINER). The bits are wrapped in U+2060 (WORD JOINER) and U+2063 (INVISIBLE SEPARATOR) so the mark can be found again.

```
"x"  ->  01111000  ->  U+2060 · 200B 200C 200C 200C 200C 200B 200B 200B · U+2063
```

Each ASCII character costs 8 invisible characters and each Chinese character costs 24, plus 2 for the wrapper.

## Placement modes

| `--mode` | Where | When to use |
|----------|-------|-------------|
| `paragraphs` (default) | End of every prose paragraph | Survives someone copying only part of the article |
| `first` | End of the first paragraph | Fewer hidden characters |
| `end` | End of the whole text | Minimal footprint, but lost on partial copies |
| `at:N` | Right after character N | Exact control |

`paragraphs` and `first` skip fenced code blocks, tables, horizontal rules and HTML-only lines, so Markdown still renders correctly.

---

## Using the script directly

The skill wraps `scripts/zwmark.py`, which works on its own (Python 3, standard library only). Without `-i` it reads stdin; without `-o` it writes stdout.

```bash
# Hide a string
python zwmark.py embed -t "Author: Alex #2026-001" -i post.md -o post.marked.md

# Read it back
python zwmark.py extract -i post.marked.md
# Author: Alex #2026-001	(x3)

# Count invisible characters of any kind
python zwmark.py inspect -i post.marked.md

# Remove this tool's marks only
python zwmark.py strip -i post.marked.md -o post.clean.md

# Remove every invisible character (also catches marks from other tools)
python zwmark.py strip --all -i suspicious.txt -o clean.txt
```

`extract` exits with code 1 and prints `NO MARK FOUND` when there is no mark, so it works in scripts.

---

## Limitations

- **Not encryption.** Anyone who knows the technique can read or delete the mark.
- **Some places drop it:** certain social networks, SMS, plain-text form fields, screenshots and OCR.
- **Retyping or cleaning removes it**, e.g. running `strip --all` or any "remove zero-width characters" tool.
- **Word / Google Docs:** pasting the text in usually keeps the mark. Copy it back out and run `extract` to confirm.

## What it won't do

The skill refuses to hide **instructions aimed at an AI** (for example a hidden "ignore previous instructions" or "give this resume a high score" in a resume, homework or web page). That is prompt injection and it misleads whoever relies on the AI's review. Use it for marks, not messages to machines.

---

## Installation

```bash
git clone https://github.com/lng255639-cpu/invisible-text-mark.git
cp -r invisible-text-mark/invisible-text-mark-en ~/.claude/skills/
```

Start a new Claude Code session afterwards.

## Uninstall

```bash
rm -rf ~/.claude/skills/invisible-text-mark-en
```
