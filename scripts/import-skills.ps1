#Requires -Version 5.0

. (Join-Path $PSScriptRoot 'Common.ps1')
Assert-InteractiveTerminal

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceDir = Join-Path $HOME '.agents/skills'
$destinationDir = Join-Path $repoRoot 'skills'
if (-not (Test-Path -LiteralPath $sourceDir -PathType Container)) { throw "Skills directory not found: $sourceDir" }

$skills = @(Get-ChildItem -LiteralPath $sourceDir -Directory -Force | Where-Object {
    Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') -PathType Leaf
} | Sort-Object Name)
if ($skills.Count -eq 0) { throw "No skill directories containing SKILL.md found in $sourceDir" }

$items = @(foreach ($skill in $skills) {
    $conflict = Test-Path -LiteralPath (Join-Path $destinationDir $skill.Name)
    $label = $skill.Name
    if ($conflict) { $label += ' (unavailable: name already exists in repo)' }

    [pscustomobject]@{ Label = $label; Enabled = -not $conflict }
})

$selection = @(Select-ArrowMenu -Title 'Import installed skills into this repository' -Items $items -Multiple)
if ($selection.Count -eq 0) { Write-Host 'Cancelled. No files changed.'; return }

if (-not (Test-Path -LiteralPath $destinationDir)) { New-Item -ItemType Directory -Path $destinationDir | Out-Null }
foreach ($index in $selection) {
    $destination = Join-Path $destinationDir $skills[$index].Name
    if (Test-Path -LiteralPath $destination) { throw "Destination now exists: $destination" }

    New-Item -ItemType Directory -Path $destination | Out-Null
    Copy-SkillTree -Source $skills[$index].FullName -Destination $destination
    Write-Host "Imported $($skills[$index].Name)"
}
