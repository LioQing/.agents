#!/usr/bin/env bash
# Shared by the entry points; not intended to be run directly.

die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

require_terminal() {
    [[ -t 0 && -t 1 && ${TERM:-dumb} != dumb ]] ||
        die 'Run this script in an interactive terminal with ANSI support.'
}

# Inputs: MENU_LABELS and MENU_ENABLED (1 = selectable, 0 = unavailable).
# Output: MENU_RESULT, containing selected zero-based indexes.
# Returns 1 on cancellation. Bash 3.2 compatible; no external menu package.
select_menu() {
    local title=$1 multiple=$2 count=${#MENU_LABELS[@]}
    local cursor=0 i start end rows=0 key suffix mark pointer line
    local width=${COLUMNS:-80} selected=() available=0 key_timeout=0.1

    # Bash 3.2 only accepts integer read timeouts.
    if ((BASH_VERSINFO[0] < 4)); then key_timeout=1; fi

    MENU_RESULT=()
    for ((i=0; i<count; i++)); do
        selected[i]=0
        [[ ${MENU_ENABLED[i]} == 1 ]] && available=$((available + 1))
    done

    if ((available == 0)); then
        printf '%s\n' "$title"
        for ((i=0; i<count; i++)); do printf '  %s\n' "${MENU_LABELS[i]}"; done
        printf 'No available choices.\n'
        return 1
    fi

    ((width >= 20)) || width=80
    printf '\033[?25l'

    # Always restore cursor visibility, including Ctrl+C or termination.
    trap 'printf "\033[?25h"' EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM

    while :; do
        if ((rows > 0)); then printf '\033[%dA\r\033[J' "$rows"; fi
        printf '%s\n' "$title"
        if [[ $multiple == 1 ]]; then
            printf 'Up/Down: move | Space: toggle | Enter: confirm | Esc/q: cancel\n'
        else
            printf 'Up/Down: move | Enter: choose | Esc/q: cancel\n'
        fi

        start=$((cursor / 10 * 10)); end=$((start + 10))
        ((end <= count)) || end=$count
        for ((i=start; i<end; i++)); do
            pointer=' '; [[ $i == "$cursor" ]] && pointer='>'
            mark=' '; [[ ${selected[i]} == 1 ]] && mark=x
            if [[ ${MENU_ENABLED[i]} == 0 ]]; then mark=-; fi

            line="$pointer [$mark] ${MENU_LABELS[i]}"
            printf '%s\n' "${line:0:width-1}"
        done
        printf 'Choices %d-%d of %d\n' "$((start + 1))" "$end" "$count"
        rows=$((end - start + 3))

        key=''
        if ! IFS= read -rsn1 key; then
            printf '\033[?25h'; trap - EXIT INT TERM; return 1
        fi

        case "$key" in
            $'\033')
                suffix=''
                if IFS= read -rsn1 -t "$key_timeout" suffix; then
                    if [[ $suffix == '[' || $suffix == O ]]; then
                        key=''; IFS= read -rsn1 -t "$key_timeout" key || true
                        case "$key" in
                            A) cursor=$(((cursor + count - 1) % count));;
                            B) cursor=$(((cursor + 1) % count));;
                        esac
                    fi
                else
                    printf '\033[?25h'; trap - EXIT INT TERM; return 1
                fi
                ;;
            k) cursor=$(((cursor + count - 1) % count));;
            j) cursor=$(((cursor + 1) % count));;
            ' ')
                if [[ $multiple == 1 && ${MENU_ENABLED[cursor]} == 1 ]]; then
                    selected[cursor]=$((1 - selected[cursor]))
                fi
                ;;
            ''|$'\r')
                if [[ $multiple == 0 ]]; then
                    [[ ${MENU_ENABLED[cursor]} == 1 ]] || continue
                    MENU_RESULT=("$cursor")
                else
                    MENU_RESULT=()
                    for ((i=0; i<count; i++)); do
                        [[ ${selected[i]} == 1 ]] && MENU_RESULT+=("$i")
                    done
                    ((${#MENU_RESULT[@]} > 0)) || continue
                fi

                printf '\033[?25h'; trap - EXIT INT TERM; return 0
                ;;
            q|Q) printf '\033[?25h'; trap - EXIT INT TERM; return 1;;
        esac
    done
}

# Confirm each overwrite separately. Back up existing files before replacing.
copy_instructions() {
    local source=$1 destination=$2 backup answer

    if [[ -e $destination || -L $destination ]]; then
        [[ -f $destination && ! -L $destination ]] ||
            die "Refusing to replace a directory or symbolic link: $destination"

        printf 'Replace %s? [y/N] ' "$destination"
        IFS= read -r answer || answer=''
        case "$answer" in y|Y|yes|YES) ;; *) printf 'Skipped %s\n' "$destination"; return 0;; esac

        backup="${destination}.backup-$(date +%Y%m%d-%H%M%S)-$$"
        [[ ! -e $backup && ! -L $backup ]] || die "Backup already exists: $backup"
        cp -p "$destination" "$backup"
        printf 'Backup: %s\n' "$backup"
    fi

    mkdir -p "$(dirname "$destination")"
    cp "$source" "$destination"
    printf 'Copied to %s\n' "$destination"
}
