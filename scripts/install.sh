#!/usr/bin/env bash
set -eo pipefail

run_install() (
    local helpers=$1 ref=$2 source skill extra kind index backup_mode seen_source already_processed skill_index
    local targets=("$HOME/.claude/CLAUDE.md" "$HOME/.codex/AGENTS.md" "$HOME/.config/opencode/AGENTS.md")
    local agent_ids=(claude-code codex opencode)
    local instructions=() destinations=() skill_agents=() sources=() skills=() selection=()
    local processed_sources=() batch_skills=()
    source "$helpers/common.sh"
    require_terminal

    MENU_LABELS=("Claude: ${targets[0]}" "Codex: ${targets[1]}" "OpenCode: ${targets[2]}")
    MENU_ENABLED=(1 1 1)
    select_menu 'Choose target agents for instructions and skills' 1 1 || { printf 'Cancelled. Nothing installed.\n'; return 0; }
    instructions=("${MENU_RESULT[@]}")

    MENU_LABELS=(); MENU_ENABLED=()
    while read -r source skill extra || [[ -n $source ]]; do
        [[ -n $source && $source != \#* ]] || continue
        [[ -n $skill && -z $extra ]] || die "Invalid skills.txt entry: $source $skill $extra"
        sources+=("$source"); skills+=("$skill")
        kind=external; [[ $source != lioqing/.agents ]] || kind=personal
        MENU_LABELS+=("$skill ($kind, $source)"); MENU_ENABLED+=(1)
    done < "$helpers/skills.txt"
    select_menu 'Choose personal and external skills to install globally' 1 1 || { printf 'Cancelled. Nothing installed.\n'; return 0; }
    selection=("${MENU_RESULT[@]}")
    command -v npx >/dev/null 2>&1 || die 'Node.js/npm (npx) is required to install skills.'

    printf 'Selected instruction destinations (existing files require overwrite confirmation):\n'
    for index in "${instructions[@]}"; do
        destinations+=("${targets[index]}")
        skill_agents+=("${agent_ids[index]}")
        printf '  %s\n' "${targets[index]}"
    done
    MENU_LABELS=('Backup existing files before replacing' 'Replace without backup')
    MENU_ENABLED=(1 1)
    select_menu 'Choose how to handle existing instruction files' 0 || { printf 'Cancelled. Nothing installed.\n'; return 0; }
    backup_mode=--backup; [[ ${MENU_RESULT[0]} == 0 ]] || backup_mode=--no-backup

    AGENTS_REF=$ref bash "$helpers/install-agents.sh" "$backup_mode" -- "${destinations[@]}" || exit $?
    for index in "${selection[@]}"; do
        source=${sources[index]}; already_processed=0
        for seen_source in "${processed_sources[@]}"; do
            if [[ $seen_source == "$source" ]]; then already_processed=1; break; fi
        done
        [[ $already_processed == 0 ]] || continue
        processed_sources+=("$source")
        batch_skills=()
        for skill_index in "${selection[@]}"; do
            if [[ ${sources[skill_index]} == "$source" ]]; then batch_skills+=("${skills[skill_index]}"); fi
        done
        if [[ $source == lioqing/.agents ]]; then source="https://github.com/lioqing/.agents/tree/$ref"; fi
        printf 'Installing %s from %s\n' "${batch_skills[*]}" "$source"
        npx skills add "$source" --skill "${batch_skills[@]}" --global --yes --agent "${skill_agents[@]}" ||
            die "Skill installation failed: ${batch_skills[*]}. Earlier installations may have completed."
    done
    printf 'Selected agent instructions and skills installed.\n'
)

# Keep bootstrap cleanup in a parent subshell, separate from the menu's traps.
install_bundle() (
    local ref=${AGENTS_REF:-master} helpers='' temporary='' file
    if [[ -n ${BASH_SOURCE[0]:-} ]]; then helpers=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd); fi
    if [[ -z $helpers || ! -f $helpers/common.sh ]]; then
        command -v curl >/dev/null 2>&1 || { printf 'Error: curl is required.\n' >&2; exit 1; }
        temporary=$(mktemp -d "${TMPDIR:-/tmp}/install-bundle.XXXXXXXX")
        trap 'rm -f -- "$temporary/common.sh" "$temporary/install-agents.sh" "$temporary/skills.txt"; rmdir -- "$temporary"' EXIT
        trap 'exit 130' INT
        trap 'exit 143' TERM
        helpers=$temporary
        for file in common.sh install-agents.sh skills.txt; do
            curl -fsSL --connect-timeout 10 --max-time 120 \
                "https://raw.githubusercontent.com/lioqing/.agents/$ref/scripts/$file" -o "$helpers/$file" || exit 1
            [[ -s $helpers/$file ]] || { printf 'Error: Downloaded %s is empty. Nothing installed.\n' "$file" >&2; exit 1; }
        done
    fi
    run_install "$helpers" "$ref"
)

install_bundle "$@"
