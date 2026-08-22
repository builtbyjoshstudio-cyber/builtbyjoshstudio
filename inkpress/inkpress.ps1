# inkpress/inkpress.ps1
# PowerShell wrapper for inkpress.py, matching the tools/publish-next-cooking.ps1 pattern.
# Runs from anywhere on disk:
#   .\inkpress.ps1 manuscripts\sample-manuscript.md
#   .\inkpress.ps1 draft.md --targets site
#   .\inkpress.ps1 draft.md --chrome-from ..\writing\directors-voice.html

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript = Join-Path $scriptDir "inkpress.py"

$python = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }

& $python $pyScript @args
exit $LASTEXITCODE
