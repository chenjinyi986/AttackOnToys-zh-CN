"""项目公共路径与 UnityPy 环境加载。"""
import os
from pathlib import Path

GAME_DIR = Path(os.environ.get("AOT_GAME_DIR", r"G:\SteamLibrary\steamapps\common\Attack on Toys"))
DATA_DIR = GAME_DIR / "Attack on Toys_Data"
BUNDLE = DATA_DIR / "data.unity3d"
METADATA = DATA_DIR / "il2cpp_data" / "Metadata" / "global-metadata.dat"
GAME_ASSEMBLY = GAME_DIR / "GameAssembly.dll"
UNITY_VERSION = "2019.4.41f2"
APP_ID = 1269690

ROOT = Path(__file__).resolve().parent.parent
TRANSLATION_DIR = ROOT / "translation"
REPORTS_DIR = ROOT / "reports"
LOGS_DIR = ROOT / "logs"


def load_env(with_typetree: bool = True):
    """加载 data.unity3d；IL2CPP 构建没有内嵌 TypeTree，需要从 GameAssembly + metadata 生成。"""
    import UnityPy

    env = UnityPy.load(str(BUNDLE))
    if with_typetree:
        from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

        gen = TypeTreeGenerator(UNITY_VERSION)
        gen.load_il2cpp(GAME_ASSEMBLY.read_bytes(), METADATA.read_bytes())
        env.typetree_generator = gen
    return env
