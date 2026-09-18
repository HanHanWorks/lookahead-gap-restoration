#!/bin/sh
# Build the three PDFs of the SEGAN submission from the Markdown sources, then
# check the build against those sources.
#
#   sh supp_code/build_latex.sh
#
# The Markdown is the source of truth: it is what the audit, the compression and
# the appendix move were done on, each with its own record.  The .tex files are
# generated from it and should not be edited by hand.
set -e
cd "$(dirname "$0")/.."

PY="${PY:-python3}"

echo "== Markdown -> LaTeX"
"$PY" supp_code/md_to_latex.py

compile () {
    if command -v latexmk >/dev/null 2>&1; then
        latexmk -pdf -interaction=nonstopmode -halt-on-error "$1.tex" >/dev/null
    elif command -v pdflatex >/dev/null 2>&1; then
        # twice, so that \ref and \cite resolve
        pdflatex -interaction=nonstopmode "$1.tex" >/dev/null
        pdflatex -interaction=nonstopmode "$1.tex" >/dev/null
    elif command -v tectonic >/dev/null 2>&1; then
        tectonic -X compile "$1.tex"
    else
        echo "no TeX engine found (looked for latexmk, pdflatex, tectonic)" >&2
        exit 1
    fi
}

echo "== engine: $( { command -v latexmk || command -v pdflatex || command -v tectonic; } )"
for f in SEGAN_manuscript_2026-09-14 \
         SEGAN_supplementary_material_2026-09-14 \
         SEGAN_highlights_2026-09-14; do
    printf '   %-46s' "$f"
    compile "$f"
    echo "ok"
done

echo "== check the PDFs against the Markdown"
"$PY" supp_code/verify_latex.py
