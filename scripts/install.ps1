#Requires -Version 5.0

param(
    [string]$Ref = $(if ($env:AGENTS_REF) { $env:AGENTS_REF } else { 'master' })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-CombinedInstall {
    param([string]$Helpers, [string]$Ref)

    . (Join-Path $Helpers 'Common.ps1')
    Assert-InteractiveTerminal

    $targets = @(Get-InstructionSources)
    $items = @(foreach ($target in $targets) {
        [pscustomobject]@{ Label = "$($target.Name): $($target.Path)"; Enabled = $true }
    })
    $instructions = @(Select-ArrowMenu -Title 'Choose target agents for instructions and skills' -Items $items -Multiple -DefaultAll)
    if ($instructions.Count -eq 0) { Write-Host 'Cancelled. Nothing installed.'; return }

    $skills = @(foreach ($line in Get-Content -LiteralPath (Join-Path $Helpers 'skills.txt')) {
        if ($line.Trim() -and -not $line.Trim().StartsWith('#')) {
            $fields = $line.Trim() -split '\s+'
            if ($fields.Count -ne 2) { throw "Invalid skills.txt entry: $line" }
            [pscustomobject]@{ Source = $fields[0]; Name = $fields[1] }
        }
    })
    $items = @(foreach ($skill in $skills) {
        $kind = 'external'; if ($skill.Source -eq 'lioqing/.agents') { $kind = 'personal' }
        [pscustomobject]@{ Label = "$($skill.Name) ($kind, $($skill.Source))"; Enabled = $true }
    })
    $selection = @(Select-ArrowMenu -Title 'Choose personal and external skills to install globally' -Items $items -Multiple -DefaultAll)
    if ($selection.Count -eq 0) { Write-Host 'Cancelled. Nothing installed.'; return }

    if (-not (Get-Command npx -ErrorAction SilentlyContinue)) { throw 'Node.js/npm (npx) is required to install skills.' }

    $destinations = @(foreach ($index in $instructions) { $targets[$index].Path })
    $agentIds = @{ Claude = 'claude-code'; Codex = 'codex'; OpenCode = 'opencode' }
    $skillAgents = @(foreach ($index in $instructions) { $agentIds[$targets[$index].Name] })
    Write-Host 'Selected instruction destinations (existing files require overwrite confirmation):'
    foreach ($path in $destinations) { Write-Host "  $path" }
    $modes = @(
        [pscustomobject]@{ Label = 'Backup existing files before replacing'; Enabled = $true }
        [pscustomobject]@{ Label = 'Replace without backup'; Enabled = $true }
    )
    $mode = @(Select-ArrowMenu -Title 'Choose how to handle existing instruction files' -Items $modes)
    if ($mode.Count -eq 0) { Write-Host 'Cancelled. Nothing installed.'; return }

    & (Join-Path $Helpers 'install-agents.ps1') -Destination $destinations -Ref $Ref -Backup:($mode[0] -eq 0) -NoBackup:($mode[0] -eq 1)
    $groups = @()
    foreach ($index in $selection) {
        $skill = $skills[$index]
        $group = $groups | Where-Object { $_.Source -eq $skill.Source } | Select-Object -First 1
        if ($null -eq $group) {
            $group = [pscustomobject]@{ Source = $skill.Source; Names = @() }
            $groups += $group
        }
        $group.Names += $skill.Name
    }
    foreach ($group in $groups) {
        $source = $group.Source
        if ($source -eq 'lioqing/.agents') { $source = "https://github.com/lioqing/.agents/tree/$Ref" }
        $names = @($group.Names)
        Write-Host "Installing $($names -join ', ') from $source"
        & npx skills add $source --skill @names --global --yes --agent @skillAgents
        if ($LASTEXITCODE -ne 0) { throw "Skill installation failed: $($names -join ', ') (exit $LASTEXITCODE). Earlier installations may have completed." }
    }
    Write-Host 'Selected agent instructions and skills installed.'
}

# A downloaded/iex entry point fetches its helpers; a clone uses adjacent files.
$helpers = $PSScriptRoot
$temporary = $null
$securityProtocol = [Net.ServicePointManager]::SecurityProtocol
try {
    if (-not $helpers -or -not (Test-Path -LiteralPath (Join-Path $helpers 'Common.ps1') -PathType Leaf)) {
        $temporary = Join-Path ([IO.Path]::GetTempPath()) "install-agents-$([Guid]::NewGuid().ToString('N'))"
        New-Item -ItemType Directory -Path $temporary | Out-Null
        $helpers = $temporary
        [Net.ServicePointManager]::SecurityProtocol = $securityProtocol -bor [Net.SecurityProtocolType]::Tls12
        foreach ($file in @('Common.ps1', 'install-agents.ps1', 'skills.txt')) {
            $path = Join-Path $helpers $file
            Invoke-WebRequest -Uri "https://raw.githubusercontent.com/lioqing/.agents/$Ref/scripts/$file" -OutFile $path -TimeoutSec 120 -UseBasicParsing
            if ((Get-Item -LiteralPath $path).Length -eq 0) { throw "Downloaded $file is empty. Nothing installed." }
        }
    }
    Invoke-CombinedInstall -Helpers $helpers -Ref $Ref
} finally {
    [Net.ServicePointManager]::SecurityProtocol = $securityProtocol
    if ($temporary) { Remove-Item -LiteralPath $temporary -Recurse -Force }
}
