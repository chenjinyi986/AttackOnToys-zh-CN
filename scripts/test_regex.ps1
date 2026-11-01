# 离线模拟 XUnity 的 r: 正则查找：从文件末尾往前试，第一条匹配即用。
# 用法：powershell -File test_regex.ps1 -RegexFile <AttackOnToys_regex.txt> -Samples <每行一条原文，\n 表示换行>
param(
    [Parameter(Mandatory = $true)][string]$RegexFile,
    [Parameter(Mandatory = $true)][string]$Samples
)
[Console]::OutputEncoding = [Text.Encoding]::UTF8
function Decode([string]$s) { return $s.Replace('\n', "`n").Replace('\r', "`r") }

$rules = @()
foreach ($line in Get-Content $RegexFile -Encoding UTF8) {
    if (-not $line.StartsWith('r:"')) { continue }
    $sep = $line.IndexOf('"=')
    $pat = Decode $line.Substring(3, $sep - 3)
    $rep = Decode $line.Substring($sep + 2)
    $rules += , @([regex]::new($pat), $rep)
}
foreach ($sample in Get-Content $Samples -Encoding UTF8) {
    if (-not $sample) { continue }
    $text = Decode $sample
    $hit = $null
    for ($i = $rules.Count - 1; $i -ge 0; $i--) {
        $m = $rules[$i][0].Match($text)
        if ($m.Success) { $hit = $m.Result($rules[$i][1]); break }
    }
    if ($hit) { "OK   $sample`n  -> $($hit.Replace("`n", '\n'))" } else { "MISS $sample" }
}
