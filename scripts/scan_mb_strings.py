"""启发式扫描 Assembly-CSharp 组件里的字符串字段（无 TypeTree，只用于估算数据驱动文本的量级）。

输出 translation/source/data_strings.json：去重字符串 + 来源脚本类 + 次数。
"""
import collections
import json
import re
import struct

from common import TRANSLATION_DIR, load_env
from mb_index import align4, build_script_index, read_header, script_of

WORDY = re.compile(r"[A-Za-z]{2,}")


def iter_strings(raw: bytes, start: int):
    """扫描 4 字节对齐的 int32 长度前缀 + UTF-8 文本。"""
    pos = start
    end = len(raw)
    while pos + 4 <= end:
        n = struct.unpack_from("<i", raw, pos)[0]
        if 2 <= n <= 4000 and pos + 4 + n <= end:
            b = raw[pos + 4 : pos + 4 + n]
            if all(c >= 0x20 or c in (9, 10, 13) for c in b):
                try:
                    s = b.decode("utf-8")
                except UnicodeDecodeError:
                    s = None
                if s and WORDY.search(s):
                    yield s
                    pos = align4(pos + 4 + n)
                    continue
        pos += 4


def main():
    env = load_env(with_typetree=False)
    idx = build_script_index(env)
    found = {}
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        raw = obj.get_raw_data()
        h = read_header(raw)
        sc = script_of(obj, h, idx)
        if not sc or sc[0] != "Assembly-CSharp.dll":
            continue
        for s in iter_strings(raw, h.end):
            e = found.setdefault(s, {"text": s, "count": 0, "scripts": collections.Counter()})
            e["count"] += 1
            e["scripts"][sc[1]] += 1
    items = []
    for e in found.values():
        e["scripts"] = dict(e["scripts"].most_common(5))
        items.append(e)
    items.sort(key=lambda e: (-e["count"], e["text"]))
    dst = TRANSLATION_DIR / "source" / "data_strings.json"
    dst.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    by_script = collections.Counter()
    for e in items:
        for k in e["scripts"]:
            by_script[k] += 1
    print(f"unique strings: {len(items)}")
    for k, v in by_script.most_common(30):
        print(v, k)


if __name__ == "__main__":
    main()
