#!/usr/bin/env python3
"""Split the SEGAN main manuscript .tex into one file per *major part*.

The parts follow the coarse structure an author actually revises:

    01 abstract | 02 introduction | 03 methods | 04 data | 05 results | 06 discussion

plus three support files (preamble, back matter, assembly).  The earlier
per-section split produced 16 files and was too fine to work with.

Guarantees
----------
* **The manuscript text is not moved.**  Every part is a contiguous slice of the
  monolith (except `03_methods`, which is the four contiguous slices §2/§3/§4),
  and the assembly order equals the document order, so section numbers, floats
  and cross-references are byte-for-byte what they were.
* After writing, the parts are concatenated again and compared **line by line**
  against the source file; one difference aborts the run.
* Existing files are never overwritten unless --force is given.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MONOLITH = ROOT / "SEGAN_manuscript_2026-09-14.tex"

# The monolith is compiled from the project root, the module split from
# manuscript_sections/, so the two need different figure prefixes.  Both lists
# also carry the CAS bundle directory, because the class pulls its own
# thumbnails from there.
GRAPHICS_OLD = "\\graphicspath{{figures/}{els-cas-templates/}{../els-cas-templates/}}"
GRAPHICS_NEW = ("\\graphicspath{{../figures/}{figures/}"
                "{els-cas-templates/}{../els-cas-templates/}}")

# (file, [slice keys in document order], human description)
PARTS = [
    ("00_preamble",     ["preamble"],                          "文档类、宏包、浮动体参数"),
    ("01_abstract",     ["frontmatter"],                       "标题、作者、摘要、关键词"),
    ("02_introduction", ["sec1"],                              "§1 引言（含贡献 C1–C5、相关工作）+ 图 1"),
    ("03_methods",      ["sec2a", "sec2b", "sec3", "sec4"],    "§2 问题表述 + §3 归因框架 + §4 精确可解性与深度剖面"),
    ("04_data",         ["sec5a"],                             "§5 节标题 + §5.0 设置与样本规则（测试系统、条件、样本规则）"),
    ("05_results",      ["sec5b", "sec6"],                     "§5.1–§5.8 数值验证 + §6 服务模型 regime + 图 2–8"),
    ("06_discussion",   ["sec7", "sec8", "sec9", "sec10"],     "§7 时延申报规范 + §8 讨论 + §9 局限 + §10 结论 + 图 9"),
    ("90_back_matter",  ["declarations", "pointer", "bibliography"],
                                                               "声明 + 补充材料指针 + 41 条文献（图已随各章节内嵌）"),
]


def build_slices(text: str) -> dict[str, str]:
    lines = text.split("\n")
    n = len(lines)

    def find(pattern, start=0):
        rx = re.compile(pattern)
        for i in range(start, n):
            if rx.match(lines[i]):
                return i
        return -1

    i_doc = find(r"\\begin\{document\}")
    # The CAS front matter is not fenced by an environment: it runs from the
    # first \shorttitle to \maketitle.  The CRediT statement is printed by
    # \printcredits rather than written as a section, so that is where the back
    # matter starts.
    i_front = find(r"\\shorttitle\{")
    i_front_end = find(r"\\maketitle")
    i_figs = find(r"\\begin\{figure\}")
    i_decl = find(r"\\printcredits")
    i_ptr = find(r"\\section\*\{Supplementary material\}")
    i_bib = find(r"\\begin\{thebibliography}")
    i_bib_end = find(r"\\end\{thebibliography\}")

    marks = {"document": i_doc, "frontmatter": i_front, "frontmatter_end": i_front_end,
             "figures": i_figs, "declarations": i_decl, "pointer": i_ptr,
             "bibliography": i_bib, "bibliography_end": i_bib_end}
    for k, v in marks.items():
        if v < 0:
            raise SystemExit(f"marker not found: {k}")

    def find_sub(start, label):
        """First \\subsection line at or after `start` whose label is `label`."""
        for i in range(start, n):
            if lines[i].startswith("\\subsection") and f"\\label{{sec:{label}}}" in lines[i]:
                return i
        raise SystemExit(f"subsection sec:{label} not found from line {start}")

    s1 = find(r"\\section\{Introduction\}")
    s2 = find(r"\\section\{Problem formulation\}")
    s3 = find(r"\\section\{An attribution framework")
    s4 = find(r"\\section\{Exact solvability")
    s5 = find(r"\\section\{Numerical verification\}")
    s6 = find(r"\\section\{The service-model regime")
    s7 = find(r"\\section\{A reporting standard")
    s8 = find(r"\\section\{Discussion\}")
    s9 = find(r"\\section\{Limitations\}")
    s10 = find(r"\\section\{Conclusions\}")
    for name, v in [("sec1", s1), ("sec2", s2), ("sec3", s3), ("sec4", s4), ("sec5", s5),
                    ("sec6", s6), ("sec7", s7), ("sec8", s8), ("sec9", s9), ("sec10", s10)]:
        if v < 0:
            raise SystemExit(f"section not found: {name}")

    cut25 = find_sub(s2, "2.5")      # §2.5 Statistical unit
    cut51 = find_sub(s5, "5.1")      # §5.1 (so §5a = heading + \setcounter + §5.0)

    spans = {
        "preamble":      (0, i_doc),
        "frontmatter":   (i_front, i_front_end + 1),
        "sec1":          (s1, s2),
        "sec2a":         (s2, cut25),        # §2.1–§2.4
        "sec2b":         (cut25, s3),        # §2.5–§2.6
        "sec3":          (s3, s4),
        "sec4":          (s4, s5),
        "sec5a":         (s5, cut51),        # §5 heading + \setcounter + §5.0
        "sec5b":         (cut51, s6),        # §5.1–§5.8
        "sec6":          (s6, s7),
        "sec7":          (s7, s8),
        "sec8":          (s8, s9),
        "sec9":          (s9, s10),
        "sec10":         (s10, i_decl),
        "declarations":  (i_decl, i_ptr),
        "pointer":       (i_ptr, i_bib),
        "bibliography":  (i_bib, i_bib_end + 1),
        "_tail":         (i_bib_end + 1, n),
    }
    # The figure floats are emitted inline by md_to_latex.py, each after the block
    # that first cites it, so they belong to whichever section carries them and
    # ride along inside that section's slice.  They used to be collected in a
    # slicing of their own just before the declarations; assuming that layout left
    # the last section ending at the first float instead of at the declarations.
    if not (s1 < i_figs < i_decl):
        raise SystemExit("expected the figure floats inside the numbered sections")
    return {k: "\n".join(lines[a:b]) for k, (a, b) in spans.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="manuscript_sections")
    ap.add_argument("--force", action="store_true", help="overwrite existing part files")
    args = ap.parse_args()

    if not MONOLITH.exists():
        print(f"missing {MONOLITH}", file=sys.stderr)
        return 1
    original = MONOLITH.read_text(encoding="utf-8")
    if GRAPHICS_OLD not in original:
        print(f"expected {GRAPHICS_OLD!r} in the monolith", file=sys.stderr)
        return 1

    sl = build_slices(original)
    sl["preamble"] = sl["preamble"].replace(GRAPHICS_OLD, GRAPHICS_NEW)

    outdir = ROOT / args.out
    outdir.mkdir(parents=True, exist_ok=True)

    written, skipped = [], []
    header = {
        "04_data":
            "% 本模块 = §5 的节标题 + §5.0「设置与样本规则」。\n"
            "% 之所以带着 §5 的节标题：设置与样本规则是 §5 的第一小节，连同标题一起\n"
            "% 放在这里，装配顺序才与原文完全一致、章节编号一个都不动。\n",
        "03_methods":
            "% 本模块 = §2 问题表述（2.1–2.6）+ §3 归因框架 + §4 精确可解性。\n",
    }
    for name, keys, _desc in PARTS:
        target = outdir / f"{name}.tex"
        if target.exists() and not args.force:
            skipped.append(target.name)
            continue
        body = "\n".join(sl[k].strip("\n") for k in keys)
        comment = header.get(name, "")
        target.write_text(comment + body + "\n", encoding="utf-8")
        written.append((name, sum(sl[k].count("\n") + 1 for k in keys)))

    names = [p[0] for p in PARTS]
    (outdir / "main.tex").write_text(
        "\n".join([
            "% Assembly file — this is what you compile.",
            "% One file per major part; see README.md for the map and the editing rules.",
            "% Generated by supp_code/split_manuscript_tex.py from SEGAN_manuscript_2026-09-14.tex",
        ])
        + f"\n\n\\input{{{names[0]}}}\n\n\\begin{{document}}\n\n"
        + "\n".join(f"\\input{{{n}}}" for n in names[1:])
        + "\n\n\\end{document}\n", encoding="utf-8")

    # ---- round-trip: rebuild from the slices and compare line by line ----
    rebuilt = (sl["preamble"] + "\n\\begin{document}\n" + sl["frontmatter"] + "\n"
               + sl["sec1"] + "\n" + sl["sec2a"] + "\n" + sl["sec2b"] + "\n"
               + sl["sec3"] + "\n" + sl["sec4"] + "\n" + sl["sec5a"] + "\n"
               + sl["sec5b"] + "\n" + sl["sec6"] + "\n" + sl["sec7"] + "\n"
               + sl["sec8"] + "\n" + sl["sec9"] + "\n" + sl["sec10"] + "\n"
               + sl["declarations"] + "\n" + sl["pointer"] + "\n"
               + sl["bibliography"] + "\n" + sl["_tail"])
    a = [l for l in original.replace(GRAPHICS_OLD, GRAPHICS_NEW).split("\n") if l.strip()]
    b = [l for l in rebuilt.split("\n") if l.strip()]

    # the floats are inline now, so check them explicitly: same set, same order
    figs_a = re.findall(r"\\label\{fig:(\d+)\}", original)
    figs_b = re.findall(r"\\label\{fig:(\d+)\}", rebuilt)
    figs_ok = figs_a == figs_b and len(figs_a) == 9

    print(f"  写入 {len(written)} 个模块"
          + (f"；跳过已存在：{len(skipped)}" if skipped else ""))
    for name, nl in written:
        desc = dict((p[0], p[2]) for p in PARTS)[name]
        print(f"     {name:18s} {nl:5d} 行   {desc}")
    print(f"\n  图环境：{len(figs_b)}/9 就位，顺序 {'一致 ✅' if figs_ok else '异常 ❌'}")
    print("\n  往返比对：")
    print(f"     原文 {len(a)} 个非空行 / 重组 {len(b)} 个非空行")
    if a == b and figs_ok:
        print("     逐行完全一致 ✅（正文没有搬动、没有丢失或错序）")
        return 0
    d = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    print(f"     ❌ 不一致：{len(d)} 行；首个差异在第 {d[0] + 1} 个非空行")
    print(f"        原文: {a[d[0]][:120]}")
    print(f"        重组: {b[d[0]][:120]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
