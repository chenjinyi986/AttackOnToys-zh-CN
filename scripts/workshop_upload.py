"""通过已登录的 Steam 客户端上传/更新创意工坊物品（调用游戏自带的 steam_api64.dll，不需要账号密码）。

首次发布分三步（物品编号要写进说明和介绍，所以先创建、再打包、再上传）：
  python workshop_upload.py --create                         只创建空物品，ID 写入 workshop/item_id.txt
  python build_workshop.py                                    打包（说明.txt 里填入物品编号）
  python workshop_upload.py --visibility private --note "…"   上传内容并设为私有
之后的更新：
  python workshop_upload.py --note "更新说明"                 更新内容、预览图、标题和介绍，不改可见性
  python workshop_upload.py --visibility public               只有明确指定时才改可见性：public / friends / private / unlisted

运行期间 Steam 会显示你“正在玩 Attack on Toys”。游戏本身不能同时运行。
上传/公开前必须征得用户同意（见 CLAUDE.md 安全边界）。
"""
import argparse
import ctypes
import os
import sys
import tempfile
import time
from pathlib import Path

from common import APP_ID, DATA_DIR, ROOT

WS = ROOT / "workshop"
ITEM_DIR = WS / "build" / "item"
PREVIEW = WS / "build" / "preview.jpg"
SCREENSHOTS = WS / "screenshots"  # 附加预览图（游戏内展示截图）
ID_FILE = WS / "item_id.txt"
TITLE = "简体中文汉化 | Simplified Chinese Translation"
DLL = DATA_DIR / "Plugins" / "x86_64" / "steam_api64.dll"

VISIBILITY = {"public": 0, "friends": 1, "private": 2, "unlisted": 3}
K_CREATE_ITEM_RESULT = 3403
K_SUBMIT_ITEM_UPDATE_RESULT = 3404
K_RESULT_OK = 1
UPDATE_STATUS = {0: "无效", 1: "准备配置", 2: "准备内容", 3: "上传内容", 4: "上传预览图", 5: "提交修改"}


class CreateItemResult(ctypes.Structure):
    _pack_ = 8
    _fields_ = [("result", ctypes.c_int32), ("file_id", ctypes.c_uint64), ("needs_legal", ctypes.c_bool)]


class SubmitItemUpdateResult(ctypes.Structure):
    _pack_ = 8
    _fields_ = [("result", ctypes.c_int32), ("needs_legal", ctypes.c_bool), ("file_id", ctypes.c_uint64)]


class Steam:
    def __init__(self):
        # SteamAPI_Init 需要知道 AppID：用环境变量 + 临时目录里的 steam_appid.txt
        os.environ["SteamAppId"] = str(APP_ID)
        os.environ["SteamGameId"] = str(APP_ID)
        self._tmp = tempfile.mkdtemp(prefix="aot_upload_")
        Path(self._tmp, "steam_appid.txt").write_text(str(APP_ID))
        os.chdir(self._tmp)

        api = ctypes.CDLL(str(DLL))
        self.api = api
        api.SteamAPI_Init.restype = ctypes.c_bool
        if not api.SteamAPI_Init():
            sys.exit("SteamAPI_Init 失败：请确认 Steam 客户端已登录、拥有本游戏，且游戏没有在运行。")
        api.SteamAPI_SteamUGC_v014.restype = ctypes.c_void_p
        api.SteamAPI_SteamUtils_v009.restype = ctypes.c_void_p
        self.ugc = ctypes.c_void_p(api.SteamAPI_SteamUGC_v014())
        self.utils = ctypes.c_void_p(api.SteamAPI_SteamUtils_v009())

        P, U64, U32, I32, S, B = ctypes.c_void_p, ctypes.c_uint64, ctypes.c_uint32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool
        sig = {
            "SteamAPI_ISteamUGC_CreateItem": (U64, [P, U32, I32]),
            "SteamAPI_ISteamUGC_StartItemUpdate": (U64, [P, U32, U64]),
            "SteamAPI_ISteamUGC_SetItemTitle": (B, [P, U64, S]),
            "SteamAPI_ISteamUGC_SetItemDescription": (B, [P, U64, S]),
            "SteamAPI_ISteamUGC_SetItemUpdateLanguage": (B, [P, U64, S]),
            "SteamAPI_ISteamUGC_SetItemContent": (B, [P, U64, S]),
            "SteamAPI_ISteamUGC_SetItemPreview": (B, [P, U64, S]),
            "SteamAPI_ISteamUGC_SetItemVisibility": (B, [P, U64, I32]),
            "SteamAPI_ISteamUGC_AddItemPreviewFile": (B, [P, U64, S, I32]),
            "SteamAPI_ISteamUGC_DownloadItem": (B, [P, U64, B]),
            "SteamAPI_ISteamUGC_GetItemState": (U32, [P, U64]),
            "SteamAPI_ISteamUGC_SubmitItemUpdate": (U64, [P, U64, S]),
            "SteamAPI_ISteamUGC_GetItemUpdateProgress": (I32, [P, U64, ctypes.POINTER(U64), ctypes.POINTER(U64)]),
            "SteamAPI_ISteamUtils_IsAPICallCompleted": (B, [P, U64, ctypes.POINTER(B)]),
            "SteamAPI_ISteamUtils_GetAPICallResult": (B, [P, U64, P, I32, I32, ctypes.POINTER(B)]),
        }
        for name, (res, args) in sig.items():
            fn = getattr(api, name)
            fn.restype, fn.argtypes = res, args

    def call(self, name, *args):
        return getattr(self.api, name)(*args)

    def wait(self, call_handle, struct, callback_id, on_tick=None):
        failed = ctypes.c_bool(False)
        while not self.call("SteamAPI_ISteamUtils_IsAPICallCompleted", self.utils, call_handle, ctypes.byref(failed)):
            self.api.SteamAPI_RunCallbacks()
            if on_tick:
                on_tick()
            time.sleep(0.5)
        result = struct()
        ok = self.call(
            "SteamAPI_ISteamUtils_GetAPICallResult", self.utils, call_handle,
            ctypes.byref(result), ctypes.sizeof(result), callback_id, ctypes.byref(failed),
        )
        if not ok or failed.value:
            sys.exit("Steam 调用失败（网络或 Steam 服务问题），请稍后重试。")
        return result

    def shutdown(self):
        self.api.SteamAPI_Shutdown()


def utf8(s: str) -> bytes:
    return s.encode("utf-8")


def create(steam: Steam) -> int:
    res = steam.wait(steam.call("SteamAPI_ISteamUGC_CreateItem", steam.ugc, APP_ID, 0), CreateItemResult, K_CREATE_ITEM_RESULT)
    if res.result != K_RESULT_OK:
        sys.exit(f"创建物品失败，EResult={res.result}")
    ID_FILE.write_text(f"{res.file_id}\n", encoding="utf-8")
    print(f"已创建物品 {res.file_id}（ID 已写入 {ID_FILE}）")
    if res.needs_legal:
        print("提示：需要先在网页上接受创意工坊法律协议，物品才能被他人看到。")
    return res.file_id


def update(steam: Steam, file_id: int, note: str, visibility: str | None, add_screenshots: bool = False):
    for path in (ITEM_DIR, PREVIEW):
        if not path.exists():
            sys.exit(f"缺少 {path}，请先运行 build_workshop.py")
    h = steam.call("SteamAPI_ISteamUGC_StartItemUpdate", steam.ugc, APP_ID, file_id)
    description = (WS / "description_zh.txt").read_text(encoding="utf-8").replace("{ITEM_ID}", str(file_id))
    checks = [
        steam.call("SteamAPI_ISteamUGC_SetItemUpdateLanguage", steam.ugc, h, b"schinese"),
        steam.call("SteamAPI_ISteamUGC_SetItemTitle", steam.ugc, h, utf8(TITLE)),
        steam.call("SteamAPI_ISteamUGC_SetItemDescription", steam.ugc, h, utf8(description)),
        steam.call("SteamAPI_ISteamUGC_SetItemContent", steam.ugc, h, utf8(str(ITEM_DIR.resolve()))),
        steam.call("SteamAPI_ISteamUGC_SetItemPreview", steam.ugc, h, utf8(str(PREVIEW.resolve()))),
    ]
    if visibility:
        checks.append(steam.call("SteamAPI_ISteamUGC_SetItemVisibility", steam.ugc, h, VISIBILITY[visibility]))
    if add_screenshots:
        # 每次调用都会新增，不会替换旧图；要换图先在网页上删掉旧的附加预览
        for shot in sorted(SCREENSHOTS.glob("*.jpg")):
            checks.append(steam.call("SteamAPI_ISteamUGC_AddItemPreviewFile", steam.ugc, h, utf8(str(shot.resolve())), 0))
            print(f"附加预览图：{shot.name}")
    if not all(checks):
        sys.exit(f"设置物品属性失败：{checks}")

    processed, total = ctypes.c_uint64(), ctypes.c_uint64()

    def tick():
        status = steam.call("SteamAPI_ISteamUGC_GetItemUpdateProgress", steam.ugc, h, ctypes.byref(processed), ctypes.byref(total))
        pct = f"{processed.value / total.value:.0%}" if total.value else ""
        print(f"\r{UPDATE_STATUS.get(status, status)} {pct}      ", end="", flush=True)

    call = steam.call("SteamAPI_ISteamUGC_SubmitItemUpdate", steam.ugc, h, utf8(note))
    res = steam.wait(call, SubmitItemUpdateResult, K_SUBMIT_ITEM_UPDATE_RESULT, tick)
    print()
    if res.result != K_RESULT_OK:
        sys.exit(f"提交失败，EResult={res.result}")
    print(f"提交成功：https://steamcommunity.com/sharedfiles/filedetails/?id={file_id}")
    if res.needs_legal:
        print("提示：需要先在网页上接受创意工坊法律协议。")


def download(steam: Steam, file_id: int):
    """让本机已订阅的副本立即更新到最新版本（本地测试用）。"""
    if not steam.call("SteamAPI_ISteamUGC_DownloadItem", steam.ugc, file_id, True):
        sys.exit("DownloadItem 失败：请确认已订阅该物品。")
    installed, needs_update, busy = 4, 8, 16 | 32
    for _ in range(240):
        steam.api.SteamAPI_RunCallbacks()
        state = steam.call("SteamAPI_ISteamUGC_GetItemState", steam.ugc, file_id)
        if state & installed and not state & (needs_update | busy):
            print(f"本地副本已是最新（state={state}）")
            return
        time.sleep(0.5)
    sys.exit("等待下载超时")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--create", action="store_true", help="只创建空物品并记录 ID（随后打包、再上传内容）")
    ap.add_argument("--note", default="", help="本次更新说明")
    ap.add_argument("--visibility", choices=VISIBILITY, help="只有明确指定时才修改可见性")
    ap.add_argument("--add-screenshots", action="store_true", help="追加 workshop/screenshots/*.jpg 为附加预览图（会新增，不替换）")
    ap.add_argument("--download", action="store_true", help="只让本机已订阅的副本立即更新（不上传）")
    args = ap.parse_args()

    if args.create and ID_FILE.exists():
        sys.exit(f"已经有物品 {ID_FILE.read_text().strip()}，不重复创建。")
    steam = Steam()
    try:
        if args.create:
            create(steam)
        elif args.download:
            download(steam, int(ID_FILE.read_text().strip()))
        else:
            if not ID_FILE.exists():
                sys.exit("还没有物品 ID，请先用 --create 创建。")
            update(steam, int(ID_FILE.read_text().strip()), args.note, args.visibility, args.add_screenshots)
    finally:
        steam.shutdown()


if __name__ == "__main__":
    main()
