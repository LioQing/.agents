#Requires -Version 5.0

param(
    [string[]]$Destination = @(),
    [string]$Ref = $(if ($env:AGENTS_REF) { $env:AGENTS_REF } else { 'master' }),
    [switch]$Backup,
    [switch]$NoBackup
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-InteractiveTerminal {
    if ([Console]::IsInputRedirected -or [Console]::IsOutputRedirected -or $env:TERM -eq 'dumb') {
        throw 'Run this script in an interactive terminal with ANSI support.'
    }
}

function Read-MenuKey { [Console]::ReadKey($true) }

function Select-ArrowMenu {
    param([string]$Title, [object[]]$Items, [switch]$Multiple)

    $cursor = 0
    $selected = New-Object 'bool[]' $Items.Count
    $rows = 0
    $escape = [char]27
    $width = 80
    if (-not [Console]::IsOutputRedirected) { $width = [Console]::WindowWidth }
    if ($width -lt 20) { $width = 80 }

    [Console]::Write("$escape[?25l")
    try {
        while ($true) {
            if ($rows -gt 0) { [Console]::Write("$escape[$($rows)A`r$escape[J") }
            [Console]::WriteLine($Title)
            if ($Multiple) {
                [Console]::WriteLine('Up/Down: move | Space: toggle | Enter: confirm | Esc/q: cancel')
            } else {
                [Console]::WriteLine('Up/Down: move | Enter: choose | Esc/q: cancel')
            }
            for ($i = 0; $i -lt $Items.Count; $i++) {
                $pointer = ' '; if ($i -eq $cursor) { $pointer = '>' }
                $mark = ' '; if ($selected[$i]) { $mark = 'x' }
                $line = "$pointer [$mark] $($Items[$i].Label)"
                if ($line.Length -ge $width) { $line = $line.Substring(0, $width - 1) }
                [Console]::WriteLine($line)
            }
            $rows = $Items.Count + 2
            $key = Read-MenuKey
            switch ($key.Key) {
                UpArrow { $cursor = ($cursor + $Items.Count - 1) % $Items.Count }
                DownArrow { $cursor = ($cursor + 1) % $Items.Count }
                Spacebar { if ($Multiple) { $selected[$cursor] = -not $selected[$cursor] } }
                Enter {
                    if ($Multiple) {
                        $result = @(for ($i = 0; $i -lt $Items.Count; $i++) { if ($selected[$i]) { $i } })
                        if ($result.Count -gt 0) { return $result }
                    } else { return $cursor }
                }
                Escape { return }
                Q { return }
            }
        }
    } finally {
        [Console]::Write("$escape[?25h")
    }
}

function Copy-Instructions {
    param([string]$Source, [string]$Destination, [bool]$Backup = $true)

    # Get-Item also detects dangling links, which must not be overwritten.
    $existing = Get-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
    if ($null -ne $existing) {
        if ($existing.PSIsContainer -or ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Refusing to replace a directory or symbolic link: $Destination"
        }
        $answer = Read-Host "Replace ${Destination}? [y/N]"
        if ($answer -notmatch '^(y|yes)$') { Write-Host "Skipped $Destination"; return }
        if ($Backup) {
            $backupPath = "$Destination.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')-$([Guid]::NewGuid().ToString('N'))"
            Copy-Item -LiteralPath $Destination -Destination $backupPath -ErrorAction Stop
            Write-Host "Backup: $backupPath"
        }
    }

    $parent = Split-Path -Parent ([IO.Path]::GetFullPath($Destination))
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    Copy-Item -LiteralPath $Source -Destination $Destination -Force -ErrorAction Stop
    Write-Host "Copied to $Destination"
}

function Invoke-AgentsInstall {
    param([string[]]$Destination, [string]$Ref, [switch]$Backup, [switch]$NoBackup)

    if ($Backup -and $NoBackup) { throw 'Specify only one of -Backup or -NoBackup.' }

    if (-not $Destination) {
        Assert-InteractiveTerminal
        $targets = @(
            Join-Path $HOME '.claude/CLAUDE.md'
            Join-Path $HOME '.codex/AGENTS.md'
            Join-Path $HOME '.config/opencode/AGENTS.md'
        )
        $items = @(
            [pscustomobject]@{ Label = "Claude: $($targets[0])" }
            [pscustomobject]@{ Label = "Codex: $($targets[1])" }
            [pscustomobject]@{ Label = "OpenCode: $($targets[2])" }
            [pscustomobject]@{ Label = 'Custom path' }
        )
        $selection = @(Select-ArrowMenu -Title 'Install GitHub instructions (select one or more targets)' -Items $items -Multiple)
        if ($selection.Count -eq 0) { Write-Host 'Cancelled. No files changed.'; return }
        $Destination = @(foreach ($index in $selection) {
            if ($index -eq 3) { Read-Host 'Destination file (full path)' } else { $targets[$index] }
        })
    }

    foreach ($path in $Destination) {
        if ([string]::IsNullOrWhiteSpace($path)) { throw 'The destination cannot be empty.' }
    }

    $existingPaths = @(foreach ($path in $Destination) {
        $existing = Get-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
        if ($null -ne $existing) {
            if ($existing.PSIsContainer -or ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
                throw "Refusing to replace a directory or symbolic link: $path"
            }
            $path
        }
    })
    if ($existingPaths.Count -gt 0) {
        Write-Host 'Existing instruction files that will be backed up if replaced (when backup is selected):'
        foreach ($path in $existingPaths) { Write-Host "  $path" }
    } else {
        Write-Host 'No existing instruction files found at the selected destinations.'
    }
    $makeBackup = [bool]$Backup
    if (-not $Backup -and -not $NoBackup) {
        Assert-InteractiveTerminal
        $modes = @(
            [pscustomobject]@{ Label = 'Backup existing files before replacing' }
            [pscustomobject]@{ Label = 'Replace without backup' }
        )
        $mode = @(Select-ArrowMenu -Title 'Choose how to handle existing instruction files' -Items $modes)
        if ($mode.Count -eq 0) { Write-Host 'Cancelled. No files changed.'; return }
        $makeBackup = $mode[0] -eq 0
    }

    $source = [IO.Path]::GetTempFileName()
    $securityProtocol = [Net.ServicePointManager]::SecurityProtocol

    try {
        [Net.ServicePointManager]::SecurityProtocol = $securityProtocol -bor [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/lioqing/.agents/$Ref/AGENTS.md" -OutFile $source -TimeoutSec 120 -UseBasicParsing

        if ((Get-Item -LiteralPath $source).Length -eq 0) { throw 'Downloaded AGENTS.md is empty. No destinations changed.' }

        foreach ($path in $Destination) { Copy-Instructions -Source $source -Destination $path -Backup $makeBackup }
    } finally {
        [Net.ServicePointManager]::SecurityProtocol = $securityProtocol
        Remove-Item -LiteralPath $source -Force -ErrorAction SilentlyContinue
    }
}

Invoke-AgentsInstall -Destination @($Destination) -Ref $Ref -Backup:$Backup -NoBackup:$NoBackup
