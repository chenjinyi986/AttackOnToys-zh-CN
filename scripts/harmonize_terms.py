"""统一并行翻译产生的术语差异：只改 translation/zh-CN/05_*.tsv 的 zh 列，原文列不动。可重复运行。"""
import re

from common import TRANSLATION_DIR
from xunity_format import read_tsv, tsv_line

# 译文替换规则（按顺序执行）
ZH_RULES = [
    (r" 亮灯$", "（亮）"),
    (r" 开盖$", "（开盖）"),
    (r" 打开$", "（打开）"),
    (r"泳池浮具", "泳池浮排"),
    (r"可缩放半管", "可缩放半圆管"),
    (r"可缩放管体", "可缩放圆管"),
    (r"草皮堆", "草堆"),
    (r"月面土堆", "月壤堆"),
    (r"峭壁", "悬崖"),
    (r"塑料兵玩具桶", "军队玩具桶"),
    (r"驯化", "驯服"),
    (r"浅木色", "浅色木纹"),
    (r"玩具豌豆射手飞机", "玩具“豌豆射手”战斗机"),
]

# 按原文决定译文的规则
SRC_RULES = [
    (re.compile(r"^WoodBlock-([0-9]+)\s*$"), lambda m: f"数字木块 {m.group(1)}"),
    (re.compile(r"^WoodBlock-([A-Z])\s*$"), lambda m: f"字母木块 {m.group(1)}"),
    (re.compile(r"^APC-M116\s*$"), lambda m: "APC-M116 装甲运兵车"),
]


def main():
    changed = 0
    for path in sorted((TRANSLATION_DIR / "zh-CN").glob("05_*.tsv")):
        lines = path.read_text(encoding="utf-8").splitlines()
        rows = read_tsv(path)
        out = [lines[0]]
        for src, zh, note in rows:
            new = zh
            for pat, fn in SRC_RULES:
                m = pat.match(src)
                if m:
                    new = fn(m)
            for pat, rep in ZH_RULES:
                new = re.sub(pat, rep, new)
            if new != zh:
                changed += 1
            out.append(tsv_line(src, new, note))
        path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"changed {changed} rows")


if __name__ == "__main__":
    main()
