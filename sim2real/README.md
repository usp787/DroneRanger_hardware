# sim2real: literature review on simulation-to-reality transfer

Research notes for DroneRanger (CS 7980 capstone, hardware group, Fall 2026). The review asks three questions:

1. How far has sim-to-real transfer come?
2. What are its latest challenges?
3. What do they mean for DroneRanger?

| File | What it is |
|---|---|
| [Sim2Real_Literature_Review_Comprehensive.md](Sim2Real_Literature_Review_Comprehensive.md) | The full review (≈10,000 words, 155 references). It opens with an executive summary, then covers Q1 (progress), Q2 (latest challenges) and Q3 (DroneRanger: gap audit, lessons, risk register, sim-vs-real test protocol). |
| [DroneRanger_Sim2Real_Literature_Review_Brief.docx](DroneRanger_Sim2Real_Literature_Review_Brief.docx) | The brief version for Canvas: DroneRanger-focused, IEEE style, 8 journal articles, 4 conference papers and 1 book, each with a short paragraph. Export it to PDF from Word (*File → Save As → PDF*). |
| [references.md](references.md) | The reference list, numbered as in the comprehensive review. Each entry shows its type, peer-review status and access links (LibKey / DOI / arXiv). ★ marks the entries used in the brief. |
| [references.bib](references.bib) | BibTeX for all 155 references. |
| [references_brief.bib](references_brief.bib) | BibTeX for the brief's 14 references only. |
| [_build/](_build/) | Sources and generator: `refs.py` (reference database), `part0…part5_*.src.md` (review text with `[@key]` citations), `brief.py` (brief text), `build.py`. |

## Citation management (Zotero)

The brief's references are kept in BibTeX. To load them into Zotero:
1. Create a collection, e.g. *DroneRanger sim2real*.
2. Choose *File → Import… → A file*, select `references_brief.bib` (or `references.bib` for everything), and import it into that collection.
3. Choose **IEEE** under *Edit → Settings → Cite → Styles* to produce the same bibliography format.

## Rebuilding

After editing `_build/refs.py`, any `_build/part*.src.md` or `_build/brief.py`, run:

```
python sim2real/_build/build.py
```

You need Python 3 with `python-docx`. The script:
- renumbers citations in order of first appearance (IEEE);
- rewrites every output file listed above;
- fails if a citation key is unknown or a `{{placeholder}}` is left in the text;
- checks that the brief still has at least 6 journal articles, 2 conference papers and 1 book.

## Verification

All references were checked on 2026-10-11:
- **Journal articles** were resolved through LibKey (Northeastern University Library).
- **Conference papers, chapters and books** were checked against Crossref, because LibKey does not index them.
- **PMLR papers** were checked on proceedings.mlr.press, and **preprints** on arXiv.

Preprints, vendor documentation and internal project documents are labelled as such in `references.md`.
