# Personal agent configurations

My shared agent instructions (`AGENTS.md`) and reusable skills (`skills/`).

## Install skills

Requires Node.js/npm:

```sh
npx skills add lioqing/.agents
```

Choose skills and agents when prompted.

## Install agent instructions

No clone required. Installers download `AGENTS.md` from GitHub.
Review the scripts before running them.

PowerShell 5.0+:

```powershell
irm https://raw.githubusercontent.com/lioqing/.agents/master/scripts/install-agents.ps1 | iex
```

> [!NOTE]
> If Windows PowerShell reports "Could not create SSL/TLS secure channel,"
> enable TLS 1.2, then retry:
>
> ```powershell
> [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
> ```

Bash:

```bash
installer=$(curl -fsSL https://raw.githubusercontent.com/lioqing/.agents/master/scripts/install-agents.sh) && bash -c "$installer"
```

Use `bash -c`, not `curl | bash`, so prompts can read standard input.
The command runs only if the download succeeds.

From a clone or downloaded script:

```powershell
pwsh -File ./scripts/install-agents.ps1
```

```bash
bash ./scripts/install-agents.sh
```

- PowerShell: arrow-key multi-select.
- Bash: numbered menu with one agent, **All three**, **Custom path**, or **Cancel**.

Default destinations:

| Agent | Destination |
| --- | --- |
| Claude | `~/.claude/CLAUDE.md` |
| Codex | `~/.codex/AGENTS.md` |
| OpenCode | `~/.config/opencode/AGENTS.md` |

Skip the destination menu with a custom file:

```powershell
pwsh -File ./scripts/install-agents.ps1 -Destination /desired/path/AGENTS.md
```

```bash
bash ./scripts/install-agents.sh /desired/path/AGENTS.md
```

- A second menu lists existing files and asks whether to back them up.
- The choice applies to all destinations, including custom paths.
- PowerShell defaults to backup; Bash requires a number and Enter.
- Cancelling either menu changes nothing and downloads no instructions.

Skip the backup menu with these mutually exclusive options:

| Mode | PowerShell | Bash |
| --- | --- | --- |
| Back up | `-Backup` | `--backup` |
| No backup | `-NoBackup` | `--no-backup` |

Specify a destination too to skip both menus. Overwrite confirmation still applies:

```powershell
pwsh -File ./scripts/install-agents.ps1 -Destination /desired/path/AGENTS.md -Backup
```

```bash
bash ./scripts/install-agents.sh --backup /desired/path/AGENTS.md
```

- Bash accepts options before or after the destination; use `--` before paths starting with `-`.
- Instructions come from remote `master`, even when running from a clone.
- Override with `AGENTS_REF` (branch, tag, or commit) or PowerShell's `-Ref`.
- To pin both scripts and instructions, replace `master` in the URL and set `AGENTS_REF` to the same ref.

Safety:

- Missing parent directories are created; directories and symbolic links are never overwritten.
- Overwriting requires `y` or `yes`, regardless of backup mode; other answers skip that file.
- Backups use `<filename>.backup-<timestamp>-<unique suffix>` beside the original.
- Failed or empty downloads leave destinations unchanged; temporary downloads are cleaned up.

## Development: import local files

### Import installed skills

```powershell
pwsh -File ./scripts/import-skills.ps1
```

```bash
bash ./scripts/import-skills.sh
```

- Select skills containing `SKILL.md` from `~/.agents/skills` to import into `skills/`.
- Choose **Copy** (default, keeps originals) or **Move**. Cancelling changes nothing.
- Existing repo names are unavailable; nothing is overwritten.
- Copies include hidden files and resources, following symbolic links for self-contained copies.
- Move removes originals only after all copies succeed. Links and junctions are removed without deleting their targets.
- Failed copies keep all originals; failed removals may leave originals behind.

Review, commit, and push imports, then update installed skills:

```sh
npx skills add lioqing/.agents --global
```

The script displays this command but never runs it. Push first, then choose skills and agents when prompted.

### Import agent instructions

```powershell
pwsh -File ./scripts/import-agents.ps1
```

```bash
bash ./scripts/import-agents.sh
```

- Choose one Claude, Codex, or OpenCode file to copy into the repo's `AGENTS.md`.
- Missing sources are unavailable.
- Replacing an existing repo file requires confirmation and creates a backup.
- Files are copied verbatim, not merged.

## Menu controls and requirements

Import scripts and the PowerShell installer use arrow-key menus:

| Key | Action |
| --- | --- |
| Up/Down | Navigate; menus page after ten rows |
| Space | Toggle multi-select choices |
| Enter | Confirm; multi-select needs at least one choice |
| Esc or q | Cancel |

`[-]` means unavailable; `[x]` means selected.
Bash imports also accept **j/k**; on Bash 3.2, **Esc** may take one second, while **q** is immediate.

The Bash installer uses numbers followed by Enter; choose **Cancel** or enter **q** to quit.

- PowerShell: **5.0+**; replace `pwsh` with `powershell` on Windows PowerShell 5.x.
- Bash: **3.2+**, `cp`, `mkdir`, `rm`, and `date` (macOS, Linux, WSL, or Git Bash).
  Installation also needs `curl` and `mktemp`.
- Arrow-key menus need an interactive ANSI terminal with no redirected input/output, including custom-path installs without a backup option. Recommended size: 80 × 15.
- No external menu package is needed.
- Paths use the current user's home (Linux home under WSL). Import scripts find the repo from their own location.
- Scripts never install skills or commit automatically; only **Move** deletes originals.
- Failed copies may leave partial destinations. Inspect before retrying; review imports and backups before committing.

## Tests

Tests use temporary homes and repo copies; personal files are untouched:

```powershell
pwsh -File ./tests/test-scripts.ps1
```

```bash
python3 ./tests/test_bash.py
```

- PowerShell tests mock keyboard input; Bash tests run menus in a pseudo-terminal.
- Downloads are mocked; no GitHub access is needed.
- Bash tests require macOS/Linux/WSL and Python 3.
