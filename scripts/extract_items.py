"""提取物品（ProfileDataScript：名称 + 说明）和玩具箱分类（ToyBoxSystem），按 GameObject 前缀分类。

输出 translation/source/items.json：[{name, desc, kind, go}]，kind 取 GameObject 名里的 [XXX] 前缀。
"""
import json
import re

from common import TRANSLATION_DIR, load_env
from mb_index import build_script_index, read_header, script_of
from scan_mb_strings import iter_strings

JUNK = re.compile(r"^[A-Za-z]{2}$")  # 混淆残留的两字母串


def main():
    env = load_env(with_typetree=False)
    idx = build_script_index(env)
    items = {}
    categories = []
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        raw = obj.get_raw_data()
        h = read_header(raw)
        sc = script_of(obj, h, idx)
        if not sc:
            continue
        if sc[1] == "ProfileDataScript" and obj.assets_file.name == "sharedassets0.assets":
            ss = [s for s in iter_strings(raw, h.end) if not JUNK.match(s)]
            if not ss:
                continue
            go = obj.assets_file.objects[h.game_object[1]].parse_as_object().m_Name
            m = re.match(r"\[([A-Z ]+)\]", go)
            name, desc = ss[0], (ss[1] if len(ss) > 1 else "")
            items.setdefault(name, {"name": name, "desc": desc, "kind": m.group(1) if m else "", "go": go})
        elif sc[1] == "ToyBoxSystem" and not categories:
            categories = [s for s in iter_strings(raw, h.end) if not JUNK.match(s)]
    out = {"items": list(items.values()), "toybox_categories": list(dict.fromkeys(categories))}
    (TRANSLATION_DIR / "source" / "items.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    kinds = {}
    for it in items.values():
        kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
    print(f"items: {len(items)}, with desc: {sum(1 for i in items.values() if i['desc'])}, categories: {len(out['toybox_categories'])}")
    print(sorted(kinds.items(), key=lambda kv: -kv[1]))


if __name__ == "__main__":
    main()
