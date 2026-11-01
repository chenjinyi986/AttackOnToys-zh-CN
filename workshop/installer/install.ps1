# Attack on Toys 简体中文汉化：安装
# 把 BepInEx 加载器和 XUnity.AutoTranslator 复制到游戏目录。
# 从创意工坊目录安装时，译文直接从工坊物品目录读取（随工坊更新自动生效）；
# 从压缩包安装时，译文复制到游戏目录（解压出来的文件夹之后删掉也不影响）。
param([string]$GameDir, [switch]$Yes)
. (Join-Path $PSScriptRoot 'common.ps1')
$script:AssumeYes = $Yes

$ItemDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Version = (Get-Content -LiteralPath (Join-Path $ItemDir 'version.txt') -Raw).Trim()
$FromWorkshop = $ItemDir -match "\\steamapps\\workshop\\content\\$AppId\\\d+$"
Write-Host "Attack on Toys 简体中文汉化 v$Version —— 安装"
Write-Host ''

try {
    $game = Find-GameDir $ItemDir $GameDir
    Write-Host "游戏目录：$game"
    Assert-GameNotRunning

    $marker = Join-Path $game "BepInEx\$MarkerName"
    if ((Test-Path -LiteralPath (Join-Path $game 'BepInEx')) -and -not (Test-Path -LiteralPath $marker)) {
        Write-Host ''
        Write-Host '游戏目录里已经有一个 BepInEx（不是本汉化安装的）。'
        Write-Host '继续安装会覆盖它的核心文件，其他基于 BepInEx 的 Mod 可能失效。'
        if (-not (Confirm-Yes '仍然继续安装吗？')) { throw '已取消安装。' }
    }

    $payload = Join-Path $ItemDir 'payload'
    Get-ChildItem -LiteralPath $payload -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $game -Recurse -Force
    }

    # 采集/替换类文件仍留在游戏的 BepInEx 目录，只有译文目录按安装来源指向不同位置
    $copyDir = Join-Path $game "BepInEx\$PackageTranslationDir"
    if (Test-Path -LiteralPath $copyDir) { Remove-Item -LiteralPath $copyDir -Recurse -Force }
    if ($FromWorkshop) {
        $translationDir = Join-Path $ItemDir 'Translation\{Lang}\Text'
    }
    else {
        New-Item -ItemType Directory -Path $copyDir | Out-Null
        Copy-Item -LiteralPath (Join-Path $ItemDir 'Translation') -Destination $copyDir -Recurse -Force
        $translationDir = Join-Path $copyDir 'Translation\{Lang}\Text'
    }
    $cfgTemplate = Get-Content -LiteralPath (Join-Path $ItemDir 'installer\AutoTranslatorConfig.ini') -Raw -Encoding UTF8
    $cfg = $cfgTemplate.Replace('__TRANSLATION_DIR__', $translationDir)
    Write-Utf8NoBom (Join-Path $game 'BepInEx\config\AutoTranslatorConfig.ini') $cfg

    $source = if ($FromWorkshop) { '创意工坊' } else { "压缩包（$ItemDir）" }
    $info = @(
        "Attack on Toys 简体中文汉化 v$Version",
        "安装时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
        "安装来源：$source",
        "译文目录：$translationDir",
        '卸载：运行汉化包里的“卸载汉化.bat”'
    ) -join "`r`n"
    Write-Utf8NoBom $marker $info

    Write-Host ''
    Write-Host '安装完成！'
    Write-Host '· 第一次启动游戏需要 1～3 分钟准备（会联网下载一次 Unity 基础库），请耐心等待，之后启动就正常了。'
    if ($FromWorkshop) {
        Write-Host '· 以后汉化更新会随创意工坊自动下载，无需重新安装（除非更新说明里要求重装）。'
    }
    else {
        Write-Host '· 译文已复制到游戏目录，解压出来的文件夹可以删除。'
        Write-Host '· 以后更新：下载新版压缩包，解压后再运行一次“安装汉化.bat”。'
    }
    Write-Host '· 想恢复英文：运行“卸载汉化.bat”。'
}
catch {
    Write-Host ''
    Write-Host "安装没有完成：$($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
