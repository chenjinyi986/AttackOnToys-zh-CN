"""从 data.unity3d 提取所有 UnityEngine.UI.Text 的 m_Text。

输出：
- translation/source/ui_texts.json  去重后的文本，带出现次数、场景、节点路径样例（入库）
- extracted/ui_text_occurrences.jsonl  每个组件一行（不入库，供后续资源补丁定位）
"""
import collections
import json
import sys

from common import ROOT, TRANSLATION_DIR, load_env
from mb_index import build_script_index, external_name, read_header, read_ui_text, script_of


def scene_names(env):
    for obj in env.objects:
        if obj.type.name == "BuildSettings":
            return [s.split("/")[-1].removesuffix(".unity") for s in obj.parse_as_object().scenes]
    return []


class Hierarchy:
    """按 GameObject 计算层级路径，带缓存。"""

    def __init__(self):
        self.cache = {}

    def _get(self, sf, pptr):
        fid, pid = pptr
        if pid == 0 or fid != 0:
            return None
        return sf.objects.get(pid)

    def path(self, sf, go_pid):
        key = (sf.name, go_pid)
        if key in self.cache:
            return self.cache[key]
        go_reader = sf.objects.get(go_pid)
        if go_reader is None:
            return "?"
        go = go_reader.parse_as_object()
        name = go.m_Name
        parent_path = ""
        try:
            tr = go.m_Component[0].component.deref_parse_as_object()
            father = tr.m_Father
            if father.m_PathID:
                ftr = father.deref_parse_as_object()
                parent_path = self.path(sf, ftr.m_GameObject.m_PathID)
        except Exception:  # noqa: BLE001
            pass
        result = f"{parent_path}/{name}" if parent_path else name
        self.cache[key] = result
        return result


def main():
    env = load_env(with_typetree=False)
    idx = build_script_index(env)
    scenes = scene_names(env)
    hier = Hierarchy()

    def where(sf_name):
        if sf_name.startswith("level"):
            i = int(sf_name[5:])
            return f"{sf_name}:{scenes[i]}" if i < len(scenes) else sf_name
        return sf_name

    out_dir = ROOT / "extracted"
    out_dir.mkdir(exist_ok=True)
    uniq = collections.OrderedDict()
    fonts = collections.Counter()
    errors = 0
    with (out_dir / "ui_text_occurrences.jsonl").open("w", encoding="utf-8") as occ:
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            raw = obj.get_raw_data()
            h = read_header(raw)
            sc = script_of(obj, h, idx)
            if not sc or sc[1] != "UnityEngine.UI.Text":
                continue
            sf = obj.assets_file
            try:
                t = read_ui_text(raw, h)
            except Exception as e:  # noqa: BLE001
                errors += 1
                print(f"parse error {sf.name}:{obj.path_id}: {e}", file=sys.stderr)
                continue
            font_key = f"{external_name(sf, t.font[0])}:{t.font[1]}"
            fonts[font_key] += 1
            path = hier.path(sf, h.game_object[1])
            rec = {
                "file": sf.name,
                "path_id": obj.path_id,
                "go": path,
                "font": font_key,
                "size": t.font_size,
                "rich": t.rich_text,
                "text": t.text,
            }
            occ.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if not t.text.strip():
                continue
            u = uniq.setdefault(t.text, {"text": t.text, "count": 0, "where": set(), "samples": []})
            u["count"] += 1
            u["where"].add(where(sf.name))
            if len(u["samples"]) < 3 and path not in u["samples"]:
                u["samples"].append(path)

    items = []
    for u in uniq.values():
        u["where"] = sorted(u["where"])
        items.append(u)
    dst = TRANSLATION_DIR / "source" / "ui_texts.json"
    dst.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"unique non-empty texts: {len(items)}, parse errors: {errors}")
    print("fonts used:", fonts.most_common())
    print("scenes:", scenes)


if __name__ == "__main__":
    main()
