#Requires -Version 5.0
# Run: pwsh -File ./tests/test-scripts.ps1
# Menu/input are mocked; all copies happen in an isolated temporary home/repo.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Join-Path ([IO.Path]::GetTempPath()) "agent-scripts-$([Guid]::NewGuid().ToString('N'))"
$repo = Join-Path $root 'repo with spaces'
$testHome = Join-Path $root 'home with spaces'
$originalHome = $HOME

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "Assertion failed: $Message" }
}
function Write-Fixture([string]$Path, [string]$Content) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force | Out-Null
    [IO.File]::WriteAllText($Path, $Content)
}
try {
    New-Item -ItemType Directory -Path $repo -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path (Split-Path -Parent $PSScriptRoot) 'scripts') -Destination $repo -Recurse
    $common = Join-Path $repo 'scripts/Common.ps1'
    . $common
    $actualMenu = ${function:Select-ArrowMenu}
    # Inject mocks only into sandbox copies, not the repository implementation.
    $mocks = @'
function Assert-InteractiveTerminal {}
function Select-ArrowMenu {
    param($Title, $Items, [switch]$Multiple)
    $global:CapturedItems = $Items
    $global:CapturedMultiple = [bool]$Multiple
    $global:MenuSelection
}
function Read-Host { param($Prompt) $global:OverwriteAnswer }
'@
    Add-Content -LiteralPath $common -Value $mocks
    $downloadMock = @'
function Invoke-WebRequest {
    param($Uri, $OutFile, $TimeoutSec, [switch]$UseBasicParsing)
    Assert-True ([bool]$UseBasicParsing) 'download does not require Internet Explorer'
    Assert-True ([bool]([Net.ServicePointManager]::SecurityProtocol -band [Net.SecurityProtocolType]::Tls12)) 'TLS 1.2 enabled for download'
    $global:DownloadCount++
    $global:DownloadUri = $Uri
    $global:DownloadPath = $OutFile
    if ($global:DownloadFails) { throw 'Simulated HTTP failure' }
    [IO.File]::WriteAllText($OutFile, $global:RemoteContent)
}
'@
    # Place a standalone installer outside the repo, as if downloaded from GitHub.
    $standalone = Join-Path $root 'install-agents.ps1'
    $entry = 'Invoke-AgentsInstall -Destination @($Destination) -Ref $Ref'
    $installer = Get-Content -LiteralPath (Join-Path $repo 'scripts/install-agents.ps1') -Raw
    Invoke-Expression ($installer.Replace($entry, ''))
    $actualInstallerMenu = ${function:Select-ArrowMenu}
    $installer = $installer.Replace($entry, "$mocks`n$downloadMock`n$entry")
    [IO.File]::WriteAllText($standalone, $installer)
    Set-Variable -Name HOME -Value $testHome -Scope Script -Force
    $global:OverwriteAnswer = 'yes'
    $global:MenuSelection = @(0, 1, 2)
    $global:DownloadCount = 0
    $global:DownloadFails = $false
    $global:RemoteContent = "remote instructions`n"
    Write-Fixture (Join-Path $repo 'AGENTS.md') "repository instructions`n"
    Write-Fixture (Join-Path $HOME '.claude/CLAUDE.md') 'previous Claude instructions'
    & $standalone -Ref 'test-ref'
    Assert-True $global:CapturedMultiple 'installer uses multi-select'
    Assert-True ($global:DownloadCount -eq 1) 'one download for multiple targets'
    Assert-True ($global:DownloadUri -eq 'https://raw.githubusercontent.com/lioqing/.agents/test-ref/AGENTS.md') 'requested ref used'
    Assert-True (-not (Test-Path -LiteralPath $global:DownloadPath)) 'temporary download removed'
    foreach ($path in @('.claude/CLAUDE.md', '.codex/AGENTS.md', '.config/opencode/AGENTS.md')) {
        Assert-True ((Get-Content -LiteralPath (Join-Path $HOME $path) -Raw) -eq "remote instructions`n") "installed $path"
    }
    $backup = @(Get-ChildItem -LiteralPath (Join-Path $HOME '.claude') -Filter '*.backup-*')
    Assert-True ($backup.Count -eq 1) 'one backup created'
    Assert-True ((Get-Content -LiteralPath $backup[0].FullName -Raw) -eq 'previous Claude instructions') 'backup preserves content'

    $global:OverwriteAnswer = 'no'
    Write-Fixture (Join-Path $repo 'AGENTS.md') 'changed instructions'
    $global:MenuSelection = @(0)
    & $standalone
    Assert-True ((Get-Content -LiteralPath (Join-Path $HOME '.claude/CLAUDE.md') -Raw) -eq "remote instructions`n") 'declined overwrite leaves file alone'

    $global:MenuSelection = @()
    $beforeCancel = $global:DownloadCount
    & $standalone
    Assert-True ($global:DownloadCount -eq $beforeCancel) 'cancel does not download'

    # Invoke-Expression must work without a script location or helper files.
    $global:OverwriteAnswer = 'yes'
    $global:MenuSelection = @(1)
    Invoke-Expression $installer
    Assert-True ((Get-Content -LiteralPath (Join-Path $HOME '.codex/AGENTS.md') -Raw) -eq "remote instructions`n") 'iex installation works'

    $custom = Join-Path $HOME 'custom path/instructions.md'
    & $standalone -Destination $custom
    Assert-True ((Get-Content -LiteralPath $custom -Raw) -eq "remote instructions`n") 'explicit custom destination works'
    $global:MenuSelection = @(3)
    $global:OverwriteAnswer = Join-Path $HOME 'menu custom/instructions.md'
    & $standalone
    Assert-True (Test-Path -LiteralPath $global:OverwriteAnswer) 'custom menu destination works'
    $global:OverwriteAnswer = 'yes'

    $global:DownloadFails = $true
    $failed = $false
    try { & $standalone -Destination $custom } catch { $failed = $true }
    Assert-True $failed 'HTTP failure reported'
    Assert-True (-not (Test-Path -LiteralPath $global:DownloadPath)) 'failed download cleaned up'
    $global:DownloadFails = $false
    $global:RemoteContent = ''
    $failed = $false
    try { & $standalone -Destination $custom } catch { $failed = $true }
    Assert-True $failed 'empty response rejected'
    Assert-True ((Get-Content -LiteralPath $custom -Raw) -eq "remote instructions`n") 'failed downloads leave file unchanged'
    Assert-True (@(Get-ChildItem -LiteralPath (Split-Path -Parent $custom) -Filter '*.backup-*').Count -eq 0) 'no backups on download failure'
    $global:RemoteContent = "remote instructions`n"

    $failed = $false
    try { & $standalone -Destination $HOME } catch { $failed = $true }
    Assert-True $failed 'directory replacement rejected'
    $linkedDestination = Join-Path $HOME 'linked-destination'
    $linkType = if ($env:OS -eq 'Windows_NT') { 'Junction' } else { 'SymbolicLink' }
    New-Item -ItemType $linkType -Path $linkedDestination -Target (Split-Path -Parent $custom) | Out-Null
    $failed = $false
    try { & $standalone -Destination $linkedDestination } catch { $failed = $true }
    Assert-True $failed 'linked destination rejected'

    $global:OverwriteAnswer = 'yes'
    Write-Fixture (Join-Path $HOME '.codex/AGENTS.md') 'Codex source'
    $global:MenuSelection = @(1)
    & (Join-Path $repo 'scripts/import-agents.ps1')
    Assert-True (-not $global:CapturedMultiple) 'instruction import is single-select'
    Assert-True ((Get-Content -LiteralPath (Join-Path $repo 'AGENTS.md') -Raw) -eq 'Codex source') 'instruction source copied verbatim'

    Write-Fixture (Join-Path $HOME '.agents/skills/alpha/SKILL.md') 'alpha skill'
    Write-Fixture (Join-Path $HOME '.agents/skills/alpha/.hidden') 'hidden asset'
    Write-Fixture (Join-Path $HOME '.agents/skills/alpha/assets/file [1].txt') 'nested asset'
    Write-Fixture (Join-Path $HOME '.agents/skills/conflict/SKILL.md') 'do not import'
    Write-Fixture (Join-Path $HOME '.agents/skills/invalid/not-a-skill.txt') 'invalid'
    Write-Fixture (Join-Path $repo 'skills/conflict') 'existing file with conflicting name'
    $global:MenuSelection = @(0)
    & (Join-Path $repo 'scripts/import-skills.ps1')
    Assert-True $global:CapturedMultiple 'skill import is multi-select'
    Assert-True ($global:CapturedItems.Count -eq 2) 'invalid skill excluded'
    Assert-True (-not $global:CapturedItems[1].Enabled) 'conflict disabled'
    Assert-True ($global:CapturedItems[1].Label -like '*unavailable*') 'conflict visibly unavailable'
    Assert-True ((Get-Content -LiteralPath (Join-Path $repo 'skills/alpha/.hidden') -Raw) -eq 'hidden asset') 'hidden file copied'
    Assert-True ((Get-Content -LiteralPath (Join-Path $repo 'skills/alpha/assets/file [1].txt') -Raw) -eq 'nested asset') 'nested file with literal brackets copied'
    Assert-True ((Get-Content -LiteralPath (Join-Path $repo 'skills/conflict') -Raw) -eq 'existing file with conflicting name') 'conflict untouched'

    $global:MenuSelection = @()
    & (Join-Path $repo 'scripts/import-skills.ps1')
    Assert-True (-not $global:CapturedItems[0].Enabled) 'newly imported skill is now unavailable'

    # Directory link imports should produce real directories, not home links.
    $linked = Join-Path $HOME '.agents/skills/linked'
    $linkType = if ($env:OS -eq 'Windows_NT') { 'Junction' } else { 'SymbolicLink' }
    New-Item -ItemType $linkType -Path $linked -Target (Join-Path $HOME '.agents/skills/alpha') | Out-Null
    $global:MenuSelection = @(2)
    & (Join-Path $repo 'scripts/import-skills.ps1')
    $copied = Get-Item -LiteralPath (Join-Path $repo 'skills/linked')
    Assert-True (-not ($copied.Attributes -band [IO.FileAttributes]::ReparsePoint)) 'directory link dereferenced'
    Assert-True (Test-Path -LiteralPath (Join-Path $copied.FullName 'SKILL.md')) 'linked content copied'

    # Exercise the real menu logic using synthetic ConsoleKey values.
    function Read-MenuKey {
        if ($global:KeyIndex -ge $global:Keys.Count) { throw 'Menu requested unexpected extra input.' }
        $key = $global:Keys[$global:KeyIndex]
        $global:KeyIndex++
        [pscustomobject]@{ Key = $key }
    }
    $menuItems = @(
        [pscustomobject]@{ Label = 'Unavailable'; Enabled = $false }
        [pscustomobject]@{ Label = 'One'; Enabled = $true }
        [pscustomobject]@{ Label = 'Two'; Enabled = $true }
    )
    $global:Keys = @('Spacebar', 'Enter', 'DownArrow', 'Spacebar', 'DownArrow', 'Spacebar', 'Enter')
    $global:KeyIndex = 0
    $indexes = @(& $actualMenu -Title 'Multi-select test' -Items $menuItems -Multiple)
    Assert-True (($indexes -join ',') -eq '1,2') 'real menu multi-select and disabled choice handling'
    $global:Keys = @('Enter', 'UpArrow', 'Enter')
    $global:KeyIndex = 0
    $indexes = @(& $actualMenu -Title 'Single-select test' -Items $menuItems)
    Assert-True (($indexes -join ',') -eq '2') 'real menu single-select, disabled source, and arrow wrap'
    $global:Keys = @('Escape')
    $global:KeyIndex = 0
    $indexes = @(& $actualMenu -Title 'Cancel test' -Items $menuItems)
    Assert-True ($indexes.Count -eq 0) 'real menu Escape cancellation'
    $indexes = @(& $actualMenu -Title 'Unavailable test' -Items @($menuItems[0]))
    Assert-True ($indexes.Count -eq 0) 'real menu handles no enabled choices'

    $global:Keys = @('Spacebar', 'DownArrow', 'Spacebar', 'Enter')
    $global:KeyIndex = 0
    $indexes = @(& $actualInstallerMenu -Title 'Standalone installer menu test' -Items $menuItems[1..2] -Multiple)
    Assert-True (($indexes -join ',') -eq '0,1') 'standalone installer menu multi-select'
    $global:Keys = @('Escape')
    $global:KeyIndex = 0
    $indexes = @(& $actualInstallerMenu -Title 'Standalone installer cancel test' -Items $menuItems[1..2] -Multiple)
    Assert-True ($indexes.Count -eq 0) 'standalone installer menu cancellation'
    Write-Host 'PowerShell tests passed.'
} finally {
    Set-Variable -Name HOME -Value $originalHome -Scope Script -Force
    # Only remove the unique sandbox created by this test.
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
    Remove-Variable MenuSelection, OverwriteAnswer, CapturedItems, CapturedMultiple, Keys, KeyIndex, RemoteContent, DownloadCount, DownloadUri, DownloadPath, DownloadFails -Scope Global -ErrorAction SilentlyContinue
}
