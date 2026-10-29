#Requires -Version 5.0
# Run: pwsh -File ./tests/test-install.ps1
# Combined installer integration tests. Downloads, npx, and menus are mocked.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Join-Path ([IO.Path]::GetTempPath()) "combined-install-$([Guid]::NewGuid().ToString('N'))"
$repo = Join-Path $root 'repo with spaces'
$originalHome = $HOME
$originalRef = $env:AGENTS_REF

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "Assertion failed: $Message" }
}
function Get-OptionValues([object[]]$Command, [string]$Option) {
    $start = [Array]::IndexOf($Command, $Option) + 1
    if ($start -eq 0) { return }
    for ($i = $start; $i -lt $Command.Count -and -not $Command[$i].StartsWith('-'); $i++) { $Command[$i] }
}
function Reset-Test {
    $global:InstallMenus = @()
    $global:InstallCommands = @()
    $global:InstallDownloads = @()
    $global:InstallCancel = ''
    $global:InstallTargets = @(0, 1, 2)
    $global:InstallSkills = @(0..7)
    $global:InstallBackup = 0
    $global:InstallFailSkill = ''
    $global:InstallFailDownload = ''
    $global:InstallOverwrite = 'yes'
    $global:InstallMissingNpx = $false
}
function Invoke-WebRequest {
    param($Uri, $OutFile, $TimeoutSec, [switch]$UseBasicParsing)
    $global:InstallDownloads += [pscustomobject]@{ Uri = $Uri; Path = $OutFile }
    if ($Uri.EndsWith($global:InstallFailDownload) -and $global:InstallFailDownload) { throw 'Simulated download failure' }
    if ($Uri.EndsWith('/AGENTS.md')) { [IO.File]::WriteAllText($OutFile, "remote instructions`n") }
    else { Copy-Item -LiteralPath (Join-Path $repo "scripts/$(Split-Path -Leaf $Uri)") -Destination $OutFile }
}

try {
    New-Item -ItemType Directory -Path $repo -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path (Split-Path -Parent $PSScriptRoot) 'scripts') -Destination $repo -Recurse
    $mock = @'
function Assert-InteractiveTerminal { }
function Select-ArrowMenu {
    param($Title, $Items, [switch]$Multiple, [switch]$DefaultAll)
    $global:InstallMenus += [pscustomobject]@{ Title = $Title; Items = $Items; Multiple = [bool]$Multiple; DefaultAll = [bool]$DefaultAll }
    if ($Title -eq $global:InstallCancel) { return }
    switch ($Title) {
        'Choose target agents for instructions and skills' { $global:InstallTargets }
        'Choose personal and external skills to install globally' { $global:InstallSkills }
        'Choose how to handle existing instruction files' { $global:InstallBackup }
        default { throw "Unexpected menu: $Title" }
    }
}
function Read-Host { param($Prompt) $global:InstallOverwrite }
function Get-Command {
    param($Name, $ErrorAction)
    if ($Name -ne 'npx') { throw "Unexpected command lookup: $Name" }
    if (-not $global:InstallMissingNpx) { 'mock npx' }
}
function npx {
    if ($args -notcontains '--agent') { throw 'PromptScript: PromptScript does not support global skill installation' }
    $global:InstallCommands += ,@($args)
    $global:LASTEXITCODE = 0
    if ($args -contains $global:InstallFailSkill) { $global:LASTEXITCODE = 7 }
}
'@
    Add-Content -LiteralPath (Join-Path $repo 'scripts/Common.ps1') -Value $mock
    Set-Variable -Name HOME -Value (Join-Path $root 'home with spaces') -Scope Script -Force
    $env:AGENTS_REF = 'test-ref'
    $entry = Join-Path $repo 'scripts/install.ps1'
    Reset-Test
    & $entry
    Assert-True ($global:InstallMenus.Count -eq 3) 'three menus in order'
    Assert-True ($global:InstallMenus[0].DefaultAll -and $global:InstallMenus[1].DefaultAll) 'both selection menus default to all'
    Assert-True ($global:InstallMenus[0].Items.Count -eq 3 -and $global:InstallMenus[1].Items.Count -eq 8) 'all targets and skills offered'
    Assert-True ($global:InstallCommands.Count -eq 4) 'all eight skills installed in four source batches'
    Assert-True (($global:InstallCommands[0] -join ' ') -eq 'skills add https://github.com/lioqing/.agents/tree/test-ref --skill blender-workflow guided-learning html-report markdown-slides markdown-slides-prep --global --yes --agent claude-code codex opencode') 'personal skills batched with selected ref and agents'
    Assert-True (($global:InstallCommands[1] -join ' ') -eq 'skills add petergyang/no-ai-slop --skill no-ai-slop --global --yes --agent claude-code codex opencode') 'external skill uses upstream source and selected agents'
    foreach ($command in $global:InstallCommands) {
        Assert-True (((Get-OptionValues $command '--agent') -join ' ') -eq 'claude-code codex opencode') 'every batch targets only selected supported agents'
    }
    foreach ($path in @('.claude/CLAUDE.md', '.codex/AGENTS.md', '.config/opencode/AGENTS.md')) {
        Assert-True ((Get-Content -LiteralPath (Join-Path $HOME $path) -Raw) -eq "remote instructions`n") "installed $path"
    }

    Reset-Test
    $global:InstallTargets = @(1)
    $global:InstallSkills = @(6, 7)
    $global:InstallBackup = 1
    & $entry -Ref 'pinned-ref'
    Assert-True ($global:InstallCommands.Count -eq 2) 'only chosen skills installed'
    Assert-True ($global:InstallCommands[0][2] -eq 'JuliusBrussee/caveman' -and $global:InstallCommands[1][4] -eq 'grilling') 'chosen external sources used'
    foreach ($command in $global:InstallCommands) {
        Assert-True (((Get-OptionValues $command '--agent') -join ' ') -eq 'codex') 'Codex-only selection limits all skill targets'
    }
    Assert-True (@(Get-ChildItem -LiteralPath (Join-Path $HOME '.codex') -Filter '*.backup-*').Count -eq 0) 'no-backup option forwarded'
    Assert-True ($global:InstallDownloads[0].Uri.Contains('/pinned-ref/')) 'explicit ref forwarded'

    Reset-Test
    $global:InstallSkills = @(0, 5, 2, 7)
    & $entry
    Assert-True ($global:InstallCommands.Count -eq 3) 'subset selections are grouped by repository'
    Assert-True (((Get-OptionValues $global:InstallCommands[0] '--skill') -join ' ') -eq 'blender-workflow html-report') 'personal batch contains only selected names'
    Assert-True ($global:InstallCommands[1][2] -eq 'petergyang/no-ai-slop' -and $global:InstallCommands[2][2] -eq 'mattpocock/skills') 'external repositories use separate batches'

    foreach ($title in @('Choose target agents for instructions and skills', 'Choose personal and external skills to install globally', 'Choose how to handle existing instruction files')) {
        Reset-Test
        $global:InstallCancel = $title
        & $entry
        Assert-True ($global:InstallCommands.Count -eq 0 -and $global:InstallDownloads.Count -eq 0) 'cancellation installs and downloads nothing from clone'
    }

    Reset-Test
    $global:InstallMissingNpx = $true
    $failed = $false
    try { & $entry } catch { $failed = $_.Exception.Message.Contains('npx') }
    Assert-True ($failed -and $global:InstallDownloads.Count -eq 0) 'missing npx detected before instruction changes'

    Reset-Test
    $global:InstallFailSkill = 'guided-learning'
    $failed = $false
    try { & $entry } catch { $failed = $_.Exception.Message.Contains('guided-learning') }
    Assert-True ($failed -and $global:InstallCommands.Count -eq 1) 'failure within first batch stops subsequent batches'

    Reset-Test
    $global:InstallFailDownload = '/AGENTS.md'
    $failed = $false
    try { & $entry } catch { $failed = $true }
    Assert-True ($failed -and $global:InstallCommands.Count -eq 0) 'instruction failure prevents skill installs'

    Reset-Test
    $global:InstallOverwrite = 'no'
    & $entry
    Assert-True ($global:InstallCommands.Count -eq 4) 'declined instruction overwrites still install skill batches'

    # iex has no adjacent helpers and must bootstrap from the chosen ref.
    Reset-Test
    $global:InstallTargets = @(2)
    $global:InstallSkills = @(7)
    Invoke-Expression (Get-Content -LiteralPath $entry -Raw)
    Assert-True ($global:InstallDownloads.Count -eq 4) 'iex downloads three helpers and instructions'
    Assert-True ($global:InstallDownloads[0].Uri -eq 'https://raw.githubusercontent.com/lioqing/.agents/test-ref/scripts/Common.ps1') 'remote helper uses chosen ref'
    Assert-True (-not (Test-Path -LiteralPath (Split-Path -Parent $global:InstallDownloads[0].Path))) 'remote helpers cleaned up'
    Assert-True ($global:InstallCommands.Count -eq 1 -and $global:InstallCommands[0][4] -eq 'grilling') 'iex installs selected external skill'
    Assert-True (((Get-OptionValues $global:InstallCommands[0] '--agent') -join ' ') -eq 'opencode') 'iex honors OpenCode-only selection'

    foreach ($indexes in @(@(0), @(0, 2))) {
        Reset-Test
        $global:InstallTargets = $indexes
        $global:InstallSkills = @(0)
        & $entry
        $expected = 'claude-code'
        if ($indexes.Count -eq 2) { $expected += ' opencode' }
        $command = $global:InstallCommands[0]
        Assert-True (((Get-OptionValues $command '--agent') -join ' ') -eq $expected) 'Claude and noncontiguous selections map to exact skill targets'
    }

    Reset-Test
    $global:InstallFailDownload = '/skills.txt'
    $failed = $false
    try { Invoke-Expression (Get-Content -LiteralPath $entry -Raw) } catch { $failed = $true }
    Assert-True ($failed -and $global:InstallCommands.Count -eq 0) 'bootstrap failure installs nothing'
    Assert-True (-not (Test-Path -LiteralPath (Split-Path -Parent $global:InstallDownloads[0].Path))) 'failed bootstrap cleaned up'
    Write-Host 'Combined PowerShell installer tests passed.'
} finally {
    Set-Variable -Name HOME -Value $originalHome -Scope Script -Force
    $env:AGENTS_REF = $originalRef
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
    Remove-Variable InstallMenus, InstallCommands, InstallDownloads, InstallCancel, InstallTargets, InstallSkills, InstallBackup, InstallFailSkill, InstallFailDownload, InstallOverwrite, InstallMissingNpx -Scope Global -ErrorAction SilentlyContinue
}
