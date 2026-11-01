# Attack on Toys 简体中文汉化 v{VERSION}

《Attack on Toys》的完整简体中文汉化（非官方，玩家自制）。这里提供压缩包下载，内容与 Steam 创意工坊版相同。

**下载**：`AttackOnToys_zh-CN_v{VERSION}.zip`（SHA256：`{SHA256}`）

## 安装

1. 把压缩包解压到任意位置。
2. 双击里面的 **安装汉化.bat**，按提示操作。脚本会自动找到 Steam 里的游戏目录，找不到时会让你输入。
3. 启动游戏。**第一次启动需要 1～3 分钟**准备（BepInEx 会联网下载一次约 5 MB 的 Unity 基础库），之后就正常了。

安装完成后，解压出来的文件夹可以删除（译文已经复制进游戏目录）。更新时下载新版压缩包，再运行一次安装脚本即可。

> **中国大陆玩家**：如果因为网络原因下载不了 Unity 基础库（表现为第一次启动后游戏仍是英文），请在 Issues 留言或发邮件反馈，最好附上游戏目录里的 `BepInEx\LogOutput.log`。

**卸载**：运行 **卸载汉化.bat**，游戏恢复英文原版。

## 翻译范围

约 3,300 条译文和 110 余条动态文本规则：主菜单与设置、全部任务名称与简报、新兵训练营全部对话、战斗界面与属性卡片、全部兵种/武器/载具/塔楼/建筑的名称与说明、玩具箱全部分类和 1,500 余个物品名称。玩家名、社区作品名、按键名按惯例保留英文。

## 原理与安全

- 加载器 **BepInEx 6（IL2CPP 版）** + 文本替换插件 **XUnity.AutoTranslator**，运行时按译文表把界面文字替换成中文，不调用任何在线翻译或机器翻译。
- 安装脚本是纯文本的 PowerShell 脚本（`installer\` 文件夹），只向游戏目录添加 `BepInEx\`、`dotnet\`、`winhttp.dll`、`doorstop_config.ini`、`.doorstop_version`，不修改任何游戏原文件；卸载脚本只删除这些文件。
- 压缩包里的 DLL 全部取自 BepInEx 和 XUnity.AutoTranslator 的官方发布包，没有修改。`校验值.txt` 列出了每个文件的 SHA256，以及官方压缩包的地址和校验值。
- 杀毒软件可能把 `winhttp.dll`（BepInEx 的启动器 Doorstop）误报为可疑文件，原因和核对方法见压缩包里的 `说明.txt`。

## 制作工具

本汉化使用 Anthropic 的 AI 编程助手 Claude Code 制作（原文提取、翻译、规则编写、安装脚本、打包），并在游戏内逐项测试校对。

## 反馈

漏翻、错译或其他问题：在 Issues 留言，或发邮件至 chenjinyi986@gmail.com（最好附截图）。

## 开源组件

BepInEx（LGPL-2.1）、Il2CppInterop（LGPL-3.0）、XUnity.AutoTranslator（MIT）、.NET 运行时（MIT）。许可证全文见压缩包内 `licenses` 文件夹。

本汉化为玩家自制，与 N7T-GAMES 无关。游戏版权归原作者所有。
