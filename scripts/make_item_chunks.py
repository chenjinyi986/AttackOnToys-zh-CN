"""把 items.json 切成待译分块 translation/todo/items_<n>.tsv（跳过已在 zh-CN/*.tsv 里出现的原文）。

note 列给出上下文：kind | GameObject 名，说明行标注所属物品名。
"""
import json

from common import TRANSLATION_DIR
from xunity_format import read_tsv, tsv_line

CHUNKS = {
    "1_troops": lambda it: it["kind"] in {"TROOP", "PLAYER", "BUCKET", "DIALOG", "SPAWN POINT", "BULLET", "RAY"},
    "2_items_towers": lambda it: it["kind"] in {"ITEM", "TOWER"},
    "3_props_a": None,
    "4_props_b": None,
    "5_categories": None,
}


def main():
    data = json.loads((TRANSLATION_DIR / "source" / "items.json").read_text(encoding="utf-8"))
    done = set()
    for p in (TRANSLATION_DIR / "zh-CN").glob("*.tsv"):
        for src, _, _ in read_tsv(p):
            done |= {src, src.strip(), src.upper()}

    seen = set()

    def rows_for(items):
        rows = []
        for it in items:
            for text, note in ((it["name"], f'{it["kind"]} | {it["go"]}'), (it["desc"], f'说明：{it["name"].strip()}')):
                if text and text not in seen and text.strip() not in done:
                    seen.add(text)
                    rows.append(tsv_line(text, "", note))
        return rows

    items = data["items"]
    props = [it for it in items if it["kind"] not in {"TROOP", "ITEM", "TOWER", "PLAYER", "BUCKET", "DIALOG", "SPAWN POINT", "BULLET", "RAY"}]
    half = len(props) // 2
    out = {
        "1_troops": rows_for([it for it in items if CHUNKS["1_troops"](it)]),
        "2_items_towers": rows_for([it for it in items if CHUNKS["2_items_towers"](it)]),
        "3_props_a": rows_for(props[:half]),
        "4_props_b": rows_for(props[half:]),
    }
    cats = []
    for c in data["toybox_categories"]:
        if c not in seen and c.strip() not in done:
            seen.add(c)
            cats.append(tsv_line(c, "", "玩具箱分类"))
    out["5_categories"] = cats

    todo = TRANSLATION_DIR / "todo"
    todo.mkdir(exist_ok=True)
    for name, rows in out.items():
        (todo / f"items_{name}.tsv").write_text("src\tzh\tnote\n" + "\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        print(f"items_{name}.tsv: {len(rows)} rows")


if __name__ == "__main__":
    main()
