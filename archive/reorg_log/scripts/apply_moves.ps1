param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('R1','R2','R3','R4','R5','R6','R7')]
    [string]$Batch,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logDir = Split-Path -Parent $scriptDir
$root = Split-Path -Parent $logDir
$planPath = Join-Path $logDir 'move_plan.csv'
$manifestPath = Join-Path $logDir 'hash_manifest_before.csv'
$movesPath = Join-Path $logDir 'moves.csv'

if (-not (Test-Path -LiteralPath $planPath)) { throw "Missing plan: $planPath" }
$plan = Import-Csv -LiteralPath $planPath
$manifest = @{}
Import-Csv -LiteralPath $manifestPath | ForEach-Object { $manifest[$_.path] = $_ }

function Get-BatchName([string]$category, [string]$oldPath) {
    if ($category -eq 'residue' -or $oldPath -eq 'README.md') { return 'R1' }
    if ($category -eq 'version') { return 'R2' }
    if ($category -eq 'evidence') { return 'R3' }
    if ($category -in @('doc','course_reference')) { return 'R4' }
    if ($category -eq 'data') { return 'R5' }
    if ($category -eq 'handin') { return 'R6' }
    if ($category -in @('pipeline_entry','pipeline_metadata')) { return 'R7' }
    return 'ROOT'
}

$rows = @($plan | Where-Object { (Get-BatchName $_.category $_.old_path) -eq $Batch })
if ($rows.Count -eq 0) { throw "No plan rows for $Batch" }

$totalBytes = 0L
foreach ($r in $rows) {
    $totalBytes += [int64]$manifest[$r.old_path].size_bytes
}
Write-Output "BATCH=$Batch FILES=$($rows.Count) BYTES=$totalBytes DRYRUN=$DryRun"

# Preconditions: every source exists, every destination is free.
foreach ($r in $rows) {
    $old = Join-Path $root $r.old_path
    $new = Join-Path $root $r.new_path
    if (-not (Test-Path -LiteralPath $old -PathType Leaf)) { throw "SOURCE MISSING: $old" }
    if (Test-Path -LiteralPath $new) { throw "DEST EXISTS: $new" }
}

if ($DryRun) {
    foreach ($r in $rows) { Write-Output ("WOULD_MOVE {0} -> {1}" -f $r.old_path, $r.new_path) }
    Write-Output 'DRY-RUN: no filesystem changes'
    exit 0
}

# Resume safety: never move a path twice.
if (Test-Path -LiteralPath $movesPath) {
    $done = Import-Csv -LiteralPath $movesPath
    $doneOld = @{}; $doneNew = @{}
    foreach ($d in $done) { $doneOld[$d.old_path] = $true; $doneNew[$d.new_path] = $true }
    foreach ($r in $rows) {
        if ($doneOld.ContainsKey($r.old_path) -or $doneNew.ContainsKey($r.new_path)) {
            throw "ALREADY LOGGED: $($r.old_path) -> $($r.new_path)"
        }
    }
}

$records = New-Object System.Collections.Generic.List[object]
$seq = 0
foreach ($r in $rows) {
    $seq++
    $oldRel = $r.old_path
    $newRel = $r.new_path
    $old = Join-Path $root $oldRel
    $new = Join-Path $root $newRel
    $newParent = Split-Path -Parent $new
    if (-not (Test-Path -LiteralPath $newParent)) { New-Item -ItemType Directory -Path $newParent -Force | Out-Null }

    $before = Get-Item -LiteralPath $old
    $bytes = [int64]$before.Length
    $ticks = $before.LastWriteTimeUtc.Ticks
    $sha = [string]$manifest[$oldRel].sha256
    if ([string]::IsNullOrWhiteSpace($sha)) { throw "No manifest SHA for $oldRel" }

    if ($r.tracked -eq 'yes') {
        & git -C $root -c core.quotepath=off mv -- $oldRel $newRel
        if ($LASTEXITCODE -ne 0) { throw "git mv failed: $oldRel -> $newRel" }
    } else {
        Move-Item -LiteralPath $old -Destination $new
    }

    if (-not (Test-Path -LiteralPath $new -PathType Leaf)) { throw "MOVE VERIFY FAILED (missing): $new" }
    if (Test-Path -LiteralPath $old) { throw "MOVE VERIFY FAILED (source remains): $old" }
    $after = Get-Item -LiteralPath $new
    if ($after.Length -ne $bytes) { throw "SIZE CHANGED: $oldRel -> $newRel" }
    if ($after.LastWriteTimeUtc.Ticks -ne $ticks) { throw "MTIME CHANGED: $oldRel -> $newRel" }

    $records.Add([pscustomobject]@{
        seq = $seq
        batch = $Batch
        old_path = $oldRel
        new_path = $newRel
        sha256_before = $sha
        bytes = $bytes
        mtime_utc_ticks = $ticks
        tracked = $r.tracked
        moved_utc = (Get-Date).ToUniversalTime().ToString('o')
    })
}

# Same-commit ignore edit (R1-R5 only).
if ($Batch -in @('R1','R2','R3','R4','R5')) {
    $stage = Join-Path $logDir ("gitignore_" + $Batch + ".txt")
    if (-not (Test-Path -LiteralPath $stage)) { throw "Missing ignore stage: $stage" }
    Copy-Item -LiteralPath $stage -Destination (Join-Path $root '.gitignore') -Force
}

# Stage only this batch's source/destination paths plus .gitignore; never the log.
$stagePaths = switch ($Batch) {
    'R1' { @('README.md','archive','.gitignore') }
    'R2' { @('v1_frozen','v2_work','v3_addons','v4_addons','versions','.gitignore') }
    'R3' { @('analysis_outputs','evidence','.gitignore') }
    'R4' { @('FINAL_ASSESSMENT_HANDOFF.md','FINAL_ASSESSMENT_READING_NOTE.md','FINAL_V2_UPGRADE_REPORT.md','README.docx','ENG_Company _A_ Dataset Overview.docx','tutorial (2).ipynb','docs','.gitignore') }
    'R5' { @('telecom','data','.gitignore') }
    'R6' { @('philopateer.ipynb','philopateer.pdf','philopateer.pptx','submission') }
    'R7' { @('analysis_pipeline.py','build_notebook.py','export_and_verify.py','restore_v1.py','references.txt','requirements-python311.txt','pipeline') }
}
& git -C $root add -A -- @stagePaths
if ($LASTEXITCODE -ne 0) { throw 'git add failed' }

$records | Export-Csv -LiteralPath $movesPath -Append -NoTypeInformation -Encoding utf8
Write-Output "MOVED=$($records.Count) LOGGED_TO=$movesPath"
Write-Output 'STAGED: review with batch_verify.py before committing.'
