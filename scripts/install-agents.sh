#!/usr/bin/env bash
set -eo pipefail

die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

copy_instructions() {
    local source=$1 destination=$2 make_backup=$3 backup answer
    if [[ -e $destination || -L $destination ]]; then
        [[ -f $destination && ! -L $destination ]] ||
            die "Refusing to replace a directory or symbolic link: $destination"

        printf 'Replace %s? [y/N] ' "$destination"
        IFS= read -r answer || answer=''
        case "$answer" in y|Y|[yY][eE][sS]) ;; *) printf 'Skipped %s\n' "$destination"; return 0;; esac

        if [[ $make_backup == 1 ]]; then
            backup=$(mktemp "${destination}.backup-$(date +%Y%m%d-%H%M%S)-XXXXXXXX")
            cp -p "$destination" "$backup"
            printf 'Backup: %s\n' "$backup"
        fi
    fi

    mkdir -p "$(dirname "$destination")"
    cp "$source" "$destination"
    printf 'Copied to %s\n' "$destination"
}

main() {
    local ref=${AGENTS_REF:-master} choice destination temp_dir make_backup=''
    local targets=("$HOME/.claude/CLAUDE.md" "$HOME/.codex/AGENTS.md" "$HOME/.config/opencode/AGENTS.md")
    local selected=()
    local existing=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --backup)
                [[ $make_backup != 0 ]] || die 'Specify only one of --backup or --no-backup.'
                make_backup=1;;
            --no-backup)
                [[ $make_backup != 1 ]] || die 'Specify only one of --backup or --no-backup.'
                make_backup=0;;
            --) shift; selected+=("$@"); break;;
            -*) die "Unknown option: $1";;
            *) selected+=("$1");;
        esac
        shift
    done
    [[ ${#selected[@]} -le 1 ]] || die 'Usage: install-agents.sh [--backup | --no-backup] [--] [destination-file]'

    if [[ ${#selected[@]} == 1 ]]; then
        [[ -n ${selected[0]} ]] || die 'The destination cannot be empty.'
    else
        printf 'Install GitHub instructions. Choose a destination by number.\n'
        # select/read use stdin. For remote execution use bash -c "$(curl ...)",
        # not curl | bash, so stdin remains available without /dev/tty.
        PS3='Destination: '
        select choice in "Claude: ${targets[0]}" "Codex: ${targets[1]}" \
            "OpenCode: ${targets[2]}" 'All three' 'Custom path' 'Cancel'; do
            case "$REPLY" in
                1|2|3) selected=("${targets[REPLY-1]}"); break;;
                4) selected=("${targets[@]}"); break;;
                5)
                    printf 'Destination file (full path): '
                    IFS= read -r destination || destination=''
                    [[ -n $destination ]] || { printf 'Cancelled. No files changed.\n'; return 0; }
                    selected=("$destination"); break;;
                6|q|Q) printf 'Cancelled. No files changed.\n'; return 0;;
                *) printf 'Enter a number from 1 to 6 (or q to cancel).\n';;
            esac
        done
        if [[ ${#selected[@]} == 0 ]]; then
            printf 'Cancelled. No files changed.\n'; return 0
        fi
    fi

    for destination in "${selected[@]}"; do
        if [[ -e $destination || -L $destination ]]; then
            [[ -f $destination && ! -L $destination ]] ||
                die "Refusing to replace a directory or symbolic link: $destination"
            existing+=("$destination")
        fi
    done
    if [[ ${#existing[@]} -gt 0 ]]; then
        printf 'Existing instruction files that will be backed up if replaced (when backup is selected):\n'
        printf '  %s\n' "${existing[@]}"
    else
        printf 'No existing instruction files found at the selected destinations.\n'
    fi
    if [[ -z $make_backup ]]; then
        PS3='Backup mode: '
        select choice in 'Backup existing files before replacing' 'Replace without backup' 'Cancel'; do
            case "$REPLY" in
                1) make_backup=1; break;;
                2) make_backup=0; break;;
                3|q|Q) printf 'Cancelled. No files changed.\n'; return 0;;
                *) printf 'Enter a number from 1 to 3 (or q to cancel).\n';;
            esac
        done
        if [[ -z $make_backup ]]; then
            printf 'Cancelled. No files changed.\n'; return 0
        fi
    fi

    command -v curl >/dev/null 2>&1 || die 'curl is required to download AGENTS.md.'
    temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/install-agents.XXXXXXXX")
    # EXIT runs after main has returned, so keep the private path outside its scope.
    INSTALL_AGENTS_TEMP_DIR=$temp_dir
    trap 'rm -f -- "$INSTALL_AGENTS_TEMP_DIR/AGENTS.md"; rmdir -- "$INSTALL_AGENTS_TEMP_DIR"' EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    curl -fsSL --connect-timeout 10 --max-time 120 \
        "https://raw.githubusercontent.com/lioqing/.agents/$ref/AGENTS.md" \
        -o "$temp_dir/AGENTS.md" || die 'Unable to download AGENTS.md. No destinations changed.'
    [[ -s $temp_dir/AGENTS.md ]] || die 'Downloaded AGENTS.md is empty. No destinations changed.'

    for destination in "${selected[@]}"; do
        copy_instructions "$temp_dir/AGENTS.md" "$destination" "$make_backup"
    done
}

main "$@"
