# tools/publish-next-cooking.ps1
# PowerShell wrapper for tools/publish_next_cooking.py.
# Daily command from anywhere on disk:
#   .\tools\publish-next-cooking.ps1
# Or pass-through flags:
#   .\tools\publish-next-cooking.ps1 -ArgumentList @('--dry-run')

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript = Join-Path $scriptDir "publish_next_cooking.py"

python $pyScript @args
