# Personal agent files

My shared agent instructions (`AGENTS.md`) and reusable skills (`skills/`).

## Install skills

Requires Node.js/npm. Run:

```sh
npx skills add lioqing/.agents
```

Follow the CLI prompts to choose skills and agents.

## Install agent instructions

No clone is required. Both installers are standalone and download this
repository's `AGENTS.md` from GitHub. Review the scripts before executing them.

PowerShell 5.0+ (including Windows PowerShell 5.1):

```powershell
irm https://raw.githubusercontent.com/lioqing/.agents/master/scripts/install-agents.ps1 | iex
```

> [!NOTE]
> On older Windows PowerShell configurations, the download may fail with
> "Could not create SSL/TLS secure channel." Enable TLS 1.2 in the current
> PowerShell session, then retry:
>
> ```powershell
> [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
> ```

Bash:

```bash
installer=$(curl -fsSL https://raw.githubusercontent.com/lioqing/.agents/master/scripts/install-agents.sh) && bash -c "$installer"
```

Use `bash -c`, **not** `curl | bash`: Bash's built-in `select` and overwrite
prompts read standard input. The command above leaves it available without
requiring `/dev/tty`, and only executes the installer if its download succeeds.

Alternatively, download the installer first or run it from a clone:

```powershell
pwsh -File ./scripts/install-agents.ps1
```

```bash
bash ./scripts/install-agents.sh
```

PowerShell keeps the arrow-key multi-select menu. Bash uses a numbered `select`
prompt: choose one agent, **All three**, **Custom path**, or **Cancel**.
The default destinations are:

| Agent | Destination |
| --- | --- |
| Claude | `~/.claude/CLAUDE.md` |
| Codex | `~/.codex/AGENTS.md` |
| OpenCode | `~/.config/opencode/AGENTS.md` |

To bypass the destination menu and specify a file yourself:

```powershell
pwsh -File ./scripts/install-agents.ps1 -Destination /desired/path/AGENTS.md
```

```bash
bash ./scripts/install-agents.sh /desired/path/AGENTS.md
```

Installers fetch `AGENTS.md` from `master` by default. Set `AGENTS_REF` to a
branch, tag, or commit SHA to override it (PowerShell also accepts `-Ref`).
For a pinned remote installation, replace `master` in the installer URL with
the same ref and set `AGENTS_REF` so the instructions are pinned too.
Running from a clone still downloads the remote file, not the local copy.

Missing parent directories are created. Existing files require confirmation
and are backed up beside the original as `<filename>.backup-<timestamp>-<unique suffix>`.
Answering anything other than `y` or `yes` skips that destination. Directories
and symbolic links are not overwritten. Downloads are stored in a temporary
file and cleaned up afterward. A failed or empty download changes no destinations.

## Development: bring local files into this repo

### Import installed skills

```powershell
pwsh -File ./scripts/import-skills.ps1
```

```bash
bash ./scripts/import-skills.sh
```

The menu lists skill directories in `~/.agents/skills` containing `SKILL.md`.
Select multiple skills to copy into this repository's `skills/` folder.
Names already present in the repo are marked **unavailable** and cannot be
selected, even if the existing entry is not a directory. Nothing is overwritten.
The entire skill directory is copied, including hidden files and supporting
resources. Installed symbolic links are followed so the imported skill is a
self-contained copy, not a link back into your home directory.

### Import agent instructions

```powershell
pwsh -File ./scripts/import-agents.ps1
```

```bash
bash ./scripts/import-agents.sh
```

Choose **one** of the Claude, Codex, or OpenCode files listed above to copy
into this repository's `AGENTS.md`. Missing sources are marked unavailable.
An existing repo file requires confirmation and receives a backup first.
Files are copied verbatim; instructions are not merged.

## Menu controls and requirements

These arrow-key controls apply to the import scripts and the PowerShell installer.
The Bash installer instead accepts the displayed number followed by Enter;
choose **Cancel** or enter **q** to cancel.

- **Up/Down**: move between choices (menus page automatically after ten rows).
- **Space**: toggle a choice in multi-select menus.
- **Enter**: confirm selected choices, or choose the highlighted single source.
- **Esc** or **q**: cancel without copying. Multi-select menus need at least one selection.
- `[-]` means unavailable; `[x]` means selected.

PowerShell scripts require **PowerShell 5.0+**. For Windows PowerShell 5.x,
replace `pwsh` with `powershell` in the commands above and below.
Bash scripts require **Bash 3.2+** and standard `cp`, `mkdir`, and `date` utilities
(macOS, Linux, WSL, or Git Bash). The Bash installer additionally requires
`curl` and `mktemp`. Neither version needs an external menu package. Arrow-key
menus require an interactive ANSI-capable terminal, not redirected input/output.
A terminal at least 80 columns wide and 15 rows tall is recommended.
Bash import menus also accept **j/k** for down/up.
On Bash 3.2, cancelling with **Esc** may take one second; **q** is immediate.

Default destinations use the current user's home directory. Under WSL that is
the Linux home, not the Windows home. Import scripts resolve the repository from
their own location; installers do not require a repository checkout. They do
not automatically install skills, commit changes, or delete user files.
A failed copy can leave a partial destination; inspect it before
retrying. Review imported files and backup files before committing.

## Tests

Tests use temporary homes and repository copies, leaving personal files alone:

```powershell
pwsh -File ./tests/test-scripts.ps1
```

```bash
python3 ./tests/test_bash.py
```

The PowerShell tests mock keyboard input; the Bash tests exercise the actual
menus in a pseudo-terminal. Installer downloads are mocked, so tests require
no GitHub access. Bash tests require macOS/Linux/WSL and Python 3.
