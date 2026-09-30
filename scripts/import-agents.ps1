#Requires -Version 5.0

. (Join-Path $PSScriptRoot 'Common.ps1')
Assert-InteractiveTerminal

$repoRoot = Split-Path -Parent $PSScriptRoot
$sources = @(Get-InstructionSources)
$items = @(foreach ($source in $sources) {
    $available = Test-Path -LiteralPath $source.Path -PathType Leaf
    $label = "$($source.Name): $($source.Path)"
    if (-not $available) { $label = "$($source.Name) (unavailable: file missing): $($source.Path)" }

    [pscustomobject]@{ Label = $label; Enabled = $available }
})

$selection = @(Select-ArrowMenu -Title 'Choose one instruction file to copy into the repository' -Items $items)
if ($selection.Count -eq 0) { Write-Host 'Cancelled. No files changed.'; return }

Copy-Instructions -Source $sources[$selection[0]].Path -Destination (Join-Path $repoRoot 'AGENTS.md')
