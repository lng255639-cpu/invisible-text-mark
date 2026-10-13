# Invisible Text Mark

A [Claude Code](https://claude.com/claude-code) skill that hides a string inside an article as **zero-width characters**. Readers see nothing, but the mark can be read back later: tag your writing with an author or tracking code, find out where a leaked copy came from, or check text for hidden characters.

用**零寬字元**把字串藏進文章的 Claude Code skill。讀者看不到，之後可以讀出來：替文章加作者或追蹤碼、查出外流的版本是哪一份，或檢查文字裡有沒有藏東西。

```
/invisible-text-mark-en hide "client-A" in post.md
```

```
$ python zwmark.py extract -i post.marked.md
client-A	(x3)
```

## Editions / 版本

| Edition | Folder | Command | Guide |
|---------|--------|---------|-------|
| 繁體中文 | [`invisible-text-mark/`](invisible-text-mark/) | `/invisible-text-mark` | [使用說明](invisible-text-mark/README.md) |
| English | [`invisible-text-mark-en/`](invisible-text-mark-en/) | `/invisible-text-mark-en` | [User guide](invisible-text-mark-en/README.md) |

Each edition only triggers on requests in its own language, so installing both is fine.
兩個版本各自只回應自己語言的請求，可以兩個都裝。

## Quick install / 快速安裝

```bash
git clone https://github.com/lng255639-cpu/invisible-text-mark.git
cp -r invisible-text-mark/invisible-text-mark-en ~/.claude/skills/   # English
cp -r invisible-text-mark/invisible-text-mark ~/.claude/skills/      # 繁體中文
```

Start a new Claude Code session afterwards. / 裝好後開新對話。

The script `zwmark.py` also works on its own (Python 3, no dependencies). / `zwmark.py` 也可以單獨使用（Python 3，免安裝套件）。

## Not for prompt injection / 不用於 prompt injection

The skill refuses to hide instructions aimed at an AI (e.g. hidden "give this resume a high score" text). It is for marks, not messages to machines.
skill 會拒絕藏給 AI 看的指令（例如在履歷裡藏「給高分」）。這是做標記用的，不是對機器傳話用的。

## License

[MIT](LICENSE)
