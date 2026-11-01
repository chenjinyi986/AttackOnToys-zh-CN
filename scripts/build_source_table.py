"""合并各原文来源，生成待译表 translation/todo/<批次>.tsv。

已在 translation/zh-CN/*.tsv 中出现的原文会被跳过，所以可以反复运行来找新增文本。

用法：python build_source_table.py ui
"""
import json
import re
import sys

from common import TRANSLATION_DIR
from xunity_format import parse_xunity_line, read_tsv, tsv_line

SRC_DIR = TRANSLATION_DIR / "source"

# 场景里的占位文本，运行时会被代码覆盖
PLACEHOLDERS = {
    "TEXT", "Option A", "Enter text...", "Player Name...", "Title...", "Tittle...", "Short description...",
    "Description Description Description", "Word Word Word", "ERROR ERROR ERROR", "CREDIT\nCREDIT\nCREDIT",
    "Dunkey Here", "SARGEEEE", "MISSION NAME", "MAP NAME", "TROOP NAME", "NAME", "????",
}
PLACEHOLDER_RE = re.compile(r"^(a{8,}|(Mission ){4,}.*|[\W\d_]*|[A-Z]\d?|F\d{1,2}|P\d|LV\.|\d.*)$", re.S)

# 菜单类数据文本所在的脚本类
UI_DATA_SCRIPTS = {
    "MenuSettingValueChangeScript", "MenuGameSettingsScript", "MenuWindowTabManagerScript",
    "SelectMissionMenuDetailsScript", "TowerHQPlayerScript", "BaseMapScript", "WayPointBaseScript",
    "EditPlayerProfileManagerScript", "PlayerScript", "BaseSystemScript",
}


def is_noise(s: str) -> bool:
    t = s.strip()
    if not t or t in PLACEHOLDERS or PLACEHOLDER_RE.match(t) or not re.search(r"[A-Za-z]{2,}", t):
        return True
    if s.count("\r\n") >= 5:  # 制作人员名单
        return True
    if s.startswith(" ") and t.upper() == t:  # 按键绑定里的键名，保留英文
        return True
    return t.startswith((":TAP:", ":HOLD:"))  # 由正则规则处理


def runtime_keys():
    for line in (SRC_DIR / "runtime_autogen.txt").read_text(encoding="utf-8-sig").splitlines():
        kv = parse_xunity_line(line)
        if kv:
            yield kv[0]


def collect_ui():
    found = {}  # src -> set(来源)

    def add(s, tag):
        if not is_noise(s):
            found.setdefault(s, set()).add(tag)

    for s in runtime_keys():
        add(s, "runtime")
    for u in json.loads((SRC_DIR / "ui_texts.json").read_text(encoding="utf-8")):
        add(u["text"], "scene")
    for d in json.loads((SRC_DIR / "data_strings.json").read_text(encoding="utf-8")):
        scripts = set(d["scripts"])
        if scripts & UI_DATA_SCRIPTS and len(d["text"].strip()) > 2 and not d["text"].startswith("["):
            add(d["text"], "data:" + sorted(scripts & UI_DATA_SCRIPTS)[0])
    return found


def main():
    batch = sys.argv[1]
    found = {"ui": collect_ui}[batch]()
    done = set()
    for p in (TRANSLATION_DIR / "zh-CN").glob("*.tsv"):
        for src, _, _ in read_tsv(p):
            done |= {src, src.strip(), src.upper(), src.strip().upper()}
    # 运行时形式（大写）与数据原形重复时只保留一份，构建时会自动补大写变体
    upper_runtime = {s for s, tags in found.items() if "runtime" in tags}
    rows = []
    for s, tags in found.items():
        if s in done or s.strip() in done or s.strip().upper() in done:
            continue
        if "runtime" not in tags and s.upper() in upper_runtime and s != s.upper():
            continue
        rows.append((s, ",".join(sorted(tags))))
    out = TRANSLATION_DIR / "todo" / f"{batch}.tsv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write("src\tzh\tnote\n")
        for s, tags in rows:
            f.write(tsv_line(s, "", tags) + "\n")
    print(f"{out}: {len(rows)} rows")


if __name__ == "__main__":
    main()
