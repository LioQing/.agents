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

Write-Host 'Move removes the selected originals after all copies succeed. Links are removed, not their targets.'
$modes = @(
    [pscustomobject]@{ Label = 'Copy (keep originals)'; Enabled = $true }
    [pscustomobject]@{ Label = 'Move (remove originals after copying)'; Enabled = $true }
)
$mode = @(Select-ArrowMenu -Title 'Choose how to import selected skills' -Items $modes)
if ($mode.Count -eq 0) { Write-Host 'Cancelled. No files changed.'; return }

if (-not (Test-Path -LiteralPath $destinationDir)) { New-Item -ItemType Directory -Path $destinationDir | Out-Null }
foreach ($index in $selection) {
    $destination = Join-Path $destinationDir $skills[$index].Name
    if (Test-Path -LiteralPath $destination) { throw "Destination now exists: $destination" }

    New-Item -ItemType Directory -Path $destination | Out-Null
    Copy-SkillTree -Source $skills[$index].FullName -Destination $destination
    Write-Host "Imported $($skills[$index].Name)"
}

# Copy every selection first: one selected link may target another selected skill.
if ($mode[0] -eq 1) {
    foreach ($index in $selection) {
        Remove-SkillTree -Path $skills[$index].FullName
        Write-Host "Removed original $($skills[$index].FullName)"
    }
}

Write-Host "`nReview, commit and push the imported skills, then reinstall/update your home-directory skills:"
Write-Host '  npx skills add lioqing/.agents --global'
