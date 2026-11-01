"""组装创意工坊物品目录 workshop/build/item/、预览图 workshop/build/preview.jpg，
以及备用渠道（GitHub 等）用的压缩包 workshop/build/release/AttackOnToys_zh-CN_v<版本>.zip。

item/
├─ 安装汉化.bat / 卸载汉化.bat     双击入口（只调用 installer/*.ps1）
├─ 说明.txt / version.txt / 校验值.txt
├─ installer/                      install.ps1、uninstall.ps1、common.ps1、AutoTranslatorConfig.ini 模板
├─ payload/                        复制到游戏根目录的加载器文件
├─ Translation/zh-CN/Text/         译文（工坊安装时 XUnity 直接从这里读取）
└─ licenses/

用法：python build_workshop.py
"""
import hashlib
import shutil
import subprocess
import sys
import zipfile

from common import ROOT

TOOLS = ROOT / "tools"
WS = ROOT / "workshop"
BUILD = WS / "build"
ITEM = BUILD / "item"
RELEASE = BUILD / "release"

# payload 里的文件都取自这两个官方发布包（tools/dl/），打包时逐个核对
OFFICIAL = {
    "BepInEx": ("BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.791.zip",
                "https://builds.bepinex.dev/projects/bepinex_be/791/"),
    "XUnity": ("XUnity.AutoTranslator-BepInEx-IL2CPP-5.6.3.1.zip",
               "https://github.com/bbepis/XUnity.AutoTranslator/releases/tag/v5.6.3.1"),
}
OWN_PAYLOAD = {"BepInEx/config/BepInEx.cfg"}  # 本汉化自己的配置（只关闭了控制台窗口）
SUMS = "校验值.txt"

BAT = """@echo off
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer\\{script}" %*
echo.
pause
"""


def write_bom(path, text):
    """PowerShell 5.1 和记事本需要 BOM 才能正确识别 UTF-8 中文。"""
    path.write_text(text, encoding="utf-8-sig", newline="\r\n")


def build_payload(dst):
    bep = TOOLS / "bepinex"
    for name in (".doorstop_version", "winhttp.dll", "doorstop_config.ini"):
        shutil.copy2(bep / name, dst / name)
    shutil.copytree(bep / "dotnet", dst / "dotnet")
    shutil.copytree(bep / "BepInEx", dst / "BepInEx")
    shutil.copytree(
        TOOLS / "xunity" / "BepInEx",
        dst / "BepInEx",
        dirs_exist_ok=True,
        # 发布版不接在线翻译，不带机翻模块；README 也不需要
        ignore=shutil.ignore_patterns("Translators", "README*"),
    )
    (dst / "BepInEx" / "config").mkdir(exist_ok=True)
    shutil.copy2(ROOT / "config" / "BepInEx.cfg", dst / "BepInEx" / "config" / "BepInEx.cfg")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_checksums(version):
    """核对 payload 与官方发布包逐字节相同，并写出全部文件的 SHA256 清单，方便玩家自行核对。"""
    official, zip_hashes = {}, {}
    for label, (zip_name, _) in OFFICIAL.items():
        path = TOOLS / "dl" / zip_name
        zip_hashes[label] = sha256(path.read_bytes())
        with zipfile.ZipFile(path) as zf:
            for name in zf.namelist():
                if not name.endswith("/"):
                    official.setdefault(name, set()).add((label, sha256(zf.read(name))))

    rows = []
    for p in sorted(ITEM.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ITEM).as_posix()
        digest = sha256(p.read_bytes())
        if rel.startswith("payload/") and rel[len("payload/"):] not in OWN_PAYLOAD:
            sources = [label for label, h in official.get(rel[len("payload/"):], ()) if h == digest]
            if not sources:
                sys.exit(f"payload 文件与官方发布包不一致：{rel}")
            origin = sources[0]
        elif rel.startswith("licenses/"):
            origin = "许可证原文"
        else:
            origin = "本汉化"
        rows.append(f"{digest}  {rel.replace('/', chr(92))}  [{origin}]")

    head = [
        f"Attack on Toys 简体中文汉化 v{version} —— 文件校验值（SHA256）",
        "",
        "payload\\ 里的加载器文件全部取自下列官方发布包，没有做任何修改",
        "（payload\\BepInEx\\config\\BepInEx.cfg 除外：它是本汉化的配置，只关闭了控制台窗口）：",
    ]
    for label, (zip_name, url) in OFFICIAL.items():
        head += [f"· {zip_name}", f"  压缩包 SHA256：{zip_hashes[label]}", f"  {url}"]
    head += [
        "",
        "核对方法：在 PowerShell 里运行  Get-FileHash \"文件路径\"  ，与下表比较；",
        "也可以把文件上传到 https://www.virustotal.com 查询。",
        "标注 [本汉化] 的是本汉化自己写的文件（脚本、配置、译文、说明），都是纯文本，可以用记事本打开查看。",
        "",
    ]
    write_bom(ITEM / SUMS, "\n".join(head + rows) + "\n")


def build_release_zip(version):
    """备用渠道用的压缩包：顶层一个文件夹，内容与工坊物品相同。"""
    RELEASE.mkdir(parents=True, exist_ok=True)
    top = f"AttackOnToys_zh-CN_v{version}"
    out = RELEASE / f"{top}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(ITEM.rglob("*")):
            if p.is_file():
                zf.write(p, f"{top}/{p.relative_to(ITEM).as_posix()}")
    # 发布页正文（压缩包每次重打 SHA256 都会变，所以随包生成）
    notes = (WS / "release_notes_zh.md").read_text(encoding="utf-8")
    notes = notes.replace("{VERSION}", version).replace("{SHA256}", sha256(out.read_bytes()))
    (RELEASE / f"发布说明_v{version}.md").write_text(notes, encoding="utf-8")
    return out


def build_preview():
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(ROOT / "reports" / "img" / "02_main_menu_zh.jpg").convert("RGB").resize((1280, 720))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((0, 470, 1280, 640), fill=(10, 60, 10, 210))
    bold = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 92)
    small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 40)
    draw.text((640, 535), "简体中文汉化", font=bold, fill="white", anchor="mm")
    draw.text((640, 607), "Attack on Toys · 游戏内逐项校对 · 订阅后运行一次安装脚本", font=small, fill=(220, 255, 200), anchor="mm")
    img.save(BUILD / "preview.jpg", quality=88)


def main():
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_xunity.py")], check=True)
    # 只清空内容，不删目录本身（目录可能正被资源管理器或终端占用）
    ITEM.mkdir(parents=True, exist_ok=True)
    for child in ITEM.iterdir():
        shutil.rmtree(child) if child.is_dir() else child.unlink()

    (ITEM / "payload").mkdir()
    build_payload(ITEM / "payload")

    shutil.copytree(BUILD / "Translation", ITEM / "Translation")
    shutil.copytree(WS / "licenses", ITEM / "licenses")

    inst = ITEM / "installer"
    inst.mkdir()
    for ps1 in (WS / "installer").glob("*.ps1"):
        write_bom(inst / ps1.name, ps1.read_text(encoding="utf-8"))
    cfg = (ROOT / "config" / "AutoTranslatorConfig.release.ini").read_text(encoding="utf-8-sig")
    cfg = cfg.replace("Directory=Translation\\{Lang}\\Text", "Directory=__TRANSLATION_DIR__")
    assert "__TRANSLATION_DIR__" in cfg
    (inst / "AutoTranslatorConfig.ini").write_text(cfg, encoding="utf-8", newline="\r\n")

    (ITEM / "安装汉化.bat").write_text(BAT.format(script="install.ps1"), encoding="ascii", newline="\r\n")
    (ITEM / "卸载汉化.bat").write_text(BAT.format(script="uninstall.ps1"), encoding="ascii", newline="\r\n")
    id_file = WS / "item_id.txt"
    item_id = id_file.read_text(encoding="utf-8").strip() if id_file.exists() else "<本物品编号>"
    write_bom(ITEM / "说明.txt", (WS / "README_zh.txt").read_text(encoding="utf-8").replace("{ITEM_ID}", item_id))
    version = (WS / "version.txt").read_text(encoding="utf-8").strip()
    (ITEM / "version.txt").write_text(version + "\n", encoding="utf-8")
    write_checksums(version)

    build_preview()
    release = build_release_zip(version)

    files = [p for p in ITEM.rglob("*") if p.is_file()]
    size = sum(p.stat().st_size for p in files)
    print(f"item v{version}: {len(files)} files, {size / 1024 / 1024:.1f} MB -> {ITEM}")
    print(f"preview: {(BUILD / 'preview.jpg').stat().st_size / 1024:.0f} KB")
    print(f"release: {release.name} {release.stat().st_size / 1024 / 1024:.1f} MB  SHA256 {sha256(release.read_bytes())}")


if __name__ == "__main__":
    main()
