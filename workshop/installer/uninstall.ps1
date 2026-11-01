# Attack on Toys 简体中文汉化：卸载
# 删除安装时加到游戏目录里的加载器文件，游戏原文件不动。
param([string]$GameDir, [switch]$Yes)
. (Join-Path $PSScriptRoot 'common.ps1')
$script:AssumeYes = $Yes

$ItemDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Write-Host 'Attack on Toys 简体中文汉化 —— 卸载'
Write-Host ''

try {
    $game = Find-GameDir $ItemDir $GameDir
    Write-Host "游戏目录：$game"
    Assert-GameNotRunning

    if (-not (Test-Path -LiteralPath (Join-Path $game "BepInEx\$MarkerName"))) {
        throw '没有检测到本汉化的安装记录，不做任何改动。'
    }

    $others = Get-ChildItem -LiteralPath (Join-Path $game 'BepInEx\plugins') -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -notlike 'XUnity.*' }
    Write-Host '将从游戏目录删除：'
    $LoaderEntries | Where-Object { Test-Path -LiteralPath (Join-Path $game $_) } | ForEach-Object { Write-Host "  $_" }
    if ($others) {
        Write-Host ''
        Write-Host '注意：BepInEx\plugins 里还有其他插件，会一起被删除：' -ForegroundColor Yellow
        $others | ForEach-Object { Write-Host "  $($_.Name)" }
    }
    if (-not (Confirm-Yes '确认卸载吗？')) { throw '已取消卸载。' }

    foreach ($entry in $LoaderEntries) {
        $path = Join-Path $game $entry
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Recurse -Force }
    }
    Write-Host ''
    Write-Host '卸载完成，游戏已恢复英文原版。'
    Write-Host '如果是从创意工坊安装的，现在可以取消订阅本物品。'
}
catch {
    Write-Host ''
    Write-Host "卸载没有完成：$($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
