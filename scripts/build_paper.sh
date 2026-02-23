#!/usr/bin/env bash
set -uo pipefail
paper="$1"
root="$2"
quiet_flag="${3:-}"

mkdir -p "$root/tmp/$paper"
export TEXINPUTS="$root/papers/$paper:"

# Determine quiet/redirection string
if [ "$quiet_flag" = "quiet" ]; then
  QUIET_REDIRECT="> /dev/null 2>&1"
else
  QUIET_REDIRECT=""
fi

# Compile (quiet if requested)
sh -c "pdflatex -interaction=nonstopmode -output-directory=\"$root/tmp/$paper\" \"$root/papers/$paper/index.tex\" $QUIET_REDIRECT" || true
sh -c "biber --input-directory=\"$root/tmp/$paper\" --output-directory=\"$root/tmp/$paper\" index $QUIET_REDIRECT" || true
sh -c "pdflatex -interaction=nonstopmode -output-directory=\"$root/tmp/$paper\" \"$root/papers/$paper/index.tex\" $QUIET_REDIRECT" || true
sh -c "pdflatex -interaction=nonstopmode -output-directory=\"$root/tmp/$paper\" \"$root/papers/$paper/index.tex\" $QUIET_REDIRECT" || true

# Move stray aux/log files into tmp
shopt -s nullglob
for f in "$root/papers/$paper"/*.aux "$root/papers/$paper"/*.log "$root/papers/$paper"/*.out "$root/papers/$paper"/*.toc; do
  mv "$f" "$root/tmp/$paper/" || true
done

if [ -f "$root/tmp/$paper/index.pdf" ]; then
  cp "$root/tmp/$paper/index.pdf" "$root/$paper.pdf"
  echo "✓ PDF compiled: $paper.pdf"
else
  echo "✗ PDF compilation failed: $paper" >&2
  exit 1
fi
