# wind: simulation + real wind for DroneRanger

Research notes for DroneRanger (CS 7980 capstone, hardware group, Fall 2026). The study asks whether a simulator (Isaac
Sim + Pegasus, or Gazebo + PX4 SITL) can fly a scripted PX4 mission while replaying *real* San Jose wind, and what the
literature says about wind and small multirotors.

**Verdict:** practical. Data, wind model and simulator replay all ran on a laptop on 2026-10-19. The recommended first
platform is Gazebo (gz) + PX4 SITL. Isaac Sim + Pegasus is the second step and needs a ≥ 16 GB RTX GPU. Start with
the summary of the report.

| File | What it is |
|---|---|
| [Wind_Sim_Feasibility.md](Wind_Sim_Feasibility.md) | The report: pipeline verdict, the legacy stack, San Jose wind data, airport-to-garden wind model and its validation, simulator options (source-verified), end-to-end RotorPy check, literature review (7 themes), plan and risks |
| [references.md](references.md) | 89 references, numbered as in the report, with type, theme, a one-line note and access links (LibKey / DOI / arXiv) |
| [references.bib](references.bib) | BibTeX for all 89 references |
| [data/](data/) | Small results: `sj_wind_summary.md` (flight-hour wind statistics), `sjc_1min_diurnal.csv`, `turbulence_validation.csv`, `rotorpy_demo_results.csv` |
| [figures/](figures/) | `sjc_diurnal.png`, `rotorpy_demo.png` |
| [tools/](tools/) | The scripts below |
| [isaac_pegasus/](isaac_pegasus/) | This week's pipeline: Isaac Sim 5.1 + Pegasus 5.1 + PX4 SITL v1.14.3 on Explorer HPC, with a wind publisher (dummy-wind smoke test). Start at its README |
| [_build/](_build/) | `wind_refs.py` (reference database), `report.src.md` (report text with `[@key]` citations), `build.py` |

## Tools

Python 3 with `pandas`, `numpy`, `scipy`, `requests` and `matplotlib`. The demo also needs `pip install rotorpy`.
Raw data and generated wind profiles go to the git-ignored `reference/08_wind_simulation/data/`.

```
python wind/tools/fetch_wind.py --start 2026-07-01 --end 2026-10-18        # SJC 1-min + METAR + Open-Meteo
python wind/tools/wind_stats.py                                             # -> wind/data/sj_wind_summary.md
python wind/tools/make_wind_profile.py --start "2025-11-07 15:30" --alt 5 --turb data   # replayable 50 Hz series
python wind/tools/validate_turbulence.py                                    # Dryden vs measured gusts
python wind/tools/rotorpy_wind_demo.py reference/08_wind_simulation/data/profiles/<profile>.csv
python wind/tools/make_figures.py
```

`make_wind_profile.py` options that matter:
- `--alt`: flight height.
- `--z0-site`: garden roughness.
- `--height-factor`: a measured garden/SJC ratio, which replaces the log-law estimate.
- `--turb mil|data|none`: turbulence model.
- `--ti-scale`: sensitivity sweeps.

The output CSV is ENU, velocity of the air, in m/s. PX4 NED is (n, e, −u).

## Citation management (Zotero)

1. Create a collection, e.g. *DroneRanger wind*.
2. Choose *File → Import… → A file* and select `references.bib`.
3. Pick **IEEE** under *Edit → Settings → Cite → Styles*.

Nineteen entries share their keys with `../sim2real/references.bib`, so importing both into one library gives duplicates
that Zotero can merge.

## Rebuilding

After editing `_build/wind_refs.py` or `_build/report.src.md`:

```
python wind/_build/build.py
```

The script imports the IEEE and BibTeX formatters from `sim2real/_build/build.py`, so both reviews cite the same way.
Entries marked `reuse=True` take their metadata from `sim2real/_build/refs.py`. The build fails if:
- a citation key is unknown;
- a `{{placeholder}}` is left;
- a database entry is never cited.

## Verification

All references were checked on 2026-10-19:
- **Journal articles** were resolved through LibKey (Northeastern University Library).
- **Conference papers, chapters, books and reports** were checked on Crossref, PMLR, NTRS or the publisher.
- **Preprints** were checked on arXiv.
- **Documentation and software claims** were checked in source code at a named tag or branch.

Copies of the sources (30 documentation and source pages, 23 open-access PDFs) and the "not verified" notes are in
`reference/08_wind_simulation/NOTES.md`.
