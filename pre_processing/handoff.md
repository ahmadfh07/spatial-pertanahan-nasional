# Handoff: desa.xlsx analysis

_Last updated: 2026-11-26 (after prompt 16)_

**Standing instruction:** write this file ONLY when the user asks (stated in prompt 9; asked again in prompts 12 and 16).
**Language:** the user mostly writes English but wrote one message in Indonesian ("Lanjutkan"). Reply in the language the user writes; keep the notebook, handoff and deliverable files in English.
**Audience note:** this file is the internal working log. It is NOT meant for the user's teammates (see "Handing over to teammates").

## Project context
- Source: `/mnt/project/desa.xlsx` (15 MB, 1 sheet `desa`). Read-only.
- Content: land parcel / land-rights summary per village (desa / kelurahan) in Indonesia, with flood-hazard and RDTR (detailed spatial plan) area columns.
- **Goal: produce clustering-ready data plus the documented decisions behind it. The user's group does the modelling (algorithms, k, validation); do not do that part.** The group will continue with their own AI assistants.
- User works in `master.ipynb` (kernel `ds-ugm`, Python 3.11). Loader puts the data in `rawDesa`; expects `./data/desa.xlsx`. **Deliver code as continuation cells appended to master.ipynb; the user runs them himself.** New cells carry no saved outputs.
- Sandbox facts:
  - No Jupyter/nbformat: test with a custom cell runner. **The sandbox workspace (`/home/claude/...`) is wiped between turns; only `/mnt/user-data/outputs` persists.** The delivered `master.ipynb` is the source of truth: to change cells, patch the notebook JSON directly and rebuild the small runner + a pickle cache of `rawDesa` (the Excel read takes ~22-26 s).
  - Python 3.12 / pandas 3.0.6 in the sandbox (user's pandas unknown): write version-safe code.
  - Packages: Step 4 needs only numpy, pandas, matplotlib. Earlier steps (3e, 3b-9) use `Series.corr(method="spearman")`, which needs scipy through pandas. Cramer's V, Spearman-on-ranks and PCA-by-SVD are hand-written.
  - Lesson learned: check cell OUTPUTS and execute documented snippets, not just "no error" (six issues were caught that way, see "Caught during the build").

## Data snapshot
- 79,842 rows x 33 columns. Grain: one row per village. `kode` unique. Snapshot computed 2026-10-17 (`dihitung_pada`), not a time series.
- Hierarchy: provinsi (34, pre-2022 Papua boundaries) > kabupaten > kecamatan > village. `tipe`: Desa 64,223 / Kelurahan 15,619.
- `kode`: Excel stores it as a number, so the leading zero is lost in the file; reading as string still gives 7 digits. Always `zfill(8)` (PP KK CC DD); the notebook builds `kode8`.

| Group | Columns |
|---|---|
| ID | `kode` |
| Text | `nama`, `tipe`, `kecamatan`, `kabupaten`, `provinsi` |
| Metrics (23) | `luas_desa`, `jumlah_persil`, `luas_persil`, 8 rights x (`_jumlah`, `_luas`): hak_milik, hgb, hgu, hak_pakai, hak_pengelolaan, hak_wakaf, kosong, lainnya; `rdtr_luas`; `banjir_rendah/sedang/tinggi` |
| Temporal | `tahun_min/median/max` (float), `dihitung_pada` |

## Progress log
- **P1 basic EDA (DONE).** **P2 plan for inferring relations (DONE).** **P3 Steps 1-3 (DONE):** structural relations, size-neutral features, robust prep.
- **P4 kode as string (DONE, no change).** Excel cells are numeric; `dtype={"kode":"string"}` gives 7 chars. Loader bug: `dtype={"id":...}` names a non-existent column.
- **P5 goal shift to clustering (DONE, discussion).** **P6 anomaly handling (DONE, discussion).** **P7 "done in steps 1-3?" (DONE).** **P8 Step 3b anomaly audit (DONE, 12 cells).**
- **P9 tenure-only vs everything (DONE, discussion).** Recommendation: tenure-only as primary run, extended variant afterwards for comparison.
- **P10 "is the data clustering-ready?" (DONE).** No: no model matrix yet (1,950 villages undefined in 11 features, zero shares block CLR, redundant columns, mixed scales).
- **P11 steps 4-8 vs new work (DONE, discussion).** Old steps 4-8 (relation inference) are replaced by a data-preparation plan; modelling belongs to the user's group.
- **P12/13 Step 4 clustering-ready data implemented (DONE).** 13 cells appended -> 50 cells; 40 code cells ran clean in ~40 s.
- **P14 "handoff.md vs a README inside clustering_ready for teammates?" (DONE, discussion).** Answer: put the guidance in a README inside the folder (it travels with the data); do not hand teammates this file (internal process notes and standing instructions an AI might mis-follow); give them a trimmed background document instead.
- **P15 hand-off documents implemented (DONE).** New cell 4-11 writes a rich `README.md` and a new `BACKGROUND.md` from the notebook's own variables; cell 4-10 no longer writes the short README. Notebook now has **51 cells (41 code)**. Versus the previously delivered notebook: 3 cells changed (the comment in 4-4, cell 4-10, the closing markdown), 1 added (4-11), 0 removed.
- **P16 update this file (DONE).**

### Notebook map (cells after the user's 5)
1. **Step 1 structural relations** -> `desa`, `kode8`, rule book, hierarchy checks, `*_n` normalized names.
2. **Step 2 features** -> `FEATURE_GROUPS`, helpers `safe_div`, `add_cols`.
3. **Step 3 robust prep** -> flags, `analysis_ok`, `RATIO_CAP=10`, `has_*`, `*_log10`, `desaOK`.
4. **Step 3b anomaly audit** -> `anomalies`, `conc`, `flood_suspect_kab`, `share_explained`, `parcel_status`, `kab_key`, `excluded`, `sens`/`delta`.
5. **Step 4 clustering-ready data:**
   - 4-1 parameters (`RARE_AREA_SHARE=0.01`, `SAMPLE_N=1500`, `SEED=42`, `EXPORT=True`, `EXPORT_DIR=DATA/"clustering_ready"`) + `roles_df`
   - 4-2 redundancy checks; 4-3 rare-rights grouping (`GROUPED`, `KEPT`); 4-4 transform -> `T`, `COLS`, `FIT`; 4-5 `place_later` + `summary`
   - 4-6 scaling -> `RECIPE`, `apply_recipe`, `X_A`, `X_A_scaled`, `X_B`, `X_B_scaled`; 4-7 evidence -> `evidence`, `EVID`, `schemes`, `comp_share`
   - 4-8 readiness checks (asserts); 4-8b histograms + PCA (`explained`); 4-9 decision log D1-D14
   - 4-10 package + export of the data files -> `village_ids`, `interp`, `recipe_json`, `deliverables`
   - **4-11 (new)** writes `README.md` and `BACKGROUND.md`, then checks that every file the README lists exists
   - Requires earlier sections to be run (uses `excluded`, `delta`, `anomalies`, `sens`, `flood_suspect_kab`, `share_explained`, `RATIO_CAP`, `ZERO_THRESH`, `STRAY_MAX`, `REF_YEAR`, `DATA`).

### Export (written by 4-10 and 4-11 when `EXPORT = True`, ~48 MB, folder `data/clustering_ready/`, 12 files)
`X_A.csv`, `X_A_scaled.csv`, `X_B.csv`, `X_B_scaled.csv` (index `kode8`); `village_ids.csv`; `interpretation_columns.csv` (33 cols); `place_later.csv` (2,744 rows, 20 cols); `excluded_rows.csv` (122); `decision_log.csv` (14); `transform_recipe.json`; `README.md`; `BACKGROUND.md`. Verified: `kode8` keeps its leading zero (read as text), ids line up across files, X_A_scaled can be rebuilt from X_A + recipe (diff ~1e-5 from the 6-significant-digit CSV rounding). **Modellers must read `kode8` as text.**
Preview copies of the two documents (from the sandbox test run) are in `/mnt/user-data/outputs/clustering_ready_preview/`; the user gets the real ones by running the notebook.

## Handing over to teammates
- Give them the whole `clustering_ready/` folder. `README.md` is the entry point. It has: status, file table, a quick-start (executed and verified against the exported files), the input columns, six rules, a `place_later` handling table, decisions already made (from the log), decisions the group still has to make (with measured evidence), caveats, next steps for modelling, a glossary, and a section written for AI assistants (read the README / decision log / recipe first, do not redo preprocessing, keep `kode8` as text, no interpretation columns as inputs, do not call clusters real before stability checks, do not read flood differences as hazard evidence, log any change as a new decision D15+).
- `BACKGROUND.md` is the trimmed history: dataset, data-quality findings and treatments (plain-language table), structural facts, early findings, pipeline in one page, unresolved questions, how to reproduce. If it conflicts with the README or `decision_log.csv`, those win.
- Do NOT hand over this `handoff.md`. The two documents are generated by cell 4-11: change the cell and rerun, do not edit the files by hand (a rerun only changes the "Created" timestamp).

## Verified results (Step 4)
- **Inputs.** Variant A (default, 8 columns): `s_hak_milik`, `s_hgb`, `s_hgu`, `s_hak_pakai`, `s_kosong`, `s_other` (sqrt of area shares) + `log_parcel_density`, `log_mean_parcel`. Variant B (10 columns) adds `log_luas_desa` and `log1p_age_median`. Flood, RDTR, years, geography, `tipe` = interpretation only.
- **Fit sets:** A = 77,770 villages; B = 77,098. `place_later` = 2,744 = 122 excluded in Step 3 + 1,950 no-parcel villages + 672 B-only (666 untitled-only + 6 titled with null year). Reconciles exactly to 79,842.
- **Coverage is NOT a third input:** `log10(density) + log10(mean parcel size) = log10(coverage) + 4` holds to 1e-15 (SVD smallest singular value 0.000). Titled share = 1 - kosong share exactly.
- **Rare rights:** rule = area share < 1% -> pengelolaan 0.47%, wakaf 0.05%, lainnya 0.00% grouped into `other`. HGB (1.17%) and hak_pakai (1.76%) kept; HGU kept (16.8% of area, present in only 6% of villages). Wakaf is present in 46% of villages: grouped because tiny by area, not rare by presence.
- **Evidence (distance-structure rank correlation vs default, 1,500 villages, seed 42):** raw shares 0.945; CLR 0.704 / 0.780 / 0.668 for zero replacement 1e-4 / 1e-3 / 1e-2, two CLR variants vs each other **0.558**; ungrouped vs grouped rights **1.000**; parcel-count shares instead of area **0.621**; scaling: z-score every column 0.934 (composition 75.0% of variance), each concept once 0.894 (31.9%), blocks equal 0.971 (50.0%), no scaling 0.762 (15.7%), default composition 70.1% (5 degrees of freedom = 6 parts - 1; factor 4.44 for A, 4.482 for B); B vs A 0.905; composition block alone vs A 0.921.
- **Readiness:** 0 NaN / inf / constant columns / duplicate ids in all four matrices; 0 exact duplicate rows; no input pair with |Spearman| >= 0.9. `age_median` raw skew 2.01 (1,523 villages beyond 5 robust SD) -> log1p skew -0.23, 0 beyond.
- **PCA (variant A, scaled):** PC1 39.7%, PC2 28.0%, PC1-4 88.7%; a **continuous cloud with two dense regions, not clearly separated groups.** Cluster-tendency tests belong to the modelling step.
- **README quick-start executed:** X (77,770 x 8), village_ids (79,842 x 7), interpretation_columns (79,842 x 33), place_later (2,744 x 20).
- **Re-run safety:** matrices, decision log and BACKGROUND identical on a second run; README differs only in the "Created" timestamp.

## Corrections to earlier statements (read these before trusting older text)
1. **`place_later` is NOT "assign to the nearest cluster afterwards".** That advice (P6 principle "fit on the clean core, then assign the rest", the old clustering-plan step C7, an earlier TODO line) is superseded. For variant A nobody in `place_later` is genuinely assignable: **1,950 no-parcel villages** have no tenure profile (report as their own group); **122 excluded rows** have unreliable areas (do not assign); **672 B-only villages** (no registration year) are already in `X_A` (for variant B they can be scored on the A columns). A first snippet returned 748 "assignable" rows: 672 already in `X_A` + 76 excluded rows with unreliable values.
2. **Coverage was listed as a clustering input in the earlier plan: it is not** (exact function of density and mean parcel size).
3. **"Three rarest rights" was loose wording:** the rule is area share < 1% (wakaf is in 46% of villages).
4. **The sqrt of the shares makes Euclidean distance proportional to (not equal to) the Hellinger distance.** Fixed in the notebook comment, README and docs.
5. **Package list:** "numpy/pandas/matplotlib only" holds for Step 4 only; earlier steps need scipy via pandas (stated in README and BACKGROUND).

### Caught during the build (fixed)
1. SVD rank demo centred by median (smallest singular value 43.6 instead of ~0); identity is linear only after mean-centring.
2. Loop variable `delta` in 4-7 overwrote the Step 3b-9 table `delta`, silently breaking decision D10's evidence; renamed `repl`.
3. `age_median` heavy tail found by the readiness table; handled with log1p (D14).
4. First README draft told modellers to assign `place_later` villages; executing the snippet showed there is nothing to assign for variant A (see correction 1).
5. Wrong "equal to Hellinger" wording (correction 4).
6. Package list understated (correction 5).

## Earlier verified findings (still valid)
- Structural relations all hold (8 rights sum to totals; count==0 <=> area==0 except 6 `kosong` rows; flood/RDTR <= village area; year present => titled parcel). Soft rule `luas_persil <= luas_desa` violated in 11,009 rows (13.8%).
- `prov_code` matches `provinsi` except 17 rows; 10 `kab_code`s are shared by two names (regency splits, hypothesis); `kab_key` gives 506 keys, 26 names still have >1 key (Kab. Bogor split over 1010/1033 is a known limit).
- Anomalies (Step 3b): 122 rows excluded (2 pseudo-records incl. kode 33000000 "HGU" and kode 16030000 whose `nama`/`kecamatan` were "-" turned into NaN by the user's SENTINELS; 46 zero area; 74 area ratio > 10). Ratio outliers are scattered, mostly `kosong`, and the parcel side is the likely inflated one (67 of 74). Zero village area concentrated in Bengkulu (22 of 46). No-parcel villages (top provinces Papua Barat 344, NTT 296, Sumut 295, Papua 283): 53% flood-zero (vs 22%), 4% RDTR (vs 17%): looks like a regional coverage gap (hypothesis).
- Flood zeros are strongly regional (kabupaten explains 28% of variance, province 11%); 11 suspect kabupaten, mostly highland/volcanic/small-island so real zeros are plausible; unresolved without the data owner or an elevation layer. Flood stays interpretation-only.
- Spearman `luas_desa ~ jumlah_persil` is ~0 in every scenario (-0.019 to 0.042): parcel count is nearly independent of village area. Medians/ranks are robust to exclusion choices; means, sums and Pearson are not.
- User's cell 2 still looks for a leftover `anggota.csv`; cell 3 `dtype={"id":...}` is a no-op (not changed).

## Assumptions to confirm with the user / group
- Area units are m2. `kosong` = parcels with no registered right. `banjir_*` = flood-hazard zone areas. `rdtr_luas` = area covered by an RDTR plan. `tahun_*` = registration years of titled parcels. (Also listed in the README as unconfirmed.)
- Defaults the user approved implicitly ("alright lets do it"): tenure-only primary variant, `luas_desa` out of A, rare rights grouped, sqrt shares. The 5-degree-of-freedom weight on the composition block is a principled default, not the only defensible one.

## TODO
Clustering-ready data (this stage):
- [x] Column roles, redundancy pruning, rare-rights grouping, transform, fit / place-later split, scaling, readiness checks, decision log, recipe, export
- [x] Teammate hand-off documents (README with an AI-assistant section, BACKGROUND), generated by cell 4-11
- [ ] User to run the notebook, review `data/clustering_ready/README.md` and `BACKGROUND.md`, and share the folder with the group
- [ ] Group to decide: variant A vs B; area-based vs count-based shares (rho 0.62: a real difference); the composition weight
- [ ] Optional: a variant C built on parcel-count shares; parquet export (needs pyarrow); a check that distances are stable under a different `SEED`
Modelling (out of scope, the user's group): algorithm choice, k, cluster-tendency tests (Hopkins/UMAP), stability, profiling and naming clusters. Note: do NOT plan on assigning `place_later` villages to clusters (see correction 1).
Open data questions:
- [ ] Ask the data owner (or add an elevation layer) about the flood zeros / 11 suspect kabupaten, the zero-area villages in Bengkulu, the regional no-parcel gap
- [ ] Optional: improve `kab_key` for Kab. Bogor-style double-code regencies
- [ ] Confirm column-meaning assumptions
- [ ] If the user hits an error in the notebook: ask for the traceback and `pd.__version__`
