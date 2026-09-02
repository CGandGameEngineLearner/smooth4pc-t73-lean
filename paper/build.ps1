$ErrorActionPreference = 'Stop'

$paperDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $paperDir
$pinnedTectonic = 'D:\tmp\tectonic\0.17.0\tectonic.exe'

if (Test-Path -LiteralPath $pinnedTectonic) {
    $tectonic = $pinnedTectonic
} else {
    $resolved = Get-Command tectonic -ErrorAction Stop
    $tectonic = $resolved.Source
}

$buildDir = Join-Path $paperDir 'build'
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

Push-Location $paperDir
try {
    & $tectonic 't73_candidate.tex' '--outdir' 'build' '--keep-logs' '--keep-intermediates'
    if ($LASTEXITCODE -ne 0) {
        throw "Tectonic failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

$logPath = Join-Path $buildDir 't73_candidate.log'
if (-not (Test-Path -LiteralPath $logPath)) {
    throw 'Tectonic did not produce t73_candidate.log'
}

$badPatterns = @(
    'LaTeX Warning: Citation .* undefined',
    'LaTeX Warning: Reference .* undefined',
    'There were undefined references',
    'Overfull \\hbox',
    'Overfull \\vbox',
    'TODO',
    'PLACEHOLDER'
)

$logText = Get-Content -Raw -LiteralPath $logPath
foreach ($pattern in $badPatterns) {
    if ($logText -match $pattern) {
        throw "Acceptance check failed: log matched $pattern"
    }
}

$builtPdf = Join-Path $buildDir 't73_candidate.pdf'
$finalPdf = Join-Path $paperDir 'T73_SPC4_CANDIDATE_FALSIFICATION_20260902.pdf'
if (-not (Test-Path -LiteralPath $builtPdf)) {
    throw 'Tectonic did not produce t73_candidate.pdf'
}
Copy-Item -LiteralPath $builtPdf -Destination $finalPdf -Force

$pdfHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $finalPdf).Hash
$pdfBytes = (Get-Item -LiteralPath $finalPdf).Length
$tectonicVersion = (& $tectonic --version | Out-String).Trim()
$tectonicHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $tectonic).Hash

Write-Output "PDF=$finalPdf"
Write-Output "PDF_BYTES=$pdfBytes"
Write-Output "PDF_SHA256=$pdfHash"
Write-Output "TECTONIC_VERSION=$tectonicVersion"
Write-Output "TECTONIC_SHA256=$tectonicHash"
