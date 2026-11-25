# Handoff: desa.xlsx analysis

_Last updated: 2026-11-19 (after prompt 12/13)_

**Standing instruction:** write this file ONLY when the user asks (stated in prompt 9; prompt 12 asked: "write in handoff dont forget").
**Language:** the user mostly writes English but switched to Indonesian in the last message ("Lanjutkan"). Reply in the language the user writes; keep the notebook, handoff and deliverable files in English.

## Project context
- Source: `/mnt/project/desa.xlsx` (15 MB, 1 sheet `desa`). Read-only.
- Content: land parcel / land-rights summary per village (desa / kelurahan) in Indonesia, with flood-hazard and RDTR (detailed spatial plan) area columns.
- **Goal: produce clustering-ready data plus the documented decisions behind it. The user's group does the modelling (algorithms, k, validation); do not do that part.**
- User works in `master.ipynb` (kernel `ds-ugm`, Python 3.11). Loader puts the data in `rawDesa`; expects `./data/desa.xlsx`. **Deliver code as continuation cells appended to master.ipynb; the user runs them himself.** New cells carry no saved outputs.
- Sandbox facts: no Jupyter/nbformat; test with a custom cell runner (not persisted). Python 3.12 / pandas 3.0.6 (user's pandas unknown): write version-safe code, numpy/pandas/matplotlib only (Cramer's V, Spearman-on-ranks, PCA-by-SVD are hand-written). Excel load ~22-26 s. Sandbox resets between tasks. Lesson learned: check cell OUTPUTS, not just "no error" (three bugs were caught that way, see "Caught during the build").

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
- **P9 tenure-only vs everything (DONE, discussion).** Pros/cons table; recommendation: tenure-only as primary run, extended variant afterwards for comparison.
- **P10 "is the data clustering-ready?" (DONE).** Answer: no, no model matrix yet. Measured: 1,950 villages have NaN in 11 features (all no-parcel villages), every village has at least one exact-zero share (so CLR impossible without grouping or zero replacement), titled share = 1 - kosong share, features on different scales.
- **P11 steps 4-8 vs new work (DONE, discussion).** Old steps 4-8 (relation inference) are replaced by a data-preparation plan; modelling items belong to the user's group.
- **P12/13 Step 4 clustering-ready data implemented (DONE).** 13 cells appended (11 code + 2 markdown) -> notebook has **50 cells**. First 37 cells byte-identical to the previously delivered version. Tested end-to-end on a copy: all 40 code cells run clean in ~40 s; Step 4 verified re-run safe (identical matrices, no duplicate columns).

### Notebook map (cells after the user's 5)
1. **Step 1 structural relations** -> `desa`, `kode8`, rule book, hierarchy checks, `*_n` normalized names.
2. **Step 2 features** -> `FEATURE_GROUPS`, helpers `safe_div`, `add_cols`.
3. **Step 3 robust prep** -> flags, `analysis_ok`, `RATIO_CAP=10`, `has_*`, `*_log10`, `desaOK`.
4. **Step 3b anomaly audit** -> `anomalies`, `conc`, `flood_suspect_kab`, `parcel_status`, `kab_key`, `excluded`, `sens`/`delta`.
5. **Step 4 clustering-ready data (new):**
   - 4-1 parameters (`RARE_AREA_SHARE=0.01`, `SAMPLE_N=1500`, `SEED=42`, `EXPORT=True`, `EXPORT_DIR=DATA/"clustering_ready"`) + `roles_df` (column roles)
   - 4-2 redundancy checks (exact identities, SVD rank, near-duplicate pairs)
   - 4-3 rare-rights grouping (`GROUPED`, `KEPT`, `other_share_luas`)
   - 4-4 transform -> `T`, `COLS` (A/B), `FIT` masks
   - 4-5 fit set vs `place_later`
   - 4-6 scaling -> `RECIPE`, `apply_recipe`, `X_A`, `X_A_scaled`, `X_B`, `X_B_scaled`, `var_share`
   - 4-7 evidence (pairwise-distance rank correlations on 1,500 villages) -> `evidence`, `EVID`
   - 4-8 readiness checks (asserts) + shape table; 4-8b histograms + PCA picture
   - 4-9 decision log D1-D14 -> `decision_log` (printed as text)
   - 4-10 package + export -> `village_ids`, `interp`, `place_later_out`, `recipe_json`, `deliverables`
   - Requires earlier sections to be run (uses `excluded`, `delta`, `RATIO_CAP`, `ZERO_THRESH`, `STRAY_MAX`, `REF_YEAR`, `DATA`).

### Export (written by 4-10 when `EXPORT = True`, ~48 MB, folder `data/clustering_ready/`)
`X_A.csv`, `X_A_scaled.csv`, `X_B.csv`, `X_B_scaled.csv` (index `kode8`); `village_ids.csv`; `interpretation_columns.csv` (33 cols); `place_later.csv` (2,744 rows, 20 cols); `excluded_rows.csv` (122); `decision_log.csv` (14); `transform_recipe.json`; `README.md`. Verified: `kode8` keeps its leading zero (read as text), ids line up across files, X_A_scaled can be rebuilt from X_A + recipe (diff ~1e-5 from the 6-significant-digit CSV rounding). **Modellers must read `kode8` as text.**

## Verified results (Step 4)
- **Inputs.** Variant A (default, 8 columns): `s_hak_milik`, `s_hgb`, `s_hgu`, `s_hak_pakai`, `s_kosong`, `s_other` (sqrt of area shares) + `log_parcel_density`, `log_mean_parcel`. Variant B (10 columns) adds `log_luas_desa` and `log1p_age_median`. Flood, RDTR, years, geography, `tipe` = interpretation only.
- **Fit sets:** A = 77,770 villages; B = 77,098. `place_later` = 2,744 = 122 excluded in Step 3 + 1,950 no-parcel villages + 672 B-only (666 untitled-only + 6 titled with null year). Reconciles exactly to 79,842.
- **Coverage is NOT a third input (correction to the earlier clustering plan):** `log10(density) + log10(mean parcel size) = log10(coverage) + 4` holds to 1e-15 (SVD smallest singular value 0.000), so coverage and its clipped version are derivable. Also titled share = 1 - kosong share exactly.
- **Rare rights:** rule = area share < 1% -> pengelolaan 0.47%, wakaf 0.05%, lainnya 0.00% grouped into `other`. HGB (1.17%) and hak_pakai (1.76%) kept; HGU kept (16.8% of area, present in only 6% of villages). Note wakaf is present in 46% of villages: it is grouped because it is tiny by area, not rare by presence (earlier wording "three rarest" was loose).
- **Evidence (distance-structure rank correlation vs default, 1,500 villages):**
  - raw shares 0.945; CLR 0.704 / 0.780 / 0.668 for zero replacement 1e-4 / 1e-3 / 1e-2; two CLR variants vs each other **0.558** (arbitrary zero replacement -> sqrt chosen)
  - ungrouped 8 parts vs grouped 6 parts: **1.000** (grouping costs nothing)
  - parcel-count shares instead of area shares: **0.621** (a real choice; default = area)
  - scaling: z-score every column 0.934 (composition 75.0% of variance); each concept once 0.894 (31.9%); blocks equal 0.971 (50.0%); no scaling 0.762 (15.7%); default composition = 70.1% (5 degrees of freedom = 6 parts - 1; factor 4.44 for A, 4.482 for B)
  - scope: B vs A 0.905; composition block alone vs A 0.921
- **Readiness:** 0 NaN / inf / constant columns / duplicate ids in all four matrices; 0 exact duplicate rows; no input pair with |Spearman| >= 0.9. Skew after transform: sqrt shares 3-7 for the zero-heavy ones (hgb 55.9% zeros, hgu 93.8%, other 51.5%), logs within +-1.2. 
- **Age:** raw `age_median` skew 2.01 with 1,523 villages beyond 5 robust SD; `log1p` -> skew -0.23, 0 beyond 5 SD (decision D14).
- **PCA picture (variant A, scaled):** PC1 39.7%, PC2 28.0%, PC1-4 88.7%. The first two components show a **continuous cloud with two dense regions, not clearly separated groups**. Whether discrete clusters exist is for the modelling step (cluster-tendency tests such as Hopkins belong there).
- Decision log D1-D14 (in the notebook and `decision_log.csv`): scope (A vs B), village area, area vs count shares, rare-rights grouping, sqrt transform, redundant columns dropped, logs for size/density, no-parcel villages not fitted, excluded rows not fitted, overshoot rows kept (dropping them shifts median parcel density -26.9%), scaling, interpretation-only columns, no `has_*` flags, log1p age.

### Caught during the build (fixed)
1. The SVD rank demo centred by median, so the smallest singular value was 43.6 instead of ~0; the identity is linear only after mean-centring. Fixed.
2. A loop variable `delta` in 4-7 overwrote the Step 3b-9 sensitivity table `delta`, which silently broke decision D10's evidence (fallback text hid it). Renamed to `repl`.
3. The readiness table showed `age_median` with a heavy tail; handled with log1p (D14) instead of only logging it.

## Earlier verified findings (still valid)
- Structural relations all hold (8 rights sum to totals; count==0 <=> area==0 except 6 `kosong` rows; flood/RDTR <= village area; year present => titled parcel). Soft rule `luas_persil <= luas_desa` violated in 11,009 rows (13.8%).
- `prov_code` matches `provinsi` except 17 rows; 10 `kab_code`s are shared by two names (regency splits, hypothesis); `kab_key` gives 506 keys, 26 names still have >1 key (Kab. Bogor split over 1010/1033 is a known limit).
- Anomalies (Step 3b): 122 rows excluded (2 pseudo-records incl. kode 33000000 "HGU" and kode 16030000 whose `nama`/`kecamatan` were "-" turned into NaN by the user's SENTINELS; 46 zero area; 74 area ratio > 10). Ratio outliers are scattered, mostly `kosong`, and the parcel side is the likely inflated one (67 of 74). Zero village area concentrated in Bengkulu (22 of 46). Zero-parcel villages: 53% flood-zero (vs 22%), 4% RDTR (vs 17%): looks like a regional coverage gap (hypothesis).
- Flood zeros are strongly regional (kabupaten explains 28% of variance, province 11%); 11 suspect kabupaten (Siau Tagulandang Biaro, Ternate, Bangli, Tolikara, Puncak Jaya, Kepulauan Seribu, ...), mostly highland/volcanic/small-island so real zeros are plausible; unresolved without the data owner or an elevation layer. Flood stays interpretation-only.
- Spearman `luas_desa ~ jumlah_persil` is ~0 in every scenario: parcel count is nearly independent of village area. Medians/ranks are robust to exclusion choices; means, sums and Pearson are not.
- User's cell 2 still looks for a leftover `anggota.csv`; cell 3 `dtype={"id":...}` is a no-op (not changed).

## Assumptions to confirm with the user / group
- Area units are m2. `kosong` = parcels with no registered right. `banjir_*` = flood-hazard zone areas. `rdtr_luas` = area covered by an RDTR plan. `tahun_*` = registration years of titled parcels.
- Defaults the user approved implicitly ("alright lets do it"): tenure-only primary variant, `luas_desa` out of A, rare rights grouped, sqrt shares. The 5-degree-of-freedom weight on the composition block is a principled default, not the only defensible one (evidence above).

## TODO
Clustering-ready data (this stage):
- [x] Column roles, redundancy pruning, rare-rights grouping, transform, fit / place-later split, scaling, readiness checks, decision log, recipe, export
- [ ] User to run the new cells and review `data/clustering_ready/README.md` and the decision log with the group
- [ ] Group to decide: variant A vs B; area-based vs count-based shares (rho 0.62: a real difference; a variant C with count shares could be built); the composition weight
- [ ] Optional: parquet export (needs pyarrow), a variant C, a quick check that distances are stable under a different `SEED`
Modelling (out of scope, user's group): algorithm choice, k, cluster-tendency tests (Hopkins/UMAP), stability, profiling and naming clusters, assigning `place_later` villages after fitting.
Open data questions:
- [ ] Ask the data owner (or add an elevation layer) about the flood zeros / 11 suspect kabupaten, the zero-area villages in Bengkulu, the regional zero-parcel gap
- [ ] Optional: improve `kab_key` for Kab. Bogor-style double-code regencies
- [ ] Confirm column-meaning assumptions
- [ ] If the user hits an error in new cells: ask for the traceback and `pd.__version__`
