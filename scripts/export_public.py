"""把本仓库的公开部分同步到 GitHub 用的仓库目录（默认 E:\\Project\\AttackOnToys-zh-CN）。

不导出：Claude 的工作文件（CLAUDE.md、HANDOFF.md、.claude/）、从游戏提取的原始文本（translation/source/）、
资源清单（reports/bundle_inventory.md）、联系开发者草稿、构建产物和日志。

目标目录里除 .git 以外的内容会先清空再复制，所以目标目录只能是本脚本导出的仓库。

用法：python export_public.py [目标目录]
之后在目标目录里 git add -A / commit / push。
"""
import shutil
import sys
from pathlib import Path

from common import ROOT

DEFAULT_DEST = Path(r"E:\Project\AttackOnToys-zh-CN")

# (源路径, 目标路径)；目录整体复制
INCLUDE = [
    ("public/README.md", "README.md"),
    ("public/.gitignore", ".gitignore"),
    ("requirements.txt", "requirements.txt"),
    ("config", "config"),
    ("scripts", "scripts"),
    ("translation/zh-CN", "translation/zh-CN"),
    ("translation/glossary.md", "translation/glossary.md"),
    ("workshop/installer", "workshop/installer"),
    ("workshop/licenses", "workshop/licenses"),
    ("workshop/screenshots", "workshop/screenshots"),
    ("workshop/README_zh.txt", "workshop/README_zh.txt"),
    ("workshop/description_zh.txt", "workshop/description_zh.txt"),
    ("workshop/release_notes_zh.md", "workshop/release_notes_zh.md"),
    ("workshop/version.txt", "workshop/version.txt"),
    ("workshop/item_id.txt", "workshop/item_id.txt"),
    ("reports", "reports"),
]
EXCLUDE_NAMES = {"__pycache__", "bundle_inventory.md"}


def main():
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DEST
    if dest.exists() and any(dest.iterdir()) and not (dest / ".git").exists():
        sys.exit(f"{dest} 不是空目录也不是 git 仓库，为避免误删不做导出。")
    dest.mkdir(parents=True, exist_ok=True)
    for child in dest.iterdir():
        if child.name != ".git":
            shutil.rmtree(child) if child.is_dir() else child.unlink()

    ignore = shutil.ignore_patterns(*EXCLUDE_NAMES)
    for src_rel, dst_rel in INCLUDE:
        src, dst = ROOT / src_rel, dest / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, ignore=ignore)
        else:
            shutil.copy2(src, dst)

    files = [p for p in dest.rglob("*") if p.is_file() and ".git" not in p.relative_to(dest).parts]
    print(f"exported {len(files)} files -> {dest}")


if __name__ == "__main__":
    main()
