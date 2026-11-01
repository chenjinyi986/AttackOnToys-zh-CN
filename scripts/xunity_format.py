"""XUnity.AutoTranslator 译文文件与项目 TSV 的转义规则。

XUnity 文本文件每行 `原文=译文`，原文里的 `=` 写成 `\\=`，换行写成 `\\n`，回车 `\\r`，反斜杠 `\\\\`。
项目 TSV（src<TAB>zh<TAB>note）用同样的反斜杠转义，另外 TAB 写成 `\\t`。
"""

_ESC = {"\\": "\\\\", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
_UNESC = {"\\": "\\", "n": "\n", "r": "\r", "t": "\t", "=": "="}


def escape(s: str, extra: str = "") -> str:
    out = []
    for ch in s:
        if ch in _ESC:
            out.append(_ESC[ch])
        elif ch in extra:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


def unescape(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] in _UNESC:
            out.append(_UNESC[s[i + 1]])
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def xunity_line(src: str, dst: str) -> str:
    return f"{escape(src, '=')}={escape(dst, '=')}"


def parse_xunity_line(line: str):
    """返回 (原文, 译文)；注释或空行返回 None。"""
    if not line.strip() or line.startswith("//"):
        return None
    i = 0
    while i < len(line):
        if line[i] == "\\":
            i += 2
            continue
        if line[i] == "=":
            return unescape(line[:i]), unescape(line[i + 1 :])
        i += 1
    return None


def read_tsv(path):
    """读取项目 TSV，返回 [(src, zh, note)]。不含 TAB 的行是注释（原文本身可能以 # 开头）。"""
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if n == 0 and line.startswith("src\t"):
            continue
        if "\t" not in line:
            continue
        parts = line.split("\t")
        parts += [""] * (3 - len(parts))
        rows.append((unescape(parts[0]), unescape(parts[1]), parts[2]))
    return rows


def tsv_line(src: str, zh: str = "", note: str = "") -> str:
    return f"{escape(src)}\t{escape(zh)}\t{note}"
