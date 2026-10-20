"""Build the wind deliverables from one reference database.

    python wind/_build/build.py

Inputs (this folder)
  wind_refs.py      reference database; entries with reuse=True take their metadata from sim2real/_build/refs.py
  report.src.md     feasibility report, citations written as [@key] or [@key1; @key2]

Outputs (wind/)
  Wind_Sim_Feasibility.md   the report with a numbered IEEE reference list
  references.md             the same numbers, with type, theme, a one-line note and access links
  references.bib            BibTeX for every cited reference (import into Zotero: File > Import)

IEEE and BibTeX formatting are imported from sim2real/_build/build.py, so both reviews cite the same way.
The build fails if a citation key is unknown, a {{placeholder}} is left, or a database entry is never cited.
"""
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
REPO = OUT.parent
sys.dont_write_bytecode = True

spec = importlib.util.spec_from_file_location('s2r_build', REPO / 'sim2real' / '_build' / 'build.py')
s2r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s2r)
sys.path.insert(0, str(HERE))
from wind_refs import REFS, THEMES  # noqa: E402

LIBKEY_LINK = 'https://libkey.io/libraries/545/{doi}'
KIND_LABEL = {**s2r.KIND_LABEL, 'R': 'Report or standard'}
KIND_SINGULAR = {'J': 'journal article', 'C': 'conference paper', 'CH': 'book chapter', 'B': 'book', 'P': 'preprint',
                 'D': 'documentation page', 'R': 'report or standard', 'W': 'software repository'}
KIND_PLURAL = {**s2r.KIND_PLURAL, 'R': 'reports and standards'}


def resolve(refs):
    out = []
    for r in refs:
        if r.get('reuse'):
            base = dict(s2r.BY_KEY[r['key']])
            base.update({k: v for k, v in r.items() if k != 'reuse'})
            r = base
        out.append(r)
    return out


BY_KEY = {r['key']: r for r in resolve(REFS)}
assert len(BY_KEY) == len(REFS), 'duplicate reference keys'


def ieee(r):
    """sim2real IEEE format; a report without a known address (e.g. a multi-agency user guide) omits it."""
    if r['kind'] == 'R' and not r.get('address'):
        return (f"{s2r.ieee_authors(r)}, {s2r._q(r['title'])} {r['institution']}, {r['rtype']}, {s2r._date(r)}. "
                f"[Online]. Available: {r['url']}")
    return s2r.ieee(r)


def bibtex(r):
    r = {f: v for f, v in r.items() if f not in ('why', 'theme')}
    if r['kind'] == 'R' and not r.get('address'):
        return '\n'.join(ln for ln in s2r.bibtex({**r, 'address': ''}).splitlines() if not ln.startswith('  address '))
    return s2r.bibtex(r)


def access_links_md(r):
    """sim2real links, plus LibKey 'Access Options' for articles the library resolves via its link resolver."""
    if r.get('libkey') and r['libkey'][1] == 'linkResolverOpenUrl':
        rest = s2r.access_links_md({k: v for k, v in r.items() if k != 'libkey'})
        return f"[\U0001F517 **Access Options**]({LIBKEY_LINK.format(doi=r['doi'])}) · " + rest
    return s2r.access_links_md(r)


class Numbering(s2r.Numbering):
    def number(self, key):
        if key not in BY_KEY:
            raise KeyError(f'unknown citation key: {key}')
        if key not in self.order:
            self.order.append(key)
        return self.order.index(key) + 1


def main():
    src = (HERE / 'report.src.md').read_text(encoding='utf-8')
    left = re.findall(r'\{\{[A-Z0-9_]+\}\}', src)
    if left:
        raise SystemExit(f'unfilled placeholders: {sorted(set(left))}')
    num = Numbering()
    body = num.sub(src, link=True)
    unused = [k for k in BY_KEY if k not in num.order]
    if unused:
        raise SystemExit(f'database entries never cited: {unused}')

    lines = ['', '## References', '',
             '*IEEE style, numbered in order of first citation. Journal articles were resolved through LibKey '
             '(Northeastern University Library); conference papers, chapters, books and reports were checked '
             'against Crossref or the publisher, preprints on arXiv. Access links, themes and BibTeX are in '
             '[references.md](references.md) and [references.bib](references.bib).*', '']
    for n, key in enumerate(num.order, 1):
        lines.append(f'<a id="ref-{n}"></a>[{n}] {s2r.md_inline(ieee(BY_KEY[key]))}  ')
    (OUT / 'Wind_Sim_Feasibility.md').write_text(body.rstrip() + '\n' + '\n'.join(lines) + '\n', encoding='utf-8')

    counts = {}
    for k in num.order:
        counts[BY_KEY[k]['kind']] = counts.get(BY_KEY[k]['kind'], 0) + 1
    summary = ', '.join(f'{v} {(KIND_PLURAL if v > 1 else KIND_SINGULAR)[k]}'
                        for k, v in sorted(counts.items(), key=lambda x: -x[1]))
    reused = sum(1 for r in REFS if r.get('reuse'))
    out = ['# Wind + drone reference list', '',
           f'{len(num.order)} references, numbered as in [Wind_Sim_Feasibility.md](Wind_Sim_Feasibility.md) '
           f'(IEEE style, order of first citation). Breakdown: {summary}. {reused} entries are shared with '
           '[../sim2real/references.md](../sim2real/references.md) and keep the same citation keys.', '',
           '- **Verification (2026-10-19).** Every journal article was resolved through LibKey (Northeastern '
           'University Library): \U0001F4C4 opens the library PDF, \U0001F517 *View Article* the article page, '
           '\U0001F517 *Access Options* the library link resolver (sign-in may be required). Conference papers, '
           'chapters, books and reports were checked on Crossref or the publisher; preprints on arXiv.',
           '- **Peer review.** *Preprint* entries had not completed peer review when checked; *Documentation* '
           'entries describe software behaviour, not research results.',
           '- **Themes.** ' + '; '.join(f'**{k}** {v}' for k, v in THEMES.items()) + '.',
           '- **Citation manager.** Import [references.bib](references.bib) into Zotero with *File → Import…* '
           '(e.g. into a *DroneRanger wind* collection) and pick the IEEE style.',
           '- **Local copies.** Open-access PDFs and saved documentation pages are in the git-ignored '
           '`reference/08_wind_simulation/` folder (see its `NOTES.md`).', '']
    for n, key in enumerate(num.order, 1):
        r = BY_KEY[key]
        out.append(f'**[{n}]** {s2r.md_inline(ieee(r))}  ')
        links = access_links_md(r) or 'no DOI'
        out.append(f'*{KIND_LABEL[r["kind"]]}* · {r.get("theme", "")} · `{key}` · {links}  ')
        if r.get('why'):
            out.append(f'{r["why"]}')
        out.append('')
    (OUT / 'references.md').write_text('\n'.join(out), encoding='utf-8')

    header = ('% Wind + drone references (DroneRanger), all cited references, in citation order.\n'
              '% Generated by _build/build.py from _build/wind_refs.py. Import into Zotero: File > Import.')
    body = '\n\n'.join(bibtex(BY_KEY[key]) for key in num.order)
    (OUT / 'references.bib').write_text(header + '\n\n' + body + '\n', encoding='utf-8')
    without = [k for k in num.order if BY_KEY[k]['kind'] == 'J' and not BY_KEY[k].get('libkey')]
    print(f'built {len(num.order)} references ({summary}); report and lists written to {OUT}')
    if without:
        print('WARNING: journal articles without LibKey resolution:', without)


if __name__ == '__main__':
    main()
