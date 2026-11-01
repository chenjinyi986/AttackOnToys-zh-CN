"""把 logs/captured_texts.jsonl（capture_server 的原始记录）去重合并进 translation/source/runtime_texts.json。

已存在的条目保留原顺序，新条目追加在末尾，可反复运行。
"""
import json

from common import LOGS_DIR, TRANSLATION_DIR

SRC = LOGS_DIR / "captured_texts.jsonl"
DST = TRANSLATION_DIR / "source" / "runtime_texts.json"


def main():
    items = json.loads(DST.read_text(encoding="utf-8")) if DST.exists() else []
    known = set(items)
    added = 0
    for line in SRC.read_text(encoding="utf-8").splitlines():
        text = json.loads(line)["text"]
        if text == "ping" or text in known:
            continue
        known.add(text)
        items.append(text)
        added += 1
    DST.write_text(json.dumps(items, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"runtime texts: {len(items)} (+{added})")


if __name__ == "__main__":
    main()
