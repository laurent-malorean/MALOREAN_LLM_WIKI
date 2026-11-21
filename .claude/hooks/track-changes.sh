#!/bin/bash
if ! command -v jq &>/dev/null; then exit 0; fi
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
if [ -n "$FILE_PATH" ]; then
  echo "$FILE_PATH" >> "$CLAUDE_PROJECT_DIR/tmp/changes.log"
fi
exit 0
