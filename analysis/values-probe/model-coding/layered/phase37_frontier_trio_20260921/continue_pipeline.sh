#!/usr/bin/env bash
set -euo pipefail
PHASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$PHASE/../../../../.." && pwd)"
export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"
source "$ROOT/../model-personality-corpus-v2/scripts/source_sops_keys.sh"
exec python3 -u "$PHASE/continue_pipeline.py"
