"""校验译文分块：python check_chunk.py <todo.tsv> <译文.tsv>

检查原文列与待译表逐行一致（顺序、空格、转义都不能变），并统计已译/留空条目。
"""
import re
import sys
from pathlib import Path

from xunity_format import read_tsv

CJK = re.compile(r"[一-鿿]")


def main():
    todo = read_tsv(Path(sys.argv[1]))
    done = read_tsv(Path(sys.argv[2]))
    problems = []
    if len(todo) != len(done):
        problems.append(f"行数不一致：待译 {len(todo)}，译文 {len(done)}")
    for i, ((src_a, _, _), (src_b, zh, _)) in enumerate(zip(todo, done), start=2):
        if src_a != src_b:
            problems.append(f"第 {i} 行原文被改动：{src_a!r} -> {src_b!r}")
        if zh and not CJK.search(zh):
            problems.append(f"第 {i} 行译文没有中文：{zh!r}")
    filled = sum(1 for _, zh, _ in done if zh)
    print(f"已译 {filled} / {len(done)}，留空 {len(done) - filled}")
    for p in problems[:50]:
        print(p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
