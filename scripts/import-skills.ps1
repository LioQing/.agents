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
    $existing = Get-Item -LiteralPath (Join-Path $destinationDir $skill.Name) -Force -ErrorAction SilentlyContinue
    $available = $null -eq $existing -or ($existing.PSIsContainer -and -not ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint))
    $label = $skill.Name
    if (-not $available) { $label += ' (unavailable: destination is a file or link)' }
    elseif ($null -ne $existing) { $label += ' (already exists in repo: replacement requires confirmation)' }

    [pscustomobject]@{ Label = $label; Enabled = $available }
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

$accepted = @()
foreach ($index in $selection) {
    $destination = Join-Path $destinationDir $skills[$index].Name
    $existing = Get-Item -LiteralPath $destination -Force -ErrorAction SilentlyContinue
    if ($null -ne $existing) {
        if (-not $existing.PSIsContainer -or ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Refusing to replace a file or symbolic link: $destination"
        }

        $answer = Read-Host "Replace ${destination}? [y/N]"
        if ($answer -notmatch '^(y|yes)$') { Write-Host "Skipped $destination"; continue }
    }
    $accepted += [pscustomobject]@{ Index = $index; Destination = $destination; Replace = $null -ne $existing }
}
if ($accepted.Count -eq 0) { return }

if (-not (Test-Path -LiteralPath $destinationDir)) { New-Item -ItemType Directory -Path $destinationDir | Out-Null }
$staging = Join-Path $destinationDir ".import-$([Guid]::NewGuid().ToString('N'))"
New-Item -ItemType Directory -Path $staging | Out-Null
try {
    # Stage every copy first: installed links may target skills being replaced.
    foreach ($item in $accepted) {
        Copy-SkillTree -Source $skills[$item.Index].FullName -Destination (Join-Path $staging $skills[$item.Index].Name)
    }

    foreach ($item in $accepted) {
        $destination = $item.Destination
        $existing = Get-Item -LiteralPath $destination -Force -ErrorAction SilentlyContinue
        if ($null -ne $existing) {
            if (-not $item.Replace -or -not $existing.PSIsContainer -or ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
                throw "Destination changed while importing: $destination"
            }
            $backup = "$destination.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')-$([Guid]::NewGuid().ToString('N').Substring(0, 8))"
            [IO.Directory]::Move($destination, $backup)
            Write-Host "Backup: $backup"
        }
        [IO.Directory]::Move((Join-Path $staging $skills[$item.Index].Name), $destination)
        Write-Host "Imported $($skills[$item.Index].Name)"
    }

    # Remove only successfully imported selections, never declined replacements.
    if ($mode[0] -eq 1) {
        foreach ($item in $accepted) {
            Remove-SkillTree -Path $skills[$item.Index].FullName
            Write-Host "Removed original $($skills[$item.Index].FullName)"
        }
    }
} finally {
    Remove-SkillTree -Path $staging
}

Write-Host "`nReview, commit and push the imported skills, then reinstall/update your home-directory skills:"
Write-Host '  npx skills add lioqing/.agents --global'
