# Shared by the entry points; not intended to be run directly.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-InteractiveTerminal {
    if ([Console]::IsInputRedirected -or [Console]::IsOutputRedirected -or $env:TERM -eq 'dumb') {
        throw 'Run this script in an interactive terminal with ANSI support.'
    }
}

function Read-MenuKey { [Console]::ReadKey($true) }

function Select-ArrowMenu {
    param(
        [Parameter(Mandatory)][string]$Title,
        [Parameter(Mandatory)][object[]]$Items,
        [switch]$Multiple
    )

    # Each item has Label and Enabled properties. Return zero-based indexes.
    if (@($Items | Where-Object { $_.Enabled }).Count -eq 0) {
        Write-Host $Title
        foreach ($item in $Items) { Write-Host "  $($item.Label)" }
        Write-Host 'No available choices.'
        return
    }

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

            $start = [int]([Math]::Floor($cursor / 10) * 10)
            $end = [Math]::Min($start + 10, $Items.Count)
            for ($i = $start; $i -lt $end; $i++) {
                $pointer = ' '; if ($i -eq $cursor) { $pointer = '>' }
                $mark = ' '; if ($selected[$i]) { $mark = 'x' }
                if (-not $Items[$i].Enabled) { $mark = '-' }

                $line = "$pointer [$mark] $($Items[$i].Label)"
                if ($line.Length -ge $width) { $line = $line.Substring(0, $width - 1) }
                [Console]::WriteLine($line)
            }
            [Console]::WriteLine("Choices $($start + 1)-$end of $($Items.Count)")
            $rows = $end - $start + 3

            $key = Read-MenuKey
            switch ($key.Key) {
                UpArrow { $cursor = ($cursor + $Items.Count - 1) % $Items.Count }
                DownArrow { $cursor = ($cursor + 1) % $Items.Count }
                Spacebar {
                    if ($Multiple -and $Items[$cursor].Enabled) { $selected[$cursor] = -not $selected[$cursor] }
                }
                Enter {
                    if ($Multiple) {
                        $result = @(for ($i = 0; $i -lt $Items.Count; $i++) { if ($selected[$i]) { $i } })
                        if ($result.Count -gt 0) { return $result }
                    } elseif ($Items[$cursor].Enabled) { return $cursor }
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
    param([Parameter(Mandatory)][string]$Source, [Parameter(Mandatory)][string]$Destination)

    if (Test-Path -LiteralPath $Destination) {
        $existing = Get-Item -LiteralPath $Destination -Force
        if ($existing.PSIsContainer -or ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Refusing to replace a directory or symbolic link: $Destination"
        }

        $answer = Read-Host "Replace ${Destination}? [y/N]"
        if ($answer -notmatch '^(y|yes)$') { Write-Host "Skipped $Destination"; return }

        $backup = "$Destination.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')-$([Guid]::NewGuid().ToString('N').Substring(0, 8))"
        Copy-Item -LiteralPath $Destination -Destination $backup -ErrorAction Stop
        Write-Host "Backup: $backup"
    }

    $parent = Split-Path -Parent $Destination
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }

    Copy-Item -LiteralPath $Source -Destination $Destination -Force -ErrorAction Stop
    Write-Host "Copied to $Destination"
}

function Get-InstructionSources {
    @(
        [pscustomobject]@{ Name = 'Claude'; Path = Join-Path $HOME '.claude/CLAUDE.md' }
        [pscustomobject]@{ Name = 'Codex'; Path = Join-Path $HOME '.codex/AGENTS.md' }
        [pscustomobject]@{ Name = 'OpenCode'; Path = Join-Path $HOME '.config/opencode/AGENTS.md' }
    )
}

function Resolve-SkillPath {
    param([string]$Path)

    $seen = @()
    $entry = Get-Item -LiteralPath $Path -Force

    while ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        if ($entry.FullName -in $seen) { throw "Circular skill link: $Path" }
        $seen += $entry.FullName

        # The filesystem provider exposes Target on Windows PowerShell 5 too.
        $targets = @($entry.Target)
        if ($targets.Count -ne 1 -or [string]::IsNullOrWhiteSpace($targets[0])) {
            throw "Unable to resolve skill link: $Path"
        }

        $target = $targets[0]
        if (-not [IO.Path]::IsPathRooted($target)) {
            $target = Join-Path (Split-Path -Parent $entry.FullName) $target
        }

        $entry = Get-Item -LiteralPath $target -Force
    }

    $entry.FullName
}

function Copy-SkillTree {
    param([string]$Source, [string]$Destination, [string[]]$Ancestors = @())

    # Follow directory links rather than committing links back into a user's home.
    $resolved = Resolve-SkillPath -Path $Source
    if ($resolved -in $Ancestors) { throw "Circular skill directory link: $Source" }

    if (-not (Test-Path -LiteralPath $Destination)) {
        New-Item -ItemType Directory -Path $Destination | Out-Null
    }

    foreach ($child in Get-ChildItem -LiteralPath $resolved -Force) {
        $targetPath = Join-Path $Destination $child.Name
        if ($child.PSIsContainer) {
            Copy-SkillTree -Source $child.FullName -Destination $targetPath -Ancestors (@($Ancestors) + $resolved)
        } else {
            $fileSource = $child.FullName
            if ($child.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                $fileSource = Resolve-SkillPath -Path $fileSource
            }

            Copy-Item -LiteralPath $fileSource -Destination $targetPath -ErrorAction Stop
        }
    }
}

function Remove-SkillTree {
    param([Parameter(Mandatory)][string]$Path)

    $entry = Get-Item -LiteralPath $Path -Force
    if ($entry.PSIsContainer) {
        # Never recurse through a symbolic link or junction, including on PS 5.
        if (-not ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            foreach ($child in Get-ChildItem -LiteralPath $Path -Force) {
                Remove-SkillTree -Path $child.FullName
            }
        }
        [IO.Directory]::Delete($Path)
    } else {
        Remove-Item -LiteralPath $Path -Force
    }
}
