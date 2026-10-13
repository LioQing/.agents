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

    destination="$REPO_ROOT/skills/$name"
    if [[ -L $destination || ( -e $destination && ! -d $destination ) ]]; then
        MENU_LABELS+=("$name (unavailable: destination is a file or link)")
        MENU_ENABLED+=(0)
    elif [[ -d $destination ]]; then
        MENU_LABELS+=("$name (already exists in repo: replacement requires confirmation)")
        MENU_ENABLED+=(1)
    else
        MENU_LABELS+=("$name"); MENU_ENABLED+=(1)
    fi
done
((${#paths[@]} > 0)) || die "No skill directories containing SKILL.md found in $source_dir"

if ! select_menu 'Import installed skills into this repository' 1; then
    printf 'Cancelled. No files changed.\n'; exit 0
fi
selection=("${MENU_RESULT[@]}")

printf 'Move removes the selected originals after all copies succeed. Links are removed, not their targets.\n'
MENU_LABELS=('Copy (keep originals)' 'Move (remove originals after copying)')
MENU_ENABLED=(1 1)
if ! select_menu 'Choose how to import selected skills' 0; then
    printf 'Cancelled. No files changed.\n'; exit 0
fi
move=${MENU_RESULT[0]}

accepted=(); replacing=()
for index in "${selection[@]}"; do
    destination="$REPO_ROOT/skills/${names[index]}"
    replacing[index]=0
    if [[ -e $destination || -L $destination ]]; then
        [[ -d $destination && ! -L $destination ]] || die "Refusing to replace a file or symbolic link: $destination"
        printf 'Replace %s? [y/N] ' "$destination"
        IFS= read -r answer || answer=''
        case "$answer" in y|Y|yes|YES) ;; *) printf 'Skipped %s\n' "$destination"; continue;; esac
        replacing[index]=1
    fi
    accepted+=("$index")
done
((${#accepted[@]} > 0)) || exit 0

mkdir -p "$REPO_ROOT/skills"
staging=$(mktemp -d "$REPO_ROOT/skills/.import-XXXXXXXX")
trap 'rm -rf -- "$staging"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Stage every copy first: installed links may target skills being replaced.
for index in "${accepted[@]}"; do
    mkdir "$staging/${names[index]}"
    cp -RL "${paths[index]}/." "$staging/${names[index]}/"
done

for index in "${accepted[@]}"; do
    destination="$REPO_ROOT/skills/${names[index]}"
    if [[ -e $destination || -L $destination ]]; then
        [[ ${replacing[index]} == 1 && -d $destination && ! -L $destination ]] ||
            die "Destination changed while importing: $destination"
        backup="${destination}.backup-$(date +%Y%m%d-%H%M%S)-$$"
        [[ ! -e $backup && ! -L $backup ]] || die "Backup already exists: $backup"
        mv -- "$destination" "$backup"
        printf 'Backup: %s\n' "$backup"
    fi
    mv -- "$staging/${names[index]}" "$destination"
    printf 'Imported %s\n' "${names[index]}"
done

# Remove only successfully imported selections, never declined replacements.
if [[ $move == 1 ]]; then
    for index in "${accepted[@]}"; do
        # No trailing slash; rm does not follow directory symlinks.
        rm -rf -- "${paths[index]}"
        printf 'Removed original %s\n' "${paths[index]}"
    done
fi

printf '\nReview, commit and push the imported skills, then reinstall/update your home-directory skills:\n'
printf '  npx skills add lioqing/.agents --global\n'
