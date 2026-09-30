#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd -P)
source "$SCRIPT_DIR/common.sh"

require_terminal

source_dir="$HOME/.agents/skills"
[[ -d $source_dir ]] || die "Skills directory not found: $source_dir"

paths=(); names=(); MENU_LABELS=(); MENU_ENABLED=()
shopt -s nullglob dotglob
for skill in "$source_dir/"*/; do
    [[ -f "${skill}SKILL.md" ]] || continue
    skill=${skill%/}; name=${skill##*/}
    paths+=("$skill"); names+=("$name")

    if [[ -e "$REPO_ROOT/skills/$name" || -L "$REPO_ROOT/skills/$name" ]]; then
        MENU_LABELS+=("$name (unavailable: name already exists in repo)")
        MENU_ENABLED+=(0)
    else
        MENU_LABELS+=("$name"); MENU_ENABLED+=(1)
    fi
done
((${#paths[@]} > 0)) || die "No skill directories containing SKILL.md found in $source_dir"

if ! select_menu 'Import installed skills into this repository' 1; then
    printf 'Cancelled. No files changed.\n'; exit 0
fi

mkdir -p "$REPO_ROOT/skills"
for index in "${MENU_RESULT[@]}"; do
    destination="$REPO_ROOT/skills/${names[index]}"

    # Check again in case the repo changed while the menu was open.
    [[ ! -e $destination && ! -L $destination ]] || die "Destination now exists: $destination"
    mkdir "$destination"

    # Dereference installed skill links to make a self-contained copy.
    cp -RL "${paths[index]}/." "$destination/"
    printf 'Imported %s\n' "${names[index]}"
done
