#!/bin/bash
if ! command -v jq &>/dev/null; then exit 0; fi
INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')
if [ -n "$PROMPT" ]; then
  # Supprimer les tags système (<ide_opened_file>, <system-reminder>, etc.)
  PROMPT=$(echo "$PROMPT" | sed 's/<[^>]*>//g' | sed '/^$/d' | sed 's/^[[:space:]]*//' | head -5)
  echo "$PROMPT" > "$CLAUDE_PROJECT_DIR/tmp/last_prompt.txt"
fi
exit 0
