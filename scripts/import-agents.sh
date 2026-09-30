#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd -P)
source "$SCRIPT_DIR/common.sh"

require_terminal

paths=("$HOME/.claude/CLAUDE.md" "$HOME/.codex/AGENTS.md" "$HOME/.config/opencode/AGENTS.md")
labels=(Claude Codex OpenCode)
MENU_LABELS=(); MENU_ENABLED=()
for ((i=0; i<${#paths[@]}; i++)); do
    if [[ -f ${paths[i]} ]]; then
        MENU_LABELS+=("${labels[i]}: ${paths[i]}"); MENU_ENABLED+=(1)
    else
        MENU_LABELS+=("${labels[i]} (unavailable: file missing): ${paths[i]}"); MENU_ENABLED+=(0)
    fi
done

if ! select_menu 'Choose one instruction file to copy into the repository' 0; then
    printf 'Cancelled. No files changed.\n'; exit 0
fi

copy_instructions "${paths[MENU_RESULT[0]]}" "$REPO_ROOT/AGENTS.md"
