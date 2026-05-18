#!/bin/bash
#
# task-collect-artifacts.sh
# Pull wiki documentation artifacts from all lab nodes back to orchestrator.
# Run after a session that produced artifacts on remote nodes.
#
# Classification logic:
#   TODAY-STATUS-*       → wiki/operational/
#   SESSION-NOTES-*      → wiki/operational/
#   RECOMMENDATION-*     → wiki/recommendations/
#   PLAN-*               → wiki/planning/
#   BACKLOG.md           → wiki/operational/
#   fnet*.json           → lab-specs/
#   decomposition-examples/* → wiki/decomposition-examples/
#
# Usage:
#   cd technical-infrastructure/scripts
#   ./task-collect-artifacts.sh --nodes all
#   ./task-collect-artifacts.sh --nodes fnet1,fnet3,fnet5
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
WIKI_BASE="$REPO_DIR/technical-infrastructure/wiki"
LABSPECS="$REPO_DIR/technical-infrastructure/lab-specs"
TEMP_DIR="/tmp/artifact-collect-$(date +%s)"

declare -a NODES=()
REPORT_FILE=""

usage() {
    echo "Usage: $(basename "$0") --nodes [all|fnet1,fnet2,...] [--report file]"
    exit 1
}

parse_args() {
    if [ $# -eq 0 ]; then usage; fi
    while [ $# -gt 0 ]; do
        case "$1" in
            --nodes)
                shift
                IFS=',' read -ra NODES <<< "$1"
                [ "${NODES[0]}" = "all" ] && NODES=(fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7)
                ;;
            --report)
                shift; REPORT_FILE="$1"
                ;;
            --help|-h)
                usage
                ;;
            *)
                echo "Unknown option: $1"; usage
                ;;
        esac
        shift
    done
}

# Classify a single file into its destination category
classify_artifact() {
    local basename="$(basename "$1")"

    case "$basename" in
        TODAY-STATUS-*.md)
            echo "wiki/operational"
            ;;
        SESSION-NOTES-*.md)
            echo "wiki/operational"
            ;;
        RECOMMENDATION-*.md)
            echo "wiki/recommendations"
            ;;
        PLAN-*.md)
            echo "wiki/planning"
            ;;
        BACKLOG.md)
            echo "wiki/operational"
            ;;
        fnet*.json)
            echo "lab-specs"
            ;;
        lab-capacity-report.json)
            echo "lab-specs"
            ;;
        *)
            # Check if the file is inside a decomposition-examples directory
            if [[ "$1" == *"decomposition-examples"* ]]; then
                echo "wiki/decomposition-examples"
            elif [[ "$1" == *.md ]]; then
                echo "unknown-md"
            elif [[ "$1" == *.json ]]; then
                echo "unknown-json"
            else
                echo "skip"
            fi
            ;;
    esac
}

# Collect artifacts from a single node
collect_from_node() {
    local host="$1"
    local node_tmp="$TEMP_DIR/$host"
    mkdir -p "$node_tmp"

    # Collect from known wiki artifact directories
    # Use rsync-like find+scp for speed, or just find files
    local found_count=0
    local node_dest="$node_tmp/artifacts"
    mkdir -p "$node_dest"

    # Pull artifacts via ssh+find+scp combo
    ssh -o ConnectTimeout=3 friasc@"$host" "
        find /srv/tasks/completed /srv/wiki /root/wiki /home/friasc/wiki \
            -type f \( -name 'TODAY-STATUS-*.md' -o -name 'SESSION-NOTES-*.md' \
                    -o -name 'RECOMMENDATION-*.md' -o -name 'PLAN-*.md' \
                    -o -name 'BACKLOG.md' -o -name 'fnet*.json' \
                    -o -name 'lab-capacity-report.json' \) 2>/dev/null | head -50
    " > "$node_tmp/files.txt" 2>/dev/null || true

    # Also check /home/friasc/Dropbox if user writes there
    ssh -o ConnectTimeout=3 friasc@"$host" "
        find /home/friasc/Dropbox/workshop/technical-infrastructure/wiki /home/friasc/Dropbox/workshop/technical-infrastructure/lab-specs \
            -type f \( -name 'TODAY-STATUS-*.md' -o -name 'SESSION-NOTES-*.md' \
                    -o -name 'RECOMMENDATION-*.md' -o -name 'PLAN-*.md' \
                    -o -name 'BACKLOG.md' -o -name 'fnet*.json' \
                    -o -name 'lab-capacity-report.json' \) 2>/dev/null | head -50
    " >> "$node_tmp/files.txt" 2>/dev/null || true

    # Deduplicate and pull
    if [ -s "$node_tmp/files.txt" ]; then
        sort "$node_tmp/files.txt" | uniq | while IFS= read -r src; do
            [ -z "$src" ] && continue
            dest="$node_dest/$(basename "$src")"
            scp -o ConnectTimeout=3 "friasc@$host:$src" "$dest" 2>/dev/null && ((found_count++)) || true
        done
    fi

    # Also directly scp any files in /srv/tasks/completed/*.json (they are the result files)
    scp -o ConnectTimeout=3 "friasc@$host:/srv/tasks/completed/*.json" "$node_dest/" 2>/dev/null || true

    echo "$found_count"
}

# Copy classified artifacts to their proper destination
distribute_artifacts() {
    local src_dir="$1"
    local moved=0
    local skipped=0

    while IFS= read -r -d '' artifact; do
        local category
        category=$(classify_artifact "$artifact")

        case "$category" in
            skip|unknown-md|unknown-json)
                ((skipped++))
                continue
                ;;
            wiki/operational|wiki/recommendations|wiki/planning|wiki/decomposition-examples|lab-specs)
                local dest
                dest="$REPO_DIR/technical-infrastructure/$category"
                mkdir -p "$dest"
                if cp -n "$artifact" "$dest/" 2>/dev/null; then
                    # -n flag means "don't overwrite existing" (preserve local edits)
                    ((moved++))
                    echo "  COPIED $(basename "$artifact") → $category"
                else
                    echo "  EXISTS $(basename "$artifact") → $category (preserved local)"
                fi
                ;;
        esac
    done < <(find "$src_dir" -type f -print0)

    echo ""
    echo "$moved new artifacts placed, $skipped skipped."
}

# Main
parse_args "$@"

if [ ${#NODES[@]} -eq 0 ]; then usage; fi

mkdir -p "$TEMP_DIR"
trap 'rm -rf "$TEMP_DIR"' EXIT

TOTAL_FILES=0

for host in "${NODES[@]}"; do
    echo "--- $host ---"
    count=$(collect_from_node "$host")
    TOTAL_FILES=$((TOTAL_FILES + count))
    echo "  Retrieved $count artifacts"
done

# Distribute to proper locations
if [ "$TOTAL_FILES" -gt 0 ] || [ -d "$TEMP_DIR" ]; then
    echo ""
    echo "=== Distributing $TOTAL_FILES artifacts ==="
    for host in "${NODES[@]}"; do
        if [ -d "$TEMP_DIR/$host/artifacts" ]; then
            distribute_artifacts "$TEMP_DIR/$host/artifacts"
        fi
    done
fi

echo ""
echo "=== Done ==="
echo "Run ./wiki-auto-commit.sh to stage and commit artifacts."
