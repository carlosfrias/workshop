#!/usr/bin/env bash
set -euo pipefail

# Wrapper for the bookkeeping import pipeline
# Usage: ./run_import.sh <command> [args]
#   ingest <file> [--auto-approve]
#   import <job_id>
#   rollback <job_id>
#   status
#   review

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PYTHON="${PROJECT_ROOT}/.venv/bin/python3"

if [ ! -x "$PYTHON" ]; then
    echo "ERROR: .venv/bin/python3 not found. Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

PIPELINE="${SCRIPT_DIR}/import_pipeline.py"

show_help() {
    cat <<EOF
Trading Desk — Import Pipeline Wrapper

Commands:
  ingest <file.csv|xlsx> [--auto-approve]  Ingest and validate a file
  import <job_id>                         Import a pending job
  rollback <job_id>                       Rollback an imported job
  status                                  Show all job statuses
  review                                  List pending jobs with draft entries

Examples:
  ./run_import.sh ingest ~/Downloads/fills_2026-04-21.csv
  ./run_import.sh import IMP-a1b2c3d4
  ./run_import.sh status
EOF
}

if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

CMD="$1"
shift

case "$CMD" in
    ingest|import|rollback|status|review)
        "$PYTHON" "$PIPELINE" "$CMD" "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $CMD"
        show_help
        exit 1
        ;;
esac
