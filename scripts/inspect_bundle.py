"""统计 data.unity3d 的内部文件、对象类型，以及 MonoBehaviour 脚本类的使用次数。"""
import collections
import sys

from common import REPORTS_DIR, load_env
from mb_index import build_script_index, read_header, script_of


def main():
    env = load_env(with_typetree=False)
    idx = build_script_index(env)
    files = collections.Counter()
    types = collections.Counter()
    scripts = collections.Counter()
    for obj in env.objects:
        files[obj.assets_file.name] += 1
        types[obj.type.name] += 1
        if obj.type.name == "MonoBehaviour":
            sc = script_of(obj, read_header(obj.get_raw_data()), idx)
            scripts[f"{sc[0]}:{sc[1]}" if sc else "<missing>"] += 1

    out = REPORTS_DIR / "bundle_inventory.md"
    with out.open("w", encoding="utf-8") as f:
        f.write("# data.unity3d 内容清单\n\n由 `scripts/inspect_bundle.py` 生成。\n\n## 内部文件\n\n")
        for k, v in sorted(files.items()):
            f.write(f"- `{k}`: {v} 个对象\n")
        f.write("\n## 对象类型\n\n")
        for k, v in types.most_common():
            f.write(f"- {k}: {v}\n")
        f.write("\n## MonoBehaviour 脚本类（按使用次数）\n\n")
        for k, v in scripts.most_common():
            f.write(f"- `{k}`: {v}\n")
    print(f"written {out}", file=sys.stderr)
    print("--- scripts top 40")
    for k, v in scripts.most_common(40):
        print(k, v)


if __name__ == "__main__":
    main()
