# Personal agent configurations

Shared instructions (`AGENTS.md`) and skills (`skills/`). No clone needed to install.

## Install instructions and skills together

Requires Node.js/npm (`npx`), PowerShell 5.0+ or Bash 3.2+, and an interactive ANSI terminal. Bash also needs `curl`.

PowerShell:

```powershell
irm https://raw.githubusercontent.com/lioqing/.agents/master/scripts/install.ps1 | iex
```

Bash:

```bash
installer=$(curl -fsSL https://raw.githubusercontent.com/lioqing/.agents/master/scripts/install.sh) && bash -c "$installer"
```

From a clone:

```powershell
pwsh -File ./scripts/install.ps1
```

```bash
bash ./scripts/install.sh
```

1. Select agents: Claude, Codex, and OpenCode (all selected by default).
2. Select personal and external skills (all selected by default).
3. Choose instruction backups (default) or no backups.
4. Enter `y` or `yes` for each instruction overwrite; other answers skip it. Selected skills still install globally.

Cancel any menu to install nothing. See menu controls below.

## Personal skills

| Skill | Description | Notes |
| --- | --- | --- |
| [blender-workflow](skills/blender-workflow/SKILL.md) | Creates and revises Blender scenes through Blender MCP, with organized collections, rendered previews, and versioned saves. | |
| [guided-learning](skills/guided-learning/SKILL.md) | Teaches complex technical topics through interactive, step-by-step walkthroughs when you ask for a full lesson. | |
| [html-report](skills/html-report/SKILL.md) | Builds single-page HTML reports with charts, diagrams, tables, light/dark mode, and section navigation. | |
| [markdown-slides](skills/markdown-slides/SKILL.md) | Turns Markdown into HTML slide presentations with per-slide customization and edit-preserving rebuilds. | |
| [markdown-slides-prep](skills/markdown-slides-prep/SKILL.md) | Organizes conversations, notes, outlines, or documents into reviewable Markdown slide sources for markdown-slides. | Requires `markdown-slides`. |

## External skills

| Skill | Source | Description |
| --- | --- | --- |
| no-ai-slop | [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) | Edits drafts for clearer, more natural writing while preserving the author's voice, or checks for AI-like writing patterns. |
| caveman | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Compresses responses to reduce token usage while preserving technical accuracy. |
| grilling | [mattpocock/skills](https://github.com/mattpocock/skills) | Stress-tests plans and ideas with questions about assumptions and gaps. |

Install individually:

```sh
npx skills add petergyang/no-ai-slop --skill no-ai-slop --global --yes --agent claude-code codex opencode
npx skills add JuliusBrussee/caveman --skill caveman --global --yes --agent claude-code codex opencode
npx skills add mattpocock/skills --skill grilling --global --yes --agent claude-code codex opencode
```

Remove unwanted agent names to install for fewer targets.

## Install skills

Requires Node.js/npm (`npx`):

```sh
npx skills add lioqing/.agents
```

Choose skills and agents when prompted.

## Install agent instructions

Requires PowerShell 5.0+ or Bash 3.2+ with `curl`. Instructions download from GitHub.

PowerShell:

```powershell
irm https://raw.githubusercontent.com/lioqing/.agents/master/scripts/install-agents.ps1 | iex
```

Bash:

```bash
installer=$(curl -fsSL https://raw.githubusercontent.com/lioqing/.agents/master/scripts/install-agents.sh) && bash -c "$installer"
```

From a clone:

```powershell
pwsh -File ./scripts/install-agents.ps1
```

```bash
bash ./scripts/install-agents.sh
```

1. Select destinations: PowerShell uses multi-select; Bash offers one agent, **All three**, or **Custom path**.
2. Choose backups or no backups (PowerShell defaults to backups).
3. Enter `y` or `yes` for each overwrite; other answers skip that file. Cancelling a menu changes nothing.

Default destinations:

| Agent | Destination |
| --- | --- |
| Claude | `~/.claude/CLAUDE.md` |
| Codex | `~/.codex/AGENTS.md` |
| OpenCode | `~/.config/opencode/AGENTS.md` |

Backup options (choose one):

| Mode | PowerShell | Bash |
| --- | --- | --- |
| Back up | `-Backup` | `--backup` |
| No backup | `-NoBackup` | `--no-backup` |

Skip both menus with a custom destination and backup option; overwrites still need confirmation:

```powershell
pwsh -File ./scripts/install-agents.ps1 -Destination /desired/path/AGENTS.md -Backup
```

```bash
bash ./scripts/install-agents.sh --backup /desired/path/AGENTS.md
```

## Development: import local files

Requires a clone. See shell and terminal requirements below.

### Import installed skills

```powershell
pwsh -File ./scripts/import-skills.ps1
```

```bash
bash ./scripts/import-skills.sh
```

1. Select skills from `~/.agents/skills` to import into `skills/`.
2. Choose **Copy** (default, keeps originals) or **Move** (removes originals after successful imports).
3. Enter `y` or `yes` to replace an existing skill with a backup; other answers skip it. Cancel either menu to change nothing.

Review, commit, and push imports, then update installed skills:

```sh
npx skills add lioqing/.agents --global
```

### Import agent instructions

```powershell
pwsh -File ./scripts/import-agents.ps1
```

```bash
bash ./scripts/import-agents.sh
```

1. Choose one available Claude, Codex, or OpenCode file to copy into the repo's `AGENTS.md`.
2. Confirm replacement to back up and overwrite the existing file.

## Menu controls and requirements

Import scripts, combined installers, and the PowerShell instruction installer:

| Key | Action |
| --- | --- |
| Up/Down | Navigate; menus page after ten rows |
| Space | Toggle multi-select choices |
| Enter | Confirm; multi-select needs at least one choice |
| Esc or q | Cancel |

`[-]` means unavailable; `[x]` means selected. Bash imports also accept **j/k**.

The Bash instruction-only installer uses numbers, then Enter; choose **Cancel** or enter **q** to quit.

- PowerShell: **5.0+**; replace `pwsh` with `powershell` on Windows PowerShell 5.x.
- Bash: **3.2+**, `cp`, `mkdir`, `mv`, `rm`, `mktemp`, and `date` (macOS, Linux, WSL, or Git Bash); installers also need `curl`.
- Arrow-key menus: interactive ANSI terminal, no redirected input/output. Recommended size: 80 × 15.
- Skill installation: Node.js/npm (`npx`).

## Tests

Requires PowerShell 5.0+, or Python 3 on macOS/Linux/WSL for Bash tests.

```powershell
pwsh -File ./tests/test-scripts.ps1
pwsh -File ./tests/test-install.ps1
```

```bash
python3 ./tests/test_bash.py
```
