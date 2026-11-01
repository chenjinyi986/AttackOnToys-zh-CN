"""从 global-metadata.dat 提取 IL2CPP 字符串字面量（代码里硬编码的文本，例如运行时拼接的提示语）。

输出 translation/source/code_strings.json：全部字面量（含索引），后续按需筛选 UI 文本。
"""
import json
import struct

from common import METADATA, TRANSLATION_DIR


def main():
    data = METADATA.read_bytes()
    sanity, version = struct.unpack_from("<Ii", data, 0)
    assert sanity == 0xFAB11BAF, hex(sanity)
    lit_off, lit_size, lit_data_off, lit_data_size = struct.unpack_from("<iiii", data, 8)
    items = []
    for i in range(lit_size // 8):
        length, index = struct.unpack_from("<Ii", data, lit_off + i * 8)
        s = data[lit_data_off + index : lit_data_off + index + length].decode("utf-8", errors="replace")
        items.append({"index": i, "text": s})
    dst = TRANSLATION_DIR / "source" / "code_strings.json"
    dst.write_text(json.dumps(items, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"metadata version {version}, string literals: {len(items)}")


if __name__ == "__main__":
    main()
