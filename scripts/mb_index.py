"""不依赖 TypeTree 的 MonoBehaviour 工具：解析基础头部并把 m_Script 解析成类名。

IL2CPP 构建的 data.unity3d 不含 MonoBehaviour 的 TypeTree，TypeTreeGeneratorAPI 对本游戏也失效，
因此这里按 Unity 2019.4 的固定序列化布局手工读取。
"""
import struct
from dataclasses import dataclass


def align4(n: int) -> int:
    return (n + 3) & ~3


class Reader:
    def __init__(self, data: bytes, pos: int = 0):
        self.data = data
        self.pos = pos

    def i32(self):
        v = struct.unpack_from("<i", self.data, self.pos)[0]
        self.pos += 4
        return v

    def u8(self):
        v = self.data[self.pos]
        self.pos += 1
        return v

    def f32(self):
        v = struct.unpack_from("<f", self.data, self.pos)[0]
        self.pos += 4
        return v

    def align(self):
        self.pos = align4(self.pos)

    def pptr(self):
        fid, pid = struct.unpack_from("<iq", self.data, self.pos)
        self.pos += 12
        return fid, pid

    def string(self):
        n = self.i32()
        s = self.data[self.pos : self.pos + n]
        self.pos = align4(self.pos + n)
        return s.decode("utf-8", errors="surrogateescape")

    def bool_aligned(self):
        v = self.u8()
        self.align()
        return v


@dataclass
class MBHeader:
    game_object: tuple
    enabled: int
    script: tuple
    name: str
    end: int


def read_header(raw: bytes) -> MBHeader:
    r = Reader(raw)
    go = r.pptr()
    enabled = r.bool_aligned()
    script = r.pptr()
    name = r.string()
    return MBHeader(go, enabled, script, name, r.pos)


def skip_persistent_calls(r: Reader):
    """UnityEvent.m_PersistentCalls.m_Calls（Unity 2019.4 布局）"""
    for _ in range(r.i32()):
        r.pptr()  # m_Target
        r.string()  # m_MethodName
        r.i32()  # m_Mode
        r.pptr()  # m_Arguments.m_ObjectArgument
        r.string()  # m_ObjectArgumentAssemblyTypeName
        r.i32()  # m_IntArgument
        r.f32()  # m_FloatArgument
        r.string()  # m_StringArgument
        r.bool_aligned()  # m_BoolArgument
        r.i32()  # m_CallState


FONTDATA_SIZE = 12 + 11 * 4


@dataclass
class UIText:
    font: tuple
    font_size: int
    rich_text: int
    text: str
    text_offset: int  # m_Text 长度前缀在 raw 中的偏移


def read_ui_text(raw: bytes, header: MBHeader) -> UIText:
    """解析 UnityEngine.UI.Text，失败时抛 ValueError。"""
    r = Reader(raw, header.end)
    r.pptr()  # m_Material
    r.pos += 16  # m_Color
    r.bool_aligned()  # m_RaycastTarget
    r.bool_aligned()  # m_Maskable
    skip_persistent_calls(r)  # m_OnCullStateChanged
    fd = r.pos
    font = r.pptr()
    font_size = r.i32()
    rich_text = struct.unpack_from("<i", raw, fd + 12 + 7 * 4)[0]
    r.pos = fd + FONTDATA_SIZE
    text_offset = r.pos
    text = r.string()
    if r.pos != len(raw):
        raise ValueError(f"Text 解析结束于 {r.pos}，数据长度 {len(raw)}")
    return UIText(font, font_size, rich_text, text, text_offset)


def external_name(assets_file, file_id: int) -> str:
    if file_id == 0:
        return assets_file.name
    return assets_file.externals[file_id - 1].path.split("/")[-1]


def build_script_index(env) -> dict:
    """(assets 文件名, pathID) -> (Assembly, Namespace.Class)"""
    idx = {}
    for obj in env.objects:
        if obj.type.name == "MonoScript":
            s = obj.parse_as_object()
            full = f"{s.m_Namespace}.{s.m_ClassName}" if s.m_Namespace else s.m_ClassName
            idx[(obj.assets_file.name, obj.path_id)] = (s.m_AssemblyName, full)
    return idx


def script_of(obj, header: MBHeader, idx: dict):
    fid, pid = header.script
    if pid == 0:
        return None
    return idx.get((external_name(obj.assets_file, fid), pid))
