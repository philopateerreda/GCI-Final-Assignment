param(
    [switch]$WhatIf,
    [string]$Batch
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logDir = Split-Path -Parent $scriptDir
$root = $scriptDir
while (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) {
    $parent = Split-Path -Parent $root
    if ([string]::IsNullOrEmpty($parent) -or $parent -eq $root) { throw "Repository root not found" }
    $root = $parent
}
$movesPath = Join-Path $logDir 'moves.csv'
if (-not (Test-Path -LiteralPath $movesPath)) { throw "Missing moves log: $movesPath" }
$moves = @(Import-Csv -LiteralPath $movesPath)
if ($Batch) {
    $moves = @($moves | Where-Object { $_.batch -eq $Batch })
}
$moves = @($moves | Sort-Object { [int]$_.seq } -Descending)

$done = 0
$conflicts = 0
foreach ($m in $moves) {
    $new = Join-Path $root $m.new_path
    $old = Join-Path $root $m.old_path
    if (-not (Test-Path -LiteralPath $new -PathType Leaf)) { throw "MISSING NEW: $new" }
    if (Test-Path -LiteralPath $old) {
        # A later file may legitimately reuse the old path (e.g. the new root
        # README). Report it in a dry run; a real undo still stops.
        if ($WhatIf) {
            Write-Output ("CONFLICT_OLD_EXISTS {0} -> {1}" -f $m.new_path, $m.old_path)
            $conflicts++
            continue
        }
        throw "OLD ALREADY EXISTS: $old"
    }
    if ($WhatIf) {
        Write-Output ("WOULD_MOVE {0} -> {1}" -f $m.new_path, $m.old_path)
        $done++
        continue
    }
    $parent = Split-Path -Parent $old
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    if ($m.tracked -eq 'yes') {
        & git -C $root -c core.quotepath=off mv -- $m.new_path $m.old_path
        if ($LASTEXITCODE -ne 0) { throw "git mv failed: $($m.new_path) -> $($m.old_path)" }
    } else {
        Move-Item -LiteralPath $new -Destination $old
    }
    $done++
}
Write-Output "UNDO moves=$($moves.Count) done=$done conflicts=$conflicts WhatIf=$WhatIf Batch=$Batch"
