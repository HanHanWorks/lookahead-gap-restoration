"""Convert the SEGAN manuscript and its supplementary material from the working
Markdown into elsarticle LaTeX.

The conversion is literal about content: no sentence is rewritten, no number is
recomputed.  What changes is the medium.

  display math ``$$ ... \\tag{N}$$``   ->  ``equation`` carrying ``\\label{eq:N}``
  pipe tables                          ->  ``table`` + ``tabular`` + booktabs
  ``**Figure N.**`` captions           ->  ``figure`` floats with the published
                                           figure file, placed right after the
                                           text block that first cites them
  ``**Table N.**`` captions            ->  the ``\\caption`` of that table
  ``Section 5.4`` / ``Table 7`` / ``Eq. (5)`` / ``[26--29]``
                                       ->  ``\\ref`` / ``\\eqref`` / ``\\cite``
  the ``[N]`` reference list           ->  ``thebibliography``

Cross-references are *converted* rather than transcribed so that LaTeX owns the
numbering; `verify_latex.py` then checks every label resolved back to the number
the Markdown quotes, which is what makes the substitution safe.

Modes:
  main  the manuscript: sections, tables, figures, equations, citations all
        become cross-references.  ``Appendix D`` and ``Table S1`` stay literal,
        because they live in the other document.
  supp  the supplementary material: its appendices and its three tables get
        cross-references; ``Section 5.3``, ``Table 5`` and ``Eq. (5)`` refer to
        the *manuscript* and therefore stay literal.
  bib   reference text: escape and typography only, no citations, no xrefs.
"""
from __future__ import annotations

import pathlib
import re
import sys
import textwrap

WORK = pathlib.Path(__file__).resolve().parent.parent
MAIN_MD = WORK / "SEGAN_manuscript_revised_2026-09-13.md"
SUPP_MD = WORK / "SEGAN_supplementary_material_2026-09-14.md"
MAIN_TEX = WORK / "SEGAN_manuscript_2026-09-14.tex"
SUPP_TEX = WORK / "SEGAN_supplementary_material_2026-09-14.tex"
HL_TEX = WORK / "SEGAN_highlights_2026-09-14.tex"

FIGFILES = {
    1: "fig1_framework", 2: "fig2_attribution", 3: "fig3_gap_by_condition",
    4: "fig4_instance_rule", 5: "fig5_depth_profile", 6: "fig6_phase",
    7: "fig7_headtohead", 8: "fig8_capacity_rules", 9: "fig9_cost_quality",
}
NREFS = 41

# Figures are emitted after the block that cites them, so that a reader meets a
# figure next to the text that reads it, and so that the printed numbers follow
# the order of appearance (which is what the journal asks for).  Two figures are
# first mentioned somewhere that does not read them: Figure 6 in the sample-rule
# caveat of Section 5.0, and Figure 9 in a passing comparison in Section 5.7.
# They are anchored at the next mention instead, which keeps the anchors
# ascending.
FIG_ANCHOR_SKIP = {6: 1, 9: 1}

# Author block.  SEGAN is single-anonymized, so this stays in the manuscript
# rather than on a separate title page; the same data is on the title page of
# the companion IJEPES submission.
# Author block.  SEGAN is single-anonymized, so this stays in the manuscript
# rather than on a separate title page; the same data is on the title page of
# the companion IJEPES submission.  CAS takes the affiliation in parts, and
# takes the ORCID iD as a field of \author, so both are held that way here.
AUTHORS = {
    "first": "Zihao Huang",
    "corresponding": "Yan Chen",
    "email": "cy@gxu.edu.cn",
    "first_orcid": "0009-0006-5842-6516",
    "corresponding_orcid": "0000-0002-9950-684X",
    "aff_a": {
        "organization": "Guangxi Key Laboratory of Digital Infrastructure, "
                        "Guangxi Zhuang Autonomous Region Information Center",
        "city": "Nanning", "postcode": "530000", "country": "China"},
    "aff_b": {
        "organization": "School of Computer and Electronic Information, "
                        "Guangxi University",
        "city": "Nanning", "postcode": "530000", "country": "China"},
    "shorttitle": "How much lookahead is worth having? An exactly computable value-and-accessibility criterion for restoration-ordering benchmarks",
    "shortauthors": "Z. Huang and Y. Chen",
}

# Per-table float-placement override (label -> CAS 'pos' key-value).  The CAS
# class renews the table environment: its optional argument is a key-value
# list (pos=..., width=...), NOT a standard placement specifier, and the
# class default is pos=t, which forces every table to a page top.  Table 1
# has to sit at the end of Section 2.2, directly after the paragraph that
# explains Eq. (2), so it asks for here-or-bottom.
TABLE_PLACEMENT = {"tab:1": "pos=htb"}


PREAMBLE = r"""\documentclass[preprint,12pt]{elsarticle}

\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{url}
\usepackage{tabularx}
\usepackage{array}
\biboptions{numbers,sort&compress}
\graphicspath{{figures/}}
\setlength{\emergencystretch}{2em}
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.8}
\renewcommand{\textfraction}{0.07}
\renewcommand{\floatpagefraction}{0.75}
\setcounter{topnumber}{2}\setcounter{bottomnumber}{2}
\setcounter{totalnumber}{4}

"""
PREAMBLE_CAS = r"""\makeatletter
% The CAS bundle sits in els-cas-templates/.  \input@path is consulted for
% \documentclass too, and both prefixes are given so that the file compiles
% from this directory and from manuscript_sections/ alike.
\def\input@path{{els-cas-templates/}{../els-cas-templates/}}
\makeatother
\documentclass[a4paper,fleqn]{cas-sc}

\usepackage[numbers,sort&compress]{natbib}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{url}
\usepackage{tabularx}
\usepackage{array}
% figures/ holds the article figures; the CAS directory also has to be on the
% path, because the class pulls its own social-media thumbnails from
% thumbnails/ next to cas-common.sty.
\graphicspath{{figures/}{els-cas-templates/}{../els-cas-templates/}}
\setlength{\emergencystretch}{2em}
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.8}
\renewcommand{\textfraction}{0.07}
\renewcommand{\floatpagefraction}{0.75}
\setcounter{topnumber}{2}\setcounter{bottomnumber}{2}
\setcounter{totalnumber}{4}

"""

PRELUDE_MAIN = r"""% ---------------------------------------------------------------------------
% Manuscript prepared for SEGAN (Sustainable Energy, Grids and Networks).
% Elsevier CAS class, single column (cas-sc), numbered references,
% single-anonymized review.  The class files are the ones in
% els-cas-templates/, found through \input@path.
% Generated from the Markdown source by supp_code/md_to_latex.py --- edit the
% Markdown and re-run that script rather than editing this file.
% ---------------------------------------------------------------------------

\let\WriteBookmarks\relax
\def\floatpagepagefraction{1}
\def\textpagefraction{.001}

"""


PRELUDE_SUPP = r"""% ---------------------------------------------------------------------------
% Supplementary material: the five appendices cited in the manuscript as
% Appendices A--E, with the three tables they contain (Tables S1--S3).
% Generated from the Markdown source by supp_code/md_to_latex.py.
% ---------------------------------------------------------------------------

"""

UNICODE_MAP = {
    "\u2014": "---",        # em dash
    "\u2013": "--",         # en dash
    "\u00b7": r"$\cdot$",   # middle dot: the separator in the contributions list
    "\u0107": r"\'{c}",
    "\u00e9": r"\'{e}",
    "\u010d": r"\v{c}",
    "\u00a0": "~",
}

SPECIAL = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
           "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
           "^": r"\textasciicircum{}", "\\": r"\textbackslash{}"}

SENT = "\x00"
SENT_END = "\x01"
SEC_ID = r"\d+(?:\.\d+)?"

COUNT: dict[str, int] = {}


def _bump(k):
    COUNT[k] = COUNT.get(k, 0) + 1


def escape(s: str) -> str:
    return "".join(SPECIAL.get(c, c) for c in s)


class Renderer:
    """One span of Markdown prose -> LaTeX, with math, code and URLs protected."""

    def __init__(self, mode: str):
        self.mode = mode
        self.store: list[str] = []

    def hold(self, latex: str) -> str:
        self.store.append(latex)
        return f"{SENT}{len(self.store) - 1}{SENT_END}"

    def restore(self, s: str, limit: int = 12) -> str:
        for _ in range(limit):
            if SENT not in s:
                break
            s = re.sub(rf"{SENT}(\d+){SENT_END}",
                       lambda m: self.store[int(m.group(1))], s)
        return s

    # ------------------------------------------------------------------ stages
    def _code(self, s):
        def f(m):
            _bump("code")
            body = escape(m.group(1))
            # a long path is one unbreakable word to TeX; give it breakpoints
            body = re.sub(r"(\\_|/|\.)", r"\1\\allowbreak{}", body)
            return self.hold(r"\texttt{%s}" % body)
        return re.sub(r"`([^`\n]+)`", f, s)

    def _urls(self, s):
        def f(m):
            u, tail = m.group(0), ""
            while u and u[-1] in ".,;":
                tail, u = u[-1] + tail, u[:-1]
            _bump("url")
            return self.hold(r"\url{%s}" % u) + tail
        return re.sub(r"https?://\S+", f, s)

    def _math(self, s):
        def f(m):
            _bump("math")
            return self.hold(m.group(0))
        return re.sub(r"\$[^$\n]+\$", f, s)

    def _emphasis(self, s):
        s = re.sub(r"\*\*(.+?)\*\*",
                   lambda m: self.hold(r"\textbf{%s}" % self.render(m.group(1))), s)
        s = re.sub(r"\*(?!\s)([^*]+?)(?<!\s)\*",
                   lambda m: self.hold(r"\emph{%s}" % self.render(m.group(1))), s)
        return s

    def _citations(self, s):
        if self.mode == "supp":
            # The supplementary document carries no bibliography of its own: a
            # bracketed number in it refers to the reference list of the
            # manuscript.  Converting it to \cite would leave the key undefined
            # in this document, so LaTeX would print "[?]" wherever the
            # supplementary cites a work -- which is what happened to the eight
            # citations in Appendices D and E (including every row of Table S3,
            # the timing table the reporting standard argues from).  Keep the
            # number as literal text instead; the manifest of the CAS bundle
            # records no bibliography for this document.
            return s

        def f(m):
            keys = []
            for part in re.split(r"[,\s]+", m.group(1).strip()):
                if not part:
                    continue
                mm = re.fullmatch(r"(\d+)(?:\s*(?:--|\u2013)\s*(\d+))?", part)
                if not mm:
                    return m.group(0)
                a = int(mm.group(1))
                b = int(mm.group(2)) if mm.group(2) else a
                if not (1 <= a <= NREFS and 1 <= b <= NREFS):
                    return m.group(0)
                keys += [f"ref{k}" for k in range(a, b + 1)]
            if not keys:
                return m.group(0)
            _bump("cite")
            return self.hold(r"\cite{%s}" % ",".join(keys))
        return re.sub(r"\[(\d[\d,\s\u2013-]*)\]", f, s)

    def _ref_list(self, s, word, idpat, prefix):
        pat = re.compile(rf"\b({word}) ({idpat}(?:\s*(?:--|\u2013|,|and)\s*{idpat})*)")

        def f(m):
            _bump(f"xref:{prefix}")
            chain = re.sub(idpat,
                           lambda x: self.hold(r"\ref{%s:%s}" % (prefix, x.group(0))),
                           m.group(2))
            # hold the whole thing: a bare "~" would be escaped into \textasciitilde{}
            return self.hold(f"{m.group(1)}~{chain.replace(' and ', ' and~')}")
        return pat.sub(f, s)

    def _xrefs(self, s):
        if self.mode == "main":
            s = self._ref_list(s, r"Sections?", SEC_ID, "sec")
            s = self._ref_list(s, r"Tables?", r"\d+", "tab")
            s = self._ref_list(s, r"Figures?", r"\d+", "fig")
            s = re.sub(r"\bEq\.\s*\((\w+)\)",
                       lambda m: self.hold("Eq.~" + r"\eqref{eq:%s}" % m.group(1)), s)
        elif self.mode == "supp":
            s = self._ref_list(s, r"Tables?", r"S\d", "tab")
        return s

    @staticmethod
    def _quotes(s):
        return re.sub(r'"([^"\n]*)"', lambda m: "``" + m.group(1) + "''", s)

    def render(self, s: str) -> str:
        # non-ASCII is turned into LaTeX *before* escaping, so it has to be held,
        # or \'e would come out as \textbackslash{}'e
        for k, v in UNICODE_MAP.items():
            if k in s:
                s = s.replace(k, self.hold(v))
        s = self._code(s)
        s = self._urls(s)
        s = self._math(s)
        s = self._emphasis(s)
        if self.mode != "bib":
            s = self._citations(s)
            s = self._xrefs(s)
        s = self._quotes(s)
        s = escape(s)
        return self.restore(s)


# --------------------------------------------------------------------------
# block parsing
# --------------------------------------------------------------------------
def is_table_row(l):
    return l.lstrip().startswith("|")


def is_list_item(l):
    return bool(re.match(r"\s*(?:-|\d+\.)\s+\S", l))


def push(store, latex, text=""):
    store.append(latex)


def collect_para(lines, i):
    para = []
    while i < len(lines) and lines[i].strip() and not (
            lines[i].startswith("#") or lines[i].startswith("> ")
            or is_table_row(lines[i]) or is_list_item(lines[i])
            or lines[i].startswith("$$") or lines[i].strip() == "---"
            or re.match(r"^\[\d+\] ", lines[i])):
        para.append(lines[i].strip())
        i += 1
    return " ".join(para), i


def collect_display(lines, i):
    blk = []
    while i < len(lines):
        blk.append(lines[i])
        if sum(l.count("$$") for l in blk) >= 2:
            i += 1
            break
        i += 1
    return blk, i


# Equation (4) is the only display in the paper that overruns the measure.  Its
# \qquad separators are where the three definitions already break, so splitting
# there changes the layout and nothing else.
SPLIT_EQUATIONS = {"eq:4"}


def display_latex(blk):
    text = " ".join(blk)
    m = re.search(r"\$\$(.*)\$\$", text, flags=re.S)
    body = (m.group(1) if m else text).strip()
    tag = re.search(r"\\tag\{([^}]+)\}", body)
    if tag:
        body = body.replace(tag.group(0), "").strip().rstrip(",").rstrip()
        _bump("equation")
        label = tag.group(1)
        if f"eq:{label}" in SPLIT_EQUATIONS:
            body = "\\begin{split}\n" + body.replace(r"\qquad", r"\\") + "\n\\end{split}"
        windback = "" if label.isdigit() else "\\addtocounter{equation}{-1}\n"
        return (f"\\begin{{equation}}\\tag{{{label}}}\\label{{eq:{label}}}\n"
                f"{body}\n\\end{{equation}}\n{windback}")
    _bump("display")
    return "\\[\n" + body.rstrip(",") + "\n\\]"


def table_rows_latex(cells, spec, env, heavy):
    body = [r"\toprule", " & ".join(cells[0]) + r" \\", r"\midrule"]
    body += [" & ".join(r) + r" \\" for r in cells[2:]]
    body += [r"\bottomrule"]
    inner = "\n".join(body)
    if env == "tabularx":
        # \hyphenpenalty=0 is what lets a long word break inside a narrow column
        # ("identifiable" in Table 3) instead of running past the table's edge,
        # which is what it did at the document's default penalty of 50.
        # \small is 9 pt in the 10 pt CAS document (it was 10.9 pt under the
        # 12 pt elsarticle preprint, where the wide tables needed \footnotesize
        # to fit); at 9 pt the tables stay inside Elsevier's 8--12 pt range and
        # read as tables rather than as footnotes.
        return ("{\\small\\hyphenpenalty=0\\exhyphenpenalty=0\n"
                "\\begin{tabularx}{\\linewidth}{" + spec + "}\n" + inner
                + "\n\\end{tabularx}}")
    return "\\begin{tabular}{" + spec + "}\n" + inner + "\n\\end{tabular}"


def visual_len(c):
    c = re.sub(r"\\[a-zA-Z]+\*?", "", c)
    c = re.sub(r"\$[^$]*\$", "xxx", c)
    return len(re.sub(r"[{}]", "", c))


def table_geometry(cells):
    """Pick an environment that fits the text block at a legible type size.

    Text-heavy tables wrap, via tabularx with weighted X columns; dense numeric
    tables are set at their natural width when that fits.  An earlier version
    scaled the wide ones with \\resizebox, which shrinks the type to whatever
    fits: Table 4 came out at 2.8 pt and Tables 3, 6 and 8 below 7.8 pt, against
    the 8-12 pt these tables are supposed to use.  Nothing is scaled now: a long
    header wraps inside its own column instead.
    """
    ncol = len(cells[0])
    widths = [max(visual_len(r[i]) for r in cells) for i in range(ncol)]
    if ncol <= 4:
        # A wide cell here means prose, not a number: unwrapped `l` columns would
        # run the table past the text block, and everything beyond the page is
        # simply not rendered (the supplementary validation table lost its whole
        # right-hand side that way).  Wrap instead.
        if max(widths) < 12:
            spec = "".join("l" if (i == 0 or widths[i] > 22) else "c" for i in range(ncol))
            return "tabular", spec, False
        xcols = [i for i, w in enumerate(widths) if w >= 12]
        tot = sum(widths[i] for i in xcols) or 1
        spec = []
        for i in range(ncol):
            if i in xcols:
                spec.append(rf">{{\raggedright\arraybackslash"
                            rf"\hsize={len(xcols) * widths[i] / tot:.3f}\hsize}}X")
            else:
                spec.append("l" if i == 0 else "c")
        return "tabularx", "".join(spec), False
    # wide: allocate the text block by what each column must be able to hold,
    # never less than its longest unbreakable word -- that floor is what keeps
    # "Protocol" off the next header and "identifiable" inside the table -- and
    # cap the surplus of a text-heavy column so a long header wraps instead of
    # squeezing the numeric columns beside it
    cap = 15 if ncol >= 7 else 18
    need, want = [], []
    for i in range(ncol):
        longest = max((visual_len(w) for r in cells for w in str(r[i]).split()), default=1)
        need.append(longest)
        want.append(max(longest, min(widths[i], cap)))
    avail = 76          # character widths of \small (9 pt) type in the CAS text block
    if sum(want) > avail:
        slack = max(avail - sum(need), 0)
        extra = [want[i] - need[i] for i in range(ncol)]
        k = slack / (sum(extra) or 1)
        final = [need[i] + extra[i] * k for i in range(ncol)]
    else:
        final = want
    tot = sum(final) or 1
    spec = "".join(rf">{{\raggedright\arraybackslash"
                   rf"\hsize={ncol * final[i] / tot:.3f}\hsize}}X" for i in range(ncol))
    return "tabularx", spec, False


def split_caption(raw):
    """First sentence is the caption; the rest is a table note.

    Elsevier: "Place any table notes below the table body."  Splitting on the
    first full stop is only safe if maths and code spans are skipped, since both
    can contain stops (`$K \\ge 7$`, `stepwise_oracle.csv`).
    """
    depth_dollar = backtick = False
    for i, ch in enumerate(raw):
        if ch == "$" and not backtick:
            depth_dollar = not depth_dollar
        elif ch == "`" and not depth_dollar:
            backtick = not backtick
        elif ch == "." and not depth_dollar and not backtick:
            if i + 1 < len(raw) and raw[i + 1] == " ":
                return raw[: i + 1].strip(), raw[i + 2:].strip()
    return raw.strip(), ""


def wrap_tex(text, width=76):
    r"""Hard-wrap a paragraph for the CAS abstract environment.

    cas-sc does not typeset the abstract where it is written: it writes it
    verbatim to \jobname.abs and inputs that file again at the title.  Emitting
    the abstract as a single 1,600-character line works, but leaves the whole
    paragraph to the file reader; wrapping it costs nothing and keeps the
    generated .tex readable.
    """
    return "\n".join(textwrap.wrap(text, width))


def credit_roles(decl_md):
    r"""Per-author CRediT roles, read out of the declarations block.

    The Markdown stays the single source of truth: the roles are lifted from
    the CRediT paragraph rather than duplicated in this script.  Elsevier's
    taxonomy capitalises each role, so the first letter of every
    comma-separated role is upper-cased here.
    """
    m = re.search(r"\*\*CRediT authorship contribution statement\.\*\*(.*?)"
                  r"(?=\n\n\*\*|\Z)", decl_md, flags=re.S)
    if not m:
        return []
    roles = []
    for a in re.finditer(r"\*\*(.+?):\*\*\s*(.*?)(?=\*\*[^*]+:\*\*|\Z)",
                         m.group(1), flags=re.S):
        raw = " ".join(a.group(2).split()).rstrip(".")
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        parts = [p[:1].upper() + p[1:] for p in parts]
        roles.append((a.group(1).strip(), ", ".join(parts)))
    return roles


def affiliation_tex(key, aff):
    r"""A CAS \affiliation, which takes the address in named parts."""
    return ("\\affiliation[" + key + "]{organization={" + aff["organization"] + "},\n"
            "  city={" + aff["city"] + "}, postcode={" + aff["postcode"] + "}, "
            "country={" + aff["country"] + "}}")


def declarations_latex(md_text, render, skip=()):
    r"""Each `**Heading.** body` paragraph becomes its own unnumbered section.

    Elsevier does not have a "Declarations" section; the declarations are
    separate sections, and the review form looks for their exact names.  The
    CRediT statement is skipped, because CAS prints it from \credit and
    \printcredits instead.
    """
    out = []
    for m in re.finditer(r"\*\*(.+?)\.\*\*\s*(.*?)(?=\n\n|\Z)", md_text, flags=re.S):
        head = m.group(1).strip()
        if head in skip:
            continue
        body = " ".join(m.group(2).split())
        out.append(f"\\section*{{{head}}}\n\n{render(body)}")
    return "\n\n".join(out)


class Body:
    """Convert a run of Markdown blocks into LaTeX, in document order."""

    def __init__(self, md, mode):
        self.md = md
        self.mode = mode
        self.r = Renderer(mode)
        self.out: list[str] = []
        self.chunks: list[tuple[str, int]] = []
        self.figcaps: dict[int, str] = {}
        self.bibitems: list[str] = []
        self.pending = None
        self.keywords: list[str] = []

    def emit(self, latex, text=""):
        self.out.append(latex)
        self.chunks.append((text, len(self.out) - 1))

    def run(self):
        lines = self.md.split("\n")
        i = 0
        prev = -1
        while i < len(lines):
            if i == prev:
                raise RuntimeError(f"scanner made no progress at line {i}: "
                                   f"{lines[i][:80]!r}")
            prev = i
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            if self.pending and not is_table_row(line):
                self.flush_pending()
            if line.startswith("> "):
                blk = []
                while i < len(lines) and lines[i].startswith(">"):
                    blk.append(re.sub(r"^>\s?", "", lines[i]))
                    i += 1
                self.emit("\\begin{quote}\n" + self.fragment(blk) + "\n\\end{quote}",
                          " ".join(blk))
                continue
            if line.lstrip().startswith("#"):
                self.heading(line)
                i += 1
                continue
            if line.strip() == "---":
                i += 1
                continue
            if is_table_row(line):
                rows = []
                while i < len(lines) and is_table_row(lines[i]):
                    rows.append(lines[i])
                    i += 1
                self.table(rows)
                continue
            if line.startswith("$$") or line.count("$$") % 2 == 1:
                blk, i = collect_display(lines, i)
                self.emit(display_latex(blk), " ".join(blk))
                continue
            if is_list_item(line):
                ordered = bool(re.match(r"\s*\d+\.\s", line))
                items, cur = [], None
                while i < len(lines):
                    l = lines[i]
                    if is_list_item(l):
                        if cur is not None:
                            items.append(cur)
                        cur = re.sub(r"^\s*(?:-|\d+\.)\s+", "", l)
                        i += 1
                    elif not l.strip():
                        j = i
                        while j < len(lines) and not lines[j].strip():
                            j += 1
                        if (j < len(lines) and is_list_item(lines[j])
                                and bool(re.match(r"\s*\d+\.\s", lines[j])) == ordered):
                            i = j
                        else:
                            break
                    else:
                        cur += " " + l.strip()
                        i += 1
                if cur is not None:
                    items.append(cur)
                env = "enumerate" if ordered else "itemize"
                self.emit(f"\\begin{{{env}}}\n"
                          + "\n".join(rf"  \item {self.r.render(x)}" for x in items)
                          + f"\n\\end{{{env}}}", " ".join(items))
                continue
            if re.match(r"^\[\d+\] ", line):
                m = re.match(r"^\[(\d+)\] (.*)$", line)
                rr = Renderer("bib")
                self.bibitems.append(f"\\bibitem{{ref{m.group(1)}}}\n{rr.render(m.group(2))}")
                self.chunks.append((f"ref {m.group(1)}", len(self.out)))
                i += 1
                continue
            para, i = collect_para(lines, i)
            self.para(para)
        self.flush_pending()
        return "\n\n".join(self.out)

    def fragment(self, blk):
        """Render a blockquote's inner lines with the full block machinery.

        It must be the full machinery: a Proposition blockquote can carry a
        paragraph, a display, and an *Algorithm* body with numbered steps, and a
        scanner that only knows paragraphs and displays would spin on the steps.
        """
        sub = Body("\n".join(blk), self.mode)
        sub.r = self.r
        return sub.run()

    def heading(self, line):
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        depth, name = len(m.group(1)), m.group(2).strip()
        if depth == 1:
            self.emit(f"% title: {name}", name)
        elif depth == 2 and re.match(r"\d+\.\s", name):
            num, rest = name.split(".", 1)
            self.emit(rf"\section{{{rest.strip()}}}\label{{sec:{num.strip()}}}", name)
        elif depth == 2 and name.startswith("Appendix "):
            letter, rest = name.split(".", 1)
            self.emit(rf"\section{{{rest.strip()}}}\label{{app:{letter.split()[-1]}}}",
                      name)
        elif depth == 2:
            self.emit(f"\\section*{{{name}}}", name)
        else:
            num, rest = name.split(" ", 1)
            pre = "\\setcounter{subsection}{-1}\n" if num == "5.0" else ""
            self.emit(rf"{pre}\subsection{{{rest.strip()}}}\label{{sec:{num}}}", name)

    def table(self, rows):
        raw = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        ncol = len(raw[0])
        raw = [r + [""] * (ncol - len(r)) for r in raw]
        cells = [[self.r.render(c) for c in row] for row in raw]
        env, spec, heavy = table_geometry(cells)
        inner = table_rows_latex(cells, spec, env, heavy)

        label, cap_raw = self.pending or ("", "")
        self.pending = None
        cap_raw, note_raw = split_caption(cap_raw)
        placement = TABLE_PLACEMENT.get(label)
        head = "\\begin{table}" + (f"[{placement}]" if placement else "") \
               + "\n\\centering\n"
        if not heavy:
            head += "\\small\n"
        if label:
            head += f"\\caption{{{self.r.render(cap_raw)}}}\n\\label{{{label}}}\n"
            _bump("table")
        if note_raw:
            # the note is not part of the caption: Elsevier wants it under the table
            head += inner + "\n\\smallskip\n{\\footnotesize " \
                    + self.r.render(note_raw) + "\\par}\n\\end{table}"
            _bump("tablenote")
            self.emit(head, f"table {label or '-'}")
            return
        self.emit(head + inner + "\n\\end{table}", f"table {label or '-'}")

    def para(self, para):
        m = re.match(r"^\*\*Table (S?\d+)\.\*\*\s*(.*)$", para, flags=re.S)
        if m:
            # the caption of the table that follows; it becomes a \caption
            # keep the raw text: table() splits it into caption and note and
            # renders each once.  Rendering here would render twice.
            self.pending = (f"tab:{m.group(1)}", m.group(2).strip())
            return
        m = re.match(r"^\*\*Figure (\d+)\.\*\*\s*(.*)$", para, flags=re.S)
        if m:
            self.figcaps[int(m.group(1))] = self.r.render(m.group(2).strip())
            return
        if para.startswith("**Keywords:**"):
            self.keywords = [k.strip() for k in
                             para.replace("**Keywords:**", "").split(";") if k.strip()]
            return
        self.emit(self.r.render(para), para)

    def flush_pending(self):
        if self.pending:
            _, cap = self.pending
            self.pending = None
            self.emit(cap, cap)


# --------------------------------------------------------------------------
def split_sections(md):
    parts = re.split(r"(?m)^## ", md)
    out = []
    for p in parts[1:]:
        name, _, body = p.partition("\n")
        out.append((name.strip(), body))
    return parts[0], dict(out), out


def build_main():
    md = MAIN_MD.read_text(encoding="utf-8")
    head, byname, ordered = split_sections(md)

    body_md = "## " + "\n## ".join(b + "\n" + t for b, t in ordered
                                   if re.match(r"\d+\. ", b))
    pointer = byname["Supplementary material"]
    refs = byname["References"]
    decl = byname["Declarations"]
    abcaps = byname["Figure captions"]

    body = Body(body_md, "main")
    body_tex = body.run()

    # The captions live in their own section, below the numbered text, so they
    # have to be parsed before the figure floats can be built.
    caps = Body("## Figure captions\n" + abcaps, "main")
    caps.run()

    def dummy(md_text):
        b = Body(md_text, "main")
        return b.run(), b

    # figures, each after the block that first cites it.  A block is searched in
    # two places, because neither alone is complete: the stored Markdown text
    # (which is what "Figure 6" is written as in the source) and the rendered
    # LaTeX (where it has become `\ref{fig:6}`).  The LaTeX matters for the
    # tables: a figure is sometimes first cited in a table note, and a table
    # block stores only the placeholder text "table tab:4".  Keying on the LaTeX
    # label alone is what an earlier version did, with `fig:6` looked up in
    # Markdown; it never matched, so every figure silently collected at the end.
    def cites_figure(k, n):
        text = body.chunks[k][0] if k < len(body.chunks) else ""
        if re.search(rf"(?<![\w.])Figures?\s+{n}\b(?!(?:\s*[--\u2013-]\s*\d))", text):
            return True
        latex = body.out[k] if k < len(body.out) else ""
        return bool(re.search(rf"\\ref\{{fig:{n}\}}(?!\s*[--\u2013-]\s*\\ref)", latex))

    def figure_tex(n):
        return ("\\begin{figure}[htbp]\n\\centering\n"
                f"\\includegraphics[width=\\linewidth]{{{FIGFILES[n]}}}\n"
                f"\\caption{{{caps.figcaps[n]}}}\n\\label{{fig:{n}}}\n\\end{{figure}}")

    anchors = []
    for n in sorted(caps.figcaps):
        hits = [k for k in range(len(body.out)) if cites_figure(k, n)]
        if not hits:
            print(f"  warning: figure {n} is never cited in the text; left at the end")
            anchors.append((len(body.out) - 1, n))
        else:
            anchors.append((hits[min(FIG_ANCHOR_SKIP.get(n, 0), len(hits) - 1)], n))
    for (i1, n1), (i2, n2) in zip(anchors, anchors[1:]):
        assert i1 <= i2, (f"figure anchors out of order: fig:{n1} at block {i1} precedes "
                          f"fig:{n2} at block {i2}, which would renumber the floats")
    inserts: dict[int, list[str]] = {}
    for idx, n in anchors:
        inserts.setdefault(idx, []).append(figure_tex(n))
    pieces = []
    for k, block in enumerate(body.out):
        pieces.append(block)
        pieces.extend(inserts.get(k, []))
    body_tex = "\n\n".join(pieces)

    decl_renderer = Renderer("main")
    decl_tex = declarations_latex("## " + decl, decl_renderer.render,
                              skip={"CRediT authorship contribution statement"})
    decl_tex = decl_tex.replace("\n\n", "\n\n", 1)
    # The section title must be re-emitted explicitly: `pointer` is the section
    # *body*, so prefixing it with "## " turned its first body line into the
    # heading and left an empty \section*{} in the PDF.
    ptr_tex, _ = dummy("## Supplementary material\n" + pointer)
    refs_body = Body("## " + refs, "main")
    refs_body.run()
    bib = ("\\begin{thebibliography}{00}\n" + "\n".join(refs_body.bibitems)
           + "\n\\end{thebibliography}")

    # abstract + keywords live ahead of the numbered sections
    pre = md[:md.index("## 1. Introduction")]
    ab = re.search(r"## Abstract\n\n(.*?)\n\n\*\*Keywords:", pre, flags=re.S)
    abstract = Renderer("main").render(ab.group(1).strip())
    kw = re.search(r"\*\*Keywords:\*\*\s*(.*)", pre)
    keywords = [k.strip() for k in kw.group(1).split(";") if k.strip()]
    title = re.match(r"# (.*)", md).group(1).strip()
    abbr = re.search(r"\*\*Abbreviations\.\*\*\s*(.*)", pre)
    abbrev = abbr.group(1).strip() if abbr else ""

    hl_md = pre[pre.index("## Highlights"):]
    bullets = [l.strip()[2:].strip() for l in hl_md.split("\n")
               if l.strip().startswith("- ")]
    HL_TEX.write_text(
        PREAMBLE + "\\begin{document}\n\\section*{Highlights}\n\\begin{itemize}\n"
        + "\n".join("  \\item " + Renderer("main").render(b) for b in bullets)
        + "\n\\end{itemize}\n\\end{document}\n", encoding="utf-8")

    abbr_tex = ""
    if abbrev:
        # Elsevier: define non-standard abbreviations in a first-page footnote.
        # In CAS this is a starred title note, so it needs a mark as well.
        abbr_tex = ("\\tnotemark[1]\n"
                    "\\tnotetext[1]{" + Renderer("main").render("Abbreviations. " + abbrev)
                    + "}\n")
    # Single-anonymized review: the author names, the affiliations and the
    # corresponding author's e-mail belong in the manuscript itself.  CAS has a
    # native ORCID field on \author, so the iDs go there rather than in a
    # footnote, and the CRediT roles go through \credit + \printcredits.
    credits = dict(credit_roles(decl))

    def credit_tex(name, indent="                  "):
        roles = credits.get(name)
        if not roles:
            return ""
        return indent + "\\credit{" + roles + "}\n"

    author_tex = (
        "\\author[a,b]{" + AUTHORS["first"] + "}"
        "[orcid=" + AUTHORS["first_orcid"] + ", ]\n"
        + credit_tex(AUTHORS["first"], "")
        + "\\author[a,b]{" + AUTHORS["corresponding"] + "}"
        "[orcid=" + AUTHORS["corresponding_orcid"] + ", ]\n"
        "\\cormark[1]\n"
        "\\ead{" + AUTHORS["email"] + "}\n"
        + credit_tex(AUTHORS["corresponding"], "")
        + affiliation_tex("a", AUTHORS["aff_a"]) + "\n"
        + affiliation_tex("b", AUTHORS["aff_b"]) + "\n"
        "\\cortext[1]{Corresponding author}\n"
    )
    # The template keeps research highlights in the manuscript; the standalone
    # highlights PDF is still written, because the submission system asks for it
    # as its own file.
    hl_tex = ""
    if bullets:
        hl_tex = ("\\begin{highlights}\n"
                  + "\n".join("\\item " + Renderer("main").render(b) for b in bullets)
                  + "\n\\end{highlights}\n\n")
    front = (
        PREAMBLE_CAS + PRELUDE_MAIN + "\\begin{document}\n\n"
        "\\shorttitle{" + AUTHORS["shorttitle"] + "}\n"
        "\\shortauthors{" + AUTHORS["shortauthors"] + "}\n\n"
        "\\title[mode=title]{" + title + "}\n\n"
        + abbr_tex
        + author_tex
        + "\\begin{abstract}\n" + wrap_tex(abstract) + "\n\\end{abstract}\n\n"
        + hl_tex
        + "\\begin{keywords}\n" + " \\sep ".join(keywords) + "\n\\end{keywords}\n\n"
        + "\\maketitle\n")
    # \printcredits prints the CRediT section from the \credit lists above, so
    # it stands where that section used to: first among the back matter.
    return (front + "\n" + body_tex + "\n\n" + "\\printcredits\n\n" + decl_tex
            + "\n\n" + ptr_tex + "\n\n" + bib + "\n\n\\end{document}\n")


def build_supp():
    md = SUPP_MD.read_text(encoding="utf-8")
    head, byname, ordered = split_sections(md)
    note = re.search(r"(?m)^> (?!$)(.*(?:\n> .*)*)", head)
    note_tex = ""
    if note:
        txt = re.sub(r"(?m)^> ?", "", note.group(0)).strip()
        note_tex = Renderer("supp").render(" ".join(txt.split("\n")))
    contents = byname.get("Contents", "")
    apx = "## " + "\n## ".join(b + "\n" + t for b, t in ordered if b.startswith("Appendix "))
    b = Body(contents if False else apx, "supp")
    apx_tex = b.run()
    contents_tex = Body("## Contents\n" + contents, "supp").run()
    return (PREAMBLE + PRELUDE_SUPP + "\\begin{document}\n\n\\begin{frontmatter}\n\n"
            "\\title{Supplementary material}\n"
            "\\begin{abstract}\n"
            "Appendices A--E of the manuscript, with the three tables they contain.\n"
            "\\end{abstract}\n\n\\end{frontmatter}\n\n"
            + "\\noindent " + note_tex + "\n\n"
            + contents_tex + "\n\n"
            + "\\appendix\n\n"
            # after \appendix the kernel renumbers tables as D.1, E.1, ...;
            # the manuscript refers to these two as Table S1 and Table S2
            + "\\renewcommand{\\thetable}{S\\arabic{table}}\n"
              "\\setcounter{table}{0}\n\n"
            + apx_tex + "\n\n\\end{document}\n")


if __name__ == "__main__":
    MAIN_TEX.write_text(build_main(), encoding="utf-8")
    SUPP_TEX.write_text(build_supp(), encoding="utf-8")
    for k in sorted(COUNT):
        print(f"  {COUNT[k]:4d}  {k}")
    print("wrote", MAIN_TEX.name, "|", SUPP_TEX.name, "|", HL_TEX.name)
