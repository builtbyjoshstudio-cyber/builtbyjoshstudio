# inkpress/bootstrap-inkpress.ps1
# One-time setup and smoke test for inkpress on Windows.
#
#   .\bootstrap-inkpress.ps1
#   .\bootstrap-inkpress.ps1 -SkipSmokeTest
#
# inkpress is standard-library only, so there is no venv and no pip install.
# This script verifies the toolchain, creates the working folders, runs the
# test suite, and builds the sample manuscript so you can see real output
# before pointing it at a real draft.

[CmdletBinding()]
param(
    [switch]$SkipSmokeTest,
    [string]$ChromeFrom
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Step($message) { Write-Host "==> $message" -ForegroundColor Cyan }
function Write-Ok($message)   { Write-Host "    OK  $message" -ForegroundColor Green }
function Write-Warn($message) { Write-Host "    !   $message" -ForegroundColor Yellow }

Write-Step "Checking Python"
$python = $null
foreach ($candidate in @("py", "python3", "python")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) { $python = $candidate; break }
}
if (-not $python) {
    throw "No Python found on PATH. Install Python 3.8+ from https://python.org and re-run."
}

$versionText = (& $python --version 2>&1) -join " "
if ($versionText -notmatch "(\d+)\.(\d+)") {
    throw "Could not read a version from '$python --version' (got: $versionText)"
}
$major = [int]$Matches[1]
$minor = [int]$Matches[2]
if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
    throw "inkpress needs Python 3.8 or newer. Found $versionText."
}
Write-Ok "$versionText via '$python'"

Write-Step "Creating working folders"
foreach ($folder in @("manuscripts", "build")) {
    $path = Join-Path $scriptDir $folder
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Ok "created $folder\"
    } else {
        Write-Ok "$folder\ already present"
    }
}

Write-Step "Running the test suite"
Push-Location $scriptDir
try {
    & $python -m unittest discover -s tests -t . -q
    if ($LASTEXITCODE -ne 0) { throw "Test suite failed (exit $LASTEXITCODE)." }
    Write-Ok "tests passed"
} finally {
    Pop-Location
}

if (-not $SkipSmokeTest) {
    Write-Step "Building the sample manuscript"
    $sample = Join-Path $scriptDir "manuscripts\sample-manuscript.md"
    if (-not (Test-Path $sample)) {
        Write-Warn "sample manuscript missing; skipping smoke test"
    } else {
        Push-Location $scriptDir
        try {
            $buildArgs = @($sample)
            if ($ChromeFrom) { $buildArgs += @("--chrome-from", $ChromeFrom) }
            & $python (Join-Path $scriptDir "inkpress.py") @buildArgs
            if ($LASTEXITCODE -ne 0) { throw "Sample build failed (exit $LASTEXITCODE)." }
            Write-Ok "sample built into build\"
        } finally {
            Pop-Location
        }
    }
}

Write-Step "Checking optional PDF renderers"
$found = @()
foreach ($tool in @("weasyprint", "prince", "pagedjs-cli")) {
    if (Get-Command $tool -ErrorAction SilentlyContinue) { $found += $tool }
}
if ($found.Count -gt 0) {
    Write-Ok ("found: " + ($found -join ", "))
} else {
    Write-Warn "no PDF renderer on PATH - open the print interior in a browser and use Print to PDF,"
    Write-Warn "or install one:  pip install weasyprint"
}

Write-Step "Checking the desktop app"
$tkCheck = & $python -c "import tkinter" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Ok "Tkinter present - double-click inkpress-app.cmd to open the app"
} else {
    Write-Warn "this Python has no Tkinter, so the app window cannot open."
    Write-Warn "Reinstall Python from python.org (the standard installer includes it),"
    Write-Warn "or use the command line below instead."
}

Write-Host ""
Write-Host "inkpress is ready." -ForegroundColor Green
Write-Host "  Open the app:    double-click inkpress-app.cmd"
Write-Host ""
Write-Host "  Or from here:"
Write-Host "  Build a draft:   .\inkpress.ps1 manuscripts\your-draft.md"
Write-Host "  Site page only:  .\inkpress.ps1 manuscripts\your-draft.md --targets site"
Write-Host "  Validate only:   .\inkpress.ps1 manuscripts\your-draft.md --check"
