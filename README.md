# Attack on Toys 简体中文汉化

《[Attack on Toys](https://store.steampowered.com/app/1269690/Attack_on_Toys/)》的完整简体中文汉化（非官方，玩家自制）。

Unofficial Simplified Chinese translation for *Attack on Toys*, built on BepInEx 6 (IL2CPP) + XUnity.AutoTranslator. No machine translation at runtime; no game files are modified.

## 下载

- **压缩包**：到 [Releases](../../releases) 下载最新的 `AttackOnToys_zh-CN_v*.zip`。
- **Steam 创意工坊**：[物品 3831407646](https://steamcommunity.com/sharedfiles/filedetails/?id=3831407646)（尚未公开，公开后可访问）。两个渠道内容相同。

## 安装

1. 把压缩包解压到任意位置。
2. 双击里面的 **安装汉化.bat**，按提示操作。脚本会自动找到 Steam 里的游戏目录，找不到时会让你输入。
3. 启动游戏。**第一次启动需要 1～3 分钟**准备（BepInEx 会联网下载一次约 5 MB 的 Unity 基础库），之后就正常了。

安装完成后，解压出来的文件夹可以删除。更新时下载新版压缩包，再运行一次安装脚本即可。想恢复英文，运行 **卸载汉化.bat**。

> **中国大陆玩家**：如果因为网络原因下载不了 Unity 基础库（表现为第一次启动后游戏仍是英文），请在 [Issues](../../issues) 留言或发邮件反馈，最好附上游戏目录里的 `BepInEx\LogOutput.log`。

## 翻译范围

约 3,300 条译文和 110 余条动态文本规则：
- 主菜单、设置、按键绑定、帮助、存档、排行榜、分屏
- 全部任务名称、任务简报与目标
- 新兵训练营全部 NPC 对话
- 战斗界面、物品栏、商店、小队、属性卡片
- 全部兵种、武器、载具、塔楼、建筑的名称与说明
- 玩具箱（关卡编辑器）全部分类和 1,500 余个物品名称

玩家名、社区作品名、按键名按惯例保留英文。

## 原理与安全

- 游戏基于 Unity 2019.4（IL2CPP），没有语言选项；创意工坊也只能加载关卡和模型 Mod。所以本汉化用 **BepInEx 6（IL2CPP 版）** 作加载器，由 **XUnity.AutoTranslator** 在运行时按译文表替换界面文字。数值、玩家名、按键提示、多句对话等动态文本由正则规则处理。中文字体使用 Windows 系统字体自动回退。
- 安装脚本（`workshop/installer/*.ps1`）是纯文本，只向游戏目录添加 `BepInEx\`、`dotnet\`、`winhttp.dll`、`doorstop_config.ini`、`.doorstop_version`，不修改任何游戏原文件；卸载脚本只删除这些文件。
- 压缩包里的 DLL 全部取自 [BepInEx](https://builds.bepinex.dev/projects/bepinex_be/791/) 和 [XUnity.AutoTranslator](https://github.com/bbepis/XUnity.AutoTranslator/releases/tag/v5.6.3.1) 的官方发布包，没有修改。包内 `校验值.txt` 列出了每个文件的 SHA256。
- 杀毒软件可能把 `winhttp.dll`（BepInEx 的启动器 Doorstop）误报为可疑文件：它利用 Windows 优先加载游戏目录里同名 DLL 的机制载入 BepInEx，这种方式和部分恶意软件相似。可以按校验值核对，或上传到 [VirusTotal](https://www.virustotal.com) 查询。

## 仓库结构

| 路径 | 内容 |
|---|---|
| `translation/zh-CN/*.tsv` | 译文表（原文 / 译文 / 备注），`00_regex.tsv` 是动态文本规则 |
| `translation/glossary.md` | 术语表 |
| `scripts/` | 原文提取、运行时采集、译文构建、工坊打包与上传脚本（Python / PowerShell） |
| `workshop/installer/` | 玩家用的安装/卸载脚本 |
| `workshop/licenses/` | 第三方组件许可证 |
| `config/` | XUnity 与 BepInEx 配置（发布用 / 采集用） |
| `reports/` | 制作过程记录：方案调研、加载器实测、各批翻译、问题排查 |

### 自行构建

本仓库**不包含**从游戏里提取的原始文本（`translation/source/`），需要用自己的游戏文件重新生成：

1. 安装 Python 3.11 和依赖：`pip install -r requirements.txt`；把 BepInEx 和 XUnity 的官方压缩包解压到 `tools/bepinex`、`tools/xunity`，压缩包本身放在 `tools/dl/`。
2. 在 `scripts/` 目录运行 `extract_ui_texts.py`、`scan_mb_strings.py`、`extract_metadata_strings.py`、`extract_items.py` 提取原文；运行时文本用 `capture_server.py` 配合采集配置收集（见 `reports/02`～`04`）。
3. `python build_xunity.py` 生成 XUnity 译文文件，`python build_workshop.py` 打包。

游戏目录默认是 `G:\SteamLibrary\steamapps\common\Attack on Toys`，可用环境变量 `AOT_GAME_DIR` 覆盖。

## 制作工具

本汉化使用 Anthropic 的 AI 编程助手 [Claude Code](https://claude.com/claude-code) 制作：原文提取、运行时文本采集、翻译与术语统一、动态文本规则、安装脚本和打包上传，都由 Claude Code 完成，并在游戏内逐项测试校对。

## 反馈

漏翻、错译或其他问题：在 [Issues](../../issues) 留言（最好附截图），或发邮件至 chenjinyi986@gmail.com。

## 第三方组件

- BepInEx 6（LGPL-2.1）https://github.com/BepInEx/BepInEx
- Il2CppInterop（LGPL-3.0）https://github.com/BepInEx/Il2CppInterop
- XUnity.AutoTranslator（MIT）https://github.com/bbepis/XUnity.AutoTranslator
- .NET 运行时（MIT）https://github.com/dotnet/runtime

许可证全文见 `workshop/licenses/`。

本汉化为玩家自制，与 N7T-GAMES 无关。游戏版权归原作者所有。
