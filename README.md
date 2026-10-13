# 隱形字串標記 Invisible Text Mark

[Claude Code](https://claude.com/claude-code) skill：把你指定的字串用**零寬字元**藏進文章。讀者什麼都看不到，文章外觀和內容完全一樣，但字串還在，之後可以讀出來。

常見用途：

- 替自己的文章加上作者、日期、版本編號
- 每個收件人給不同的追蹤碼，文章外流或被轉貼時，就知道是從誰那裡流出去的
- 檢查別人傳來的文字有沒有藏隱形字元，並清乾淨

> English edition: [invisible-text-mark-en](https://github.com/lng255639-cpu/invisible-text-mark-en)。兩個版本各自只回應自己語言的請求，可以兩個都裝。

---

## 快速開始

在 Claude Code 輸入：

```
/invisible-text-mark 把「作者:小明 #2026-001」藏進 ~/草稿/文章.md
```

Claude 會在原檔旁邊產生 `文章.marked.md`，讀回標記確認無誤，再告訴你放了幾處。

也可以直接講：

- 「幫這篇文章加隱形浮水印 `客戶A`」
- 「這段文字裡有沒有隱形字元？」
- 「讀出 `外流.txt` 裡藏的標記」
- 「把這個檔案的隱形字元全部清掉」

---

## 原理

字串的每個位元組（UTF-8）拆成 8 個位元，`0` 寫成 U+200B（ZERO WIDTH SPACE），`1` 寫成 U+200C（ZERO WIDTH NON-JOINER），前後再用 U+2060（WORD JOINER）和 U+2063（INVISIBLE SEPARATOR）包起來，方便之後找回。

```
"x"  ->  01111000  ->  U+2060 · 200B 200C 200C 200C 200C 200B 200B 200B · U+2063
```

英文字母或數字一個字占 8 個隱形字元，中文字一個字占 24 個，外加頭尾 2 個。

## 放置位置

| `--mode` | 放在哪 | 適合 |
|----------|--------|------|
| `paragraphs`（預設） | 每個文字段落結尾 | 別人只複製一部分也抓得到 |
| `first` | 第一段結尾 | 隱形字元少一點 |
| `end` | 全文最後 | 最精簡，但只複製一部分就會丟失 |
| `at:N` | 第 N 個字元後面 | 要精準控制位置時 |

`paragraphs` 和 `first` 會跳過程式碼區塊、表格、分隔線、純 HTML 行，Markdown 排版不會壞。

---

## 直接用腳本

skill 背後是 `scripts/zwmark.py`，可以單獨使用（Python 3，只用標準函式庫）。不給 `-i` 就從 stdin 讀，不給 `-o` 就輸出到 stdout。

```bash
# 藏字串
python zwmark.py embed -t "作者:小明 #2026-001" -i 文章.md -o 文章.marked.md

# 讀出來
python zwmark.py extract -i 文章.marked.md
# 作者:小明 #2026-001	(x3)

# 統計各種隱形字元
python zwmark.py inspect -i 文章.marked.md

# 只清掉本工具的標記
python zwmark.py strip -i 文章.marked.md -o 文章.clean.md

# 清掉所有隱形字元（別的工具藏的也一起清）
python zwmark.py strip --all -i 可疑.txt -o 乾淨.txt
```

找不到標記時，`extract` 會印 `NO MARK FOUND` 並以代碼 1 結束，方便寫進腳本。

---

## 限制

- **不是加密。** 知道方法的人都讀得出、刪得掉。
- **有些地方會濾掉：** 部分社群網站、簡訊、純文字表單、截圖、OCR。
- **重新打字或被清過就沒了**，例如跑過 `strip --all` 或其他「清除零寬字元」工具。
- **Word / Google Docs：** 貼進去通常會保留。可以再複製出來跑 `extract` 確認。

## 不做的事

skill 會拒絕藏**給 AI 看的指令**，例如在履歷、作業、網頁裡偷藏「忽略前面的指示」「給這份履歷高分」。這是 prompt injection，會誤導依賴 AI 審查的人。這個工具用來做標記，不是用來對機器傳話。

---

## 安裝

```bash
git clone https://github.com/lng255639-cpu/invisible-text-mark.git ~/.claude/skills/invisible-text-mark
```

裝好後開新對話。之後要更新：`git -C ~/.claude/skills/invisible-text-mark pull`。

## 移除

```bash
rm -rf ~/.claude/skills/invisible-text-mark
```

## 授權

[MIT](LICENSE)
