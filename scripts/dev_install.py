"""开发用：把 BepInEx 6 IL2CPP + XUnity.AutoTranslator 装进游戏目录 / 从游戏目录移除。

只新增文件：安装前检查游戏根目录里不存在加载器的任何顶层条目，存在就中止。
卸载时删除这些顶层条目（BepInEx、dotnet、winhttp.dll 等），游戏原文件不动。

用法：
  python dev_install.py install
  python dev_install.py uninstall
  python dev_install.py status
"""
import shutil
import sys

from common import GAME_DIR, ROOT

PACKAGES = [ROOT / "tools" / "bepinex", ROOT / "tools" / "xunity"]
# 加载器在游戏根目录新增的顶层条目；BepInEx 首次运行还会在 BepInEx/ 下生成 interop、cache、config 等
TOP_LEVEL = [".doorstop_version", "BepInEx", "changelog.txt", "doorstop_config.ini", "dotnet", "winhttp.dll"]


def status():
    present = [n for n in TOP_LEVEL if (GAME_DIR / n).exists()]
    print("installed entries:", present or "none")
    return present


def install():
    if status():
        sys.exit("游戏目录里已有加载器文件，先 uninstall 或手动检查。")
    for pkg in PACKAGES:
        for src in pkg.rglob("*"):
            if src.is_dir():
                continue
            dst = GAME_DIR / src.relative_to(pkg)
            if dst.exists() and not dst.relative_to(GAME_DIR).parts[0] in TOP_LEVEL:
                sys.exit(f"拒绝覆盖游戏原文件：{dst}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    status()


def uninstall():
    for n in TOP_LEVEL:
        p = GAME_DIR / n
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    status()


if __name__ == "__main__":
    {"install": install, "uninstall": uninstall, "status": status}[sys.argv[1]]()
