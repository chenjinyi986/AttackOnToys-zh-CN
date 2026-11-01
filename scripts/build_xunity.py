"""把 translation/zh-CN/*.tsv 构建成 XUnity 译文文件，并做一致性检查。

输出到 workshop/build/Translation/zh-CN/Text/：
- AttackOnToys_zh-CN.txt  普通条目（混合大小写的原文会自动补一条全大写版本）
- AttackOnToys_regex.txt  r: / sr: 正则条目

用法：
  python build_xunity.py            # 只构建 + 检查
  python build_xunity.py --deploy   # 构建后复制到游戏 BepInEx/Translation/zh-CN/Text/
"""
import json
import re
import shutil
import sys

from common import GAME_DIR, ROOT, TRANSLATION_DIR
from xunity_format import escape, parse_xunity_line, read_tsv, xunity_line

# Unity 旧版 Text 只在空格处断行：中文段落里夹一个空格，后面整段中文会被当成一个"单词"挤到下一行。
# 所以构建时去掉中文与英文/数字之间的空格。
CJK = r"[　-〿一-鿿＀-￯“”‘’…]"
CJK_GAP = re.compile(rf"(?<={CJK}) (?=[A-Za-z0-9])|(?<=[A-Za-z0-9®]) (?={CJK})")


def tighten(zh: str) -> str:
    return CJK_GAP.sub("", zh)

OUT_DIR = ROOT / "workshop" / "build" / "Translation" / "zh-CN" / "Text"
GAME_TEXT_DIR = GAME_DIR / "BepInEx" / "Translation" / "zh-CN" / "Text"
SRC_DIR = TRANSLATION_DIR / "source"


def is_regex(src: str) -> bool:
    return src.startswith(('r:"', 'sr:"'))


def source_pool() -> set:
    pool = set()
    for path in SRC_DIR.glob("runtime_autogen*.txt"):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            kv = parse_xunity_line(line)
            if kv:
                pool.add(kv[0])
    for name in ("ui_texts.json", "data_strings.json", "code_strings.json"):
        for item in json.loads((SRC_DIR / name).read_text(encoding="utf-8")):
            pool.add(item["text"])
    for line in (SRC_DIR / "observed.txt").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            pool.add(line)
    pool |= {s.strip() for s in pool} | {s.upper() for s in pool} | {s.strip().upper() for s in pool}
    # 训练营对话显示时游戏会在碎片末尾补一个句号
    pool |= {s + "." for s in pool}
    return pool


# 对话里插入的按键显示为 ":键:"，手柄绑定则是 "::TAP: 键:" / "::HOLD: 键:"（键名后可能带空格）。
# 正则行里写 {KEY}，构建时展开成三条；XUnity 先试文件靠后的规则，所以通用写法放最前。
KEY_VARIANTS = [
    (":+([^:]+?) ?:", "【$1】"),
    (":+:TAP: (.+?) ?:", "【点按 $1】"),
    (":+:HOLD: (.+?) ?:", "【长按 $1】"),
]
LEVELED_KINDS = {"TOWER", "TROOP"}
MAX_LEVEL = 5


def expand_keys(src: str, zh: str):
    if "{KEY}" not in src:
        return [(src, zh)]
    return [(src.replace("{KEY}", pat), zh.replace("{KEY}", rep)) for pat, rep in KEY_VARIANTS]


def item_names(kinds=None) -> set:
    data = json.loads((SRC_DIR / "items.json").read_text(encoding="utf-8"))
    return {it["name"].strip() for it in data["items"] if kinds is None or it["kind"] in kinds}


def leveled_names() -> set:
    """会以 "名称 Lv.N" 形式出现在名牌上的单位/建筑名（XUnity 的 sr: 拆分在这类名牌上实测不生效）。"""
    return item_names(LEVELED_KINDS)


def main():
    pool = source_pool()
    entries = {}  # src -> (zh, 文件名)
    regex = []
    warnings = []
    for path in sorted((TRANSLATION_DIR / "zh-CN").glob("*.tsv")):
        for src, zh, _ in read_tsv(path):
            if not zh:
                continue
            if is_regex(src):
                # 正则键里没有 '='，只需转义换行和反斜杠
                for s, z in expand_keys(src, zh):
                    regex.append(f"{escape(s)}={escape(z)}")
                continue
            if "dialog" in path.name and src.endswith("."):
                # 训练营对话：开场军官的字幕会补句号，岗位 NPC 的不补，两种都要。
                # 游戏显示时每行前面有一个空格；只按去空格的键匹配时 XUnity 会把空格加回译文开头，
                # 长句换行时 Unity 会在这个空格处断开，多出一个空行。所以再生成带前导空格的键，让它精确命中。
                for variant in (src[:-1], " " + src, " " + src[:-1]):
                    if variant.strip() and variant not in entries:
                        entries[variant] = (tighten(zh), "生成：对话变体")
            if src not in pool and src.upper() not in pool:
                warnings.append(f"[未在原文池中] {path.name}: {src[:80]!r}")
            zh = tighten(zh)
            if src in entries and entries[src][0] != zh:
                warnings.append(f"[译文冲突] {src!r}: {entries[src][1]}={entries[src][0]!r} vs {path.name}={zh!r}")
            entries[src] = (zh, path.name)

    for name in sorted(leveled_names()):
        if name in entries:
            zh = entries[name][0]
            for lv in range(1, MAX_LEVEL + 1):
                entries.setdefault(f"{name} Lv.{lv}", (f"{zh} Lv.{lv}", "生成：等级名称"))
    # 属性栏第一行 "NAME: 大写名称"：游戏分段拼接属性栏，整块规则不可靠，按行逐条命中
    for name in sorted(item_names()):
        if name in entries:
            entries.setdefault(f"NAME: {name.upper()}", (f"名称：{entries[name][0]}", "生成：属性栏名称"))

    lines = []
    explicit = set(entries)
    for src, (zh, origin) in entries.items():
        lines.append(xunity_line(src, zh))
        if origin.startswith("生成"):
            continue
        up = src.upper()
        if up != src and up not in explicit:
            lines.append(xunity_line(up, zh))
            explicit.add(up)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    header = "// Attack on Toys 简体中文汉化 —— 由 scripts/build_xunity.py 生成，请勿手改\n"
    (OUT_DIR / "AttackOnToys_zh-CN.txt").write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    (OUT_DIR / "AttackOnToys_regex.txt").write_text(header + "\n".join(regex) + "\n", encoding="utf-8")
    print(f"entries: {len(entries)} (+{len(lines) - len(entries)} 大写变体), regex: {len(regex)}")
    for w in warnings:
        print(w)

    if "--deploy" in sys.argv:
        GAME_TEXT_DIR.mkdir(parents=True, exist_ok=True)
        (GAME_TEXT_DIR / "dev_test.txt").unlink(missing_ok=True)
        for f in OUT_DIR.glob("*.txt"):
            shutil.copy2(f, GAME_TEXT_DIR / f.name)
        print(f"deployed to {GAME_TEXT_DIR}")


if __name__ == "__main__":
    main()
