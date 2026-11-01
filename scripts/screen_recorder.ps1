# 开发调试用：定时截取主屏幕，缩小后存 JPEG，用于回看用户演示。
# 用法：powershell -File screen_recorder.ps1 -Out <目录> [-Seconds 900] [-Interval 3]
param(
    [Parameter(Mandatory = $true)][string]$Out,
    [int]$Seconds = 900,
    [int]$Interval = 3,
    [int]$Scale = 3
)

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System.Runtime.InteropServices;
public static class Dpi { [DllImport("user32.dll")] public static extern bool SetProcessDPIAware(); }
"@
[Dpi]::SetProcessDPIAware() | Out-Null
Add-Type -AssemblyName System.Windows.Forms

New-Item -ItemType Directory -Force $Out | Out-Null
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$params = New-Object System.Drawing.Imaging.EncoderParameters 1
$params.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [long]70)

$end = (Get-Date).AddSeconds($Seconds)
$i = 0
while ((Get-Date) -lt $end) {
    $full = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $g = [System.Drawing.Graphics]::FromImage($full)
    $g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
    $small = New-Object System.Drawing.Bitmap $full, ([int]($bounds.Width / $Scale)), ([int]($bounds.Height / $Scale))
    $small.Save((Join-Path $Out ("{0:HHmmss}_{1:D4}.jpg" -f (Get-Date), $i)), $codec, $params)
    $g.Dispose(); $full.Dispose(); $small.Dispose()
    $i++
    Start-Sleep -Seconds $Interval
}
"done: $i frames"
