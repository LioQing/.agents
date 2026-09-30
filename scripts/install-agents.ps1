#Requires -Version 5.0

param(
    [string[]]$Destination = @(),
    [string]$Ref = $(if ($env:AGENTS_REF) { $env:AGENTS_REF } else { 'master' })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-InteractiveTerminal {
    if ([Console]::IsInputRedirected -or [Console]::IsOutputRedirected -or $env:TERM -eq 'dumb') {
        throw 'Run this script in an interactive terminal with ANSI support, or specify -Destination.'
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
            [Console]::WriteLine('Up/Down: move | Space: toggle | Enter: confirm | Esc/q: cancel')
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
                Spacebar { $selected[$cursor] = -not $selected[$cursor] }
                Enter {
                    $result = @(for ($i = 0; $i -lt $Items.Count; $i++) { if ($selected[$i]) { $i } })
                    if ($result.Count -gt 0) { return $result }
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
    param([string]$Source, [string]$Destination)

    # Get-Item also detects dangling links, which must not be overwritten.
    $existing = Get-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
    if ($null -ne $existing) {
        if ($existing.PSIsContainer -or ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Refusing to replace a directory or symbolic link: $Destination"
        }
        $answer = Read-Host "Replace ${Destination}? [y/N]"
        if ($answer -notmatch '^(y|yes)$') { Write-Host "Skipped $Destination"; return }
        $backup = "$Destination.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')-$([Guid]::NewGuid().ToString('N'))"
        Copy-Item -LiteralPath $Destination -Destination $backup -ErrorAction Stop
        Write-Host "Backup: $backup"
    }

    $parent = Split-Path -Parent ([IO.Path]::GetFullPath($Destination))
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    Copy-Item -LiteralPath $Source -Destination $Destination -Force -ErrorAction Stop
    Write-Host "Copied to $Destination"
}

function Invoke-AgentsInstall {
    param([string[]]$Destination, [string]$Ref)

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

    $source = [IO.Path]::GetTempFileName()
    $securityProtocol = [Net.ServicePointManager]::SecurityProtocol

    try {
        [Net.ServicePointManager]::SecurityProtocol = $securityProtocol -bor [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/lioqing/.agents/$Ref/AGENTS.md" -OutFile $source -TimeoutSec 120 -UseBasicParsing

        if ((Get-Item -LiteralPath $source).Length -eq 0) { throw 'Downloaded AGENTS.md is empty. No destinations changed.' }

        foreach ($path in $Destination) { Copy-Instructions -Source $source -Destination $path }
    } finally {
        [Net.ServicePointManager]::SecurityProtocol = $securityProtocol
        Remove-Item -LiteralPath $source -Force -ErrorAction SilentlyContinue
    }
}

Invoke-AgentsInstall -Destination @($Destination) -Ref $Ref
