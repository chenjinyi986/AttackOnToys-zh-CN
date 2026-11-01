# Attack on Toys 简体中文汉化：安装/卸载脚本共用函数
$ErrorActionPreference = 'Stop'

$AppId = '1269690'
$GameFolderName = 'Attack on Toys'
$GameExe = 'Attack on Toys.exe'
$MarkerName = 'AttackOnToys_zh-CN.txt'
# 从压缩包安装时译文复制到 BepInEx\ 下的这个文件夹（随 BepInEx 一起卸载）
$PackageTranslationDir = 'AttackOnToys_zh-CN'
# 加载器在游戏根目录新增的顶层条目（卸载时删除）
$LoaderEntries = @('.doorstop_version', 'BepInEx', 'doorstop_config.ini', 'dotnet', 'winhttp.dll')

function Test-GameDir([string]$dir) {
    return $dir -and (Test-Path -LiteralPath (Join-Path $dir $GameExe))
}

function Get-SteamLibraries {
    $libs = @()
    $steam = (Get-ItemProperty -Path 'HKCU:\Software\Valve\Steam' -ErrorAction SilentlyContinue).SteamPath
    if ($steam) {
        $steam = $steam -replace '/', '\'
        $libs += $steam
        $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf) {
            foreach ($m in [regex]::Matches((Get-Content -LiteralPath $vdf -Raw -Encoding UTF8), '"path"\s+"([^"]+)"')) {
                $libs += ($m.Groups[1].Value -replace '\\\\', '\')
            }
        }
    }
    return $libs | Select-Object -Unique
}

function Find-GameDir([string]$ItemDir, [string]$Override) {
    if ($Override) {
        if (Test-GameDir $Override) { return (Resolve-Path -LiteralPath $Override).Path }
        throw "指定的目录里没有找到 $GameExe：$Override"
    }
    # 工坊物品位于 <Steam 库>\steamapps\workshop\content\1269690\<物品ID>\，游戏在同一个库的 steamapps\common 下
    $guess = Join-Path $ItemDir "..\..\..\..\common\$GameFolderName"
    if (Test-GameDir $guess) { return (Resolve-Path -LiteralPath $guess).Path }
    foreach ($lib in Get-SteamLibraries) {
        $dir = Join-Path $lib "steamapps\common\$GameFolderName"
        if (Test-GameDir $dir) { return (Resolve-Path -LiteralPath $dir).Path }
    }
    Write-Host '没有自动找到游戏目录。'
    $manual = Read-Host "请输入游戏安装目录（包含 $GameExe 的文件夹）"
    $manual = $manual.Trim('"', ' ')
    if (Test-GameDir $manual) { return (Resolve-Path -LiteralPath $manual).Path }
    throw "这个目录里没有 $GameExe：$manual"
}

function Assert-GameNotRunning {
    while (Get-Process -Name ([IO.Path]::GetFileNameWithoutExtension($GameExe)) -ErrorAction SilentlyContinue) {
        Read-Host '游戏正在运行。请先退出游戏，然后按回车继续'
    }
}

function Confirm-Yes([string]$question) {
    if ($script:AssumeYes) { Write-Host "$question [Y/N] Y"; return $true }
    $answer = Read-Host "$question [Y/N]"
    return $answer -match '^[Yy]'
}

function Write-Utf8NoBom([string]$path, [string]$text) {
    [IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding $false))
}
