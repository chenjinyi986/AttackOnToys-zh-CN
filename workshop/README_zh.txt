Attack on Toys（玩具大进攻）简体中文汉化
========================================

【安装：从创意工坊】
1. 在创意工坊订阅本物品，等 Steam 下载完成。
2. 打开本物品的文件夹（你现在可能已经在这里了）：
   <Steam 库>\steamapps\workshop\content\1269690\{ITEM_ID}
3. 双击“安装汉化.bat”，按提示操作。
4. 启动游戏。第一次启动需要 1～3 分钟准备（会联网下载一次约 5 MB 的 Unity 基础库），之后就正常了。

【安装：从压缩包】
压缩包下载：https://github.com/chenjinyi986/AttackOnToys-zh-CN/releases
1. 把压缩包解压到任意位置。
2. 双击里面的“安装汉化.bat”，按提示操作。脚本会自动找到 Steam 里的游戏目录，找不到时会让你输入。
3. 译文会复制到游戏目录，安装完成后解压出来的文件夹可以删除。
4. 启动游戏（第一次启动同样需要 1～3 分钟准备）。

【更新】
从创意工坊安装：汉化更新会随创意工坊自动下载，重启游戏后生效，一般不需要重新安装。
Steam 有时不会马上推送更新：可以在游戏主菜单 → 我的模组（扳手图标）→ 点“更新创意工坊”立即下载，然后重启游戏。
从压缩包安装：下载新版压缩包，解压后再运行一次“安装汉化.bat”。
如果更新说明里写了“需要重新安装”，或者游戏更新后汉化失效，再运行一次“安装汉化.bat”即可。

【卸载】
双击“卸载汉化.bat”，游戏即恢复英文原版。从创意工坊安装的，之后可以取消订阅。
只取消订阅而不卸载也可以：游戏会显示英文，但加载器仍留在游戏目录里。

【原理】
游戏本身没有语言切换功能，创意工坊也无法直接加载翻译，所以本汉化用插件实现：
· BepInEx 6（IL2CPP 版）：Unity 游戏常用的插件加载器，由 winhttp.dll（Doorstop）在启动时载入。
· XUnity.AutoTranslator：运行时把界面文字按译文表替换成中文；动态拼接的文本用正则规则处理。
· 中文字体使用 Windows 系统字体自动回退。

【安全与透明】
· 两个 bat 除了设置控制台编码和最后暂停窗口，只做一件事：用 PowerShell 运行 installer 文件夹里对应的 .ps1 脚本。
  命令里的 -ExecutionPolicy Bypass 只对这一次运行有效，不改系统设置。脚本都是纯文本，可以用记事本打开查看。
· 安装脚本只做三件事：
  1) 定位游戏目录（只读取注册表里的 Steam 安装路径，不写注册表）；
  2) 把 payload 文件夹里的加载器复制到游戏根目录：BepInEx\、dotnet\、winhttp.dll、doorstop_config.ini、.doorstop_version；
  3) 写入翻译插件的配置文件和一个安装记录 BepInEx\AttackOnToys_zh-CN.txt。
  不修改、不删除任何游戏原文件，不联网。
· 卸载脚本只删除上面这些新增的文件和文件夹，删除前会列出清单并让你确认。
· payload 里的 DLL 全部取自 BepInEx 和 XUnity.AutoTranslator 的官方发布包，没有做任何修改。
  “校验值.txt”列出了每个文件的 SHA256，以及对应官方压缩包的下载地址和校验值，可以自行核对。
· 联网情况：游戏第一次启动时，BepInEx 会从官方地址 unity.bepinex.dev 下载一次 Unity 基础库（BepInEx 的正常行为）；
  汉化本身运行时不联网，不调用任何机器翻译。
· 杀毒软件报 winhttp.dll：这是 BepInEx 的启动器（Doorstop）。它利用 Windows 优先加载游戏目录里同名 DLL 的机制，
  在游戏启动时载入 BepInEx。这种加载方式和部分恶意软件相似，所以常被启发式引擎误报。
  可以按“校验值.txt”核对，或上传到 virustotal.com 查询，确认后再加入信任。

【制作工具】
本汉化使用 Anthropic 的 AI 编程助手 Claude Code 制作（原文提取、翻译、规则编写、安装脚本、打包上传），
并在游戏内逐项测试校对。

【常见问题】
· 中国大陆玩家：如果因为网络原因下载不了 Unity 基础库（表现为第一次启动后游戏仍是英文），
  请留言或发邮件反馈，最好附上游戏目录里的 BepInEx\LogOutput.log。
· 双击 bat 后窗口一闪而过：右键“安装汉化.bat” → 以管理员身份运行。
· 少量文字仍是英文：玩家名、社区作品名、按键名按惯例不翻译。
· 加载关卡时左下角一闪而过的“aaaa…”小框是原版游戏就有的现象，与汉化无关。

【反馈】
漏翻、错译或其他问题：创意工坊页面留言、GitHub Issues（最好附截图），或发邮件至 chenjinyi986@gmail.com
GitHub：https://github.com/chenjinyi986/AttackOnToys-zh-CN

【开源组件与许可证】
· BepInEx 6（LGPL-2.1）https://github.com/BepInEx/BepInEx
· Il2CppInterop（LGPL-3.0）https://github.com/BepInEx/Il2CppInterop
· XUnity.AutoTranslator（MIT）https://github.com/bbepis/XUnity.AutoTranslator
· .NET 运行时（MIT）https://github.com/dotnet/runtime
许可证全文见 licenses 文件夹。

本汉化为玩家自制，与 N7T-GAMES 无关。游戏版权归原作者所有。
