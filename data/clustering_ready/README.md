# Clustering-ready data: desa (Indonesian villages, land tenure)

## Status

- **Data preparation is finished and documented. Modelling has not started.** Choosing the algorithm, the number of clusters,
  validating and naming clusters is the next stage and belongs to the modelling group.
- Source: `desa.xlsx` (not included in this folder), snapshot computed 2026-10-17. 79,842 villages (desa and kelurahan), one row per village.
- Variant A (default): 77,770 villages x 8 columns. Variant B: 77,098 villages x 10 columns.
- 2,744 villages are not in a fit set and are listed in `place_later.csv` with the reason.
- Read `BACKGROUND.md` for the story behind the data, and `decision_log.csv` for the reason and evidence behind every choice.

## What is in this folder

| file | rows | columns | what it is |
|---|---|---|---|
| `README.md` | - | - | this file: start here |
| `BACKGROUND.md` | - | - | how the data was prepared, what was found, what is still unresolved |
| `X_A.csv` | 77,770 | 8 | variant A inputs (land-tenure profile only), unscaled |
| `X_A_scaled.csv` | 77,770 | 8 | variant A inputs, scaled: ready for distance-based methods |
| `X_B.csv` | 77,098 | 10 | variant B inputs (A + village size + registration age), unscaled |
| `X_B_scaled.csv` | 77,098 | 10 | variant B inputs, scaled |
| `village_ids.csv` | 79,842 | 7 | names and keys for every village (raw names, inconsistent casing) |
| `interpretation_columns.csv` | 79,842 | 33 | raw shares, flood, RDTR, years, flags: for profiling clusters afterwards (village size and age enter variant B only in transformed form) |
| `place_later.csv` | 2,744 | 20 | villages outside a fit set, with the reason (scaled values are shown where defined, but are unreliable for excluded rows) |
| `excluded_rows.csv` | 122 | 11 | rows removed in Step 3 (placeholders, zero area, area outliers) |
| `decision_log.csv` | 14 | 5 | every preparation decision: default, alternatives, reason, measured evidence |
| `transform_recipe.json` | - | - | every parameter needed to reproduce or re-apply the transform |

## Quick start (Python)

```python
import pandas as pd

d = 'clustering_ready/'                                   # path to this folder
T = dict(index_col='kode8', dtype={'kode8': str})         # kode8 is TEXT: it has a leading zero
X     = pd.read_csv(d + 'X_A_scaled.csv', **T)            # model matrix, variant A, scaled
ids   = pd.read_csv(d + 'village_ids.csv', **T)           # names and kabupaten key
meta  = pd.read_csv(d + 'interpretation_columns.csv', **T)  # for profiling clusters only
later = pd.read_csv(d + 'place_later.csv', **T)           # villages outside a fit set; reason_A / reason_B say why

# ... fit a model on X, then attach the labels and profile the clusters:
# labels  = pd.Series(model_labels, index=X.index, name='cluster')
# profile = meta.join(labels, how='inner').groupby('cluster').median(numeric_only=True)

# who is missing from variant A, and why (an empty reason_A means the village IS in X_A):
print(later['reason_A'].dropna().str.slice(0, 40).value_counts())
```

To rebuild or re-apply the scaling, read `transform_recipe.json` (`scaling` -> `A` or `B`):
composition columns = `(value - comp_center) * comp_factor`; the other columns = `(value - center) / scale`.

## Who is in `place_later.csv`, and what to do with them

| group | variant A | variant B | suggested handling |
|---|---|---|---|
| no parcels: shares undefined | 1,950 | 1,950 | no tenure profile exists: report them as a group of their own, do not assign them to a cluster |
| excluded in Step 3 | 122 | 122 | placeholders, zero area and area outliers: areas are unreliable, so do not assign them |
| no registration year (age undefined) | 0 | 672 | already in `X_A`; for variant B they can be scored on the A columns if needed |

## The input columns

- `s_hak_milik`, `s_hgb`, `s_hgu`, `s_hak_pakai`, `s_kosong`, `s_other`: square root of the share of the village's parcel **area** held under each right
  (the square root makes Euclidean distance proportional to the Hellinger distance and tolerates exact zeros).
  `s_other` groups the rights below 1% of total area: hak_pengelolaan, hak_wakaf, lainnya.
- `log_parcel_density`: log10 of parcels per hectare. `log_mean_parcel`: log10 of the mean parcel size in m2.
- Variant B adds `log_luas_desa` (log10 village area, m2) and `log1p_age_median` (log of 1 + years between 2026 and the median registration year).
- Scaled files: log / age columns are robust z-scores; the composition block is centred and multiplied by one common factor so it carries 5 units of variance (6 parts that sum to 1 = 5 independent directions).

## Rules for working with this data

1. Read `kode8` as **text**. Spreadsheets and default CSV readers drop its leading zero.
2. Use the `*_scaled.csv` files as delivered for distance-based methods. Do not rescale the blocks again by habit; if you change the weighting,
   do it on purpose (decision D11) and record it.
3. Do **not** use columns from `interpretation_columns.csv` as clustering inputs without an explicit new decision. Flood in particular (see Caveats).
   The only vetted extras, village size and registration age, are already inside `X_B` in transformed form.
4. Do not drop or impute `place_later` villages silently. Villages with no parcels have no tenure profile (the shares are 0/0): report them as their own group.
5. Any change to the preparation is a new decision: add an entry (D15, D16, ...) with the reason and the measured effect.
6. The evidence numbers describe how much a preparation choice changes distances. They are **not** a measure of clustering quality.

## Decisions already made (reasons and evidence: `decision_log.csv`)

| id | decision | default |
|---|---|---|
| D1 | Scope of the inputs | Variant A: land-tenure profile only. Variant B: A + village size + registration age. |
| D2 | Village area as an input | Not in A; log10 area in B. |
| D3 | What the shares measure | Share of parcel AREA, not of parcel count. |
| D4 | Rare rights | Rights below 1% of total area are grouped into 'other': hak_pengelolaan, hak_wakaf, lainnya. |
| D5 | Transform for the shares | Square root (Hellinger geometry). |
| D6 | Redundant columns | Dropped: titled share, coverage (log, clipped), count-based shares, per-right mean sizes. |
| D7 | Parcel size and density | log10 of both. |
| D8 | Villages with no parcels | Not fitted (1,950 analysis rows); listed in place_later. |
| D9 | Rows excluded in Step 3 | Not fitted; listed in place_later with the reason. |
| D10 | Overshoot rows (parcels 1-10x village area) | Kept in the fit set. |
| D11 | Scaling | Robust z-score for the log / age columns; composition block scaled jointly to 5 units of variance (5 = parts - 1). |
| D12 | Flood, RDTR, years, geography | Interpretation only; never used to build clusters. |
| D13 | Binary has_* flags | Not used. |
| D14 | Registration age (variant B) | log(1 + years since the median registration year). |

## Decisions the group still has to make

1. **Variant A or B.** B differs from A by a distance rank correlation of 0.905 (1.00 = identical neighbourhoods).
   A is the default because it keeps clusters readable as tenure types; B is there so the effect of extra columns can be tested.
2. **Shares of area or of parcel count.** The default measures area. Parcel-count shares give a clearly different geometry (rank correlation 0.621).
   A variant built on counts is not delivered; cells 4-4 and 4-7 of the notebook show how it would be made.
3. **Weight of the composition block.** The default gives it 70.1% of the total variance. Alternatives, as rank correlation with the default:
   - z-score every column: 0.934; composition = 75.0% of total variance, default 70.1%)
   - each concept counts once (composition = 1): 0.894; composition = 31.9% of total variance, default 70.1%)
   - composition and log block equal: 0.971; composition = 50.0% of total variance, default 70.1%)
   - no scaling: 0.762; composition = 15.7% of total variance, default 70.1%)
4. **Whether to add flood, RDTR or registration years later**, once the flood question is settled.

## Caveats you should know before interpreting anything

- **Flood zeros are ambiguous.** 21.8% of villages have no flood area in any class: 'no hazard' or 'not computed' cannot be told apart.
  The zeros are strongly regional (kabupaten explains 28% of the variance of the zero flag, province 11%), and 11 kabupaten have 90% or more of their villages at zero.
  Do not read flood differences between clusters as proven hazard differences.
- **A first look does not show clearly separated groups.** In a PCA of variant A (scaled), the first two components explain 68% of the variance and the villages form a continuous cloud with dense regions.
  Discrete clusters are not guaranteed; a gradient that an algorithm cuts into segments is a real possibility. Test this before presenting clusters as 'types'.
- **Villages with no parcels** (1,950 in the analysis rows) are concentrated in Papua Barat (344), Nusa Tenggara Timur (296), Sumatera Utara (295), Papua (283). They also have more zero-flood and less RDTR coverage than other villages,
  which looks like a regional coverage gap (hypothesis, not confirmed).
- **Excluded rows** (122): placeholders, villages with zero area, and 74 villages whose parcel area is more than 10x the village area. Their area-based values are unreliable even where `place_later.csv` shows them.
- **Names are raw.** `village_ids.csv` keeps the source spelling (UPPER and Title case mixed). Group at kabupaten level with `kab_key`, not with the name:
  a name can hide a Kabupaten and a Kota. 26 names still map to more than one key (mostly real Kabupaten/Kota twins; Kab. Bogor is split over two codes).
- **Assumptions not yet confirmed with the data owner:** area units are m2; `kosong` = parcels with no registered right; `banjir_*` = areas in low / medium / high flood-hazard zones;
  `rdtr_luas` = area covered by an RDTR plan; `tahun_*` = registration years of titled parcels.
- The evidence correlations were measured on a random sample of 1,500 villages (seed 42).

## Suggested next steps for modelling (not prescriptive)

1. Check whether the data has cluster structure at all (tendency tests, projections), given the continuous cloud above.
2. Compare several algorithms and several criteria for the number of clusters. With about 78,000 rows, compute expensive metrics (such as the silhouette) on samples.
3. Test stability: different seeds, bootstrap resamples, variant A versus B, and a changed composition weight.
4. Test whether clusters merely reproduce geography (for example Cramer's V between cluster and province).
5. Profile and name clusters with `interpretation_columns.csv` (raw rights shares, flood, RDTR, registration years, village type, geography).
6. Report `place_later` explicitly: villages with no parcels as a group of their own; excluded rows are not assigned (unreliable areas); for variant B, the villages that only lack a registration year can be scored on the A columns.

## Glossary

- **desa / kelurahan**: rural village / urban ward. **kabupaten / kota**: regency / city. **provinsi**: province.
- **persil**: land parcel. **hak milik**: freehold ownership title. **HGB** (hak guna bangunan): right to build. **HGU** (hak guna usaha): cultivation / plantation concession.
- **hak pakai**: right of use. **hak pengelolaan**: management right over state land. **hak wakaf**: endowment (religious / charitable) land. **lainnya**: other.
- **kosong**: 'empty'; here understood as parcels with no registered right (assumption, supported by the registration-year pattern).
- **RDTR**: detailed spatial plan. **banjir**: flood. **kode8**: 8-digit village code PP KK CC DD (province, kabupaten/kota, kecamatan, village).

## If you are an AI assistant helping a teammate

- Read this README, `decision_log.csv` and `transform_recipe.json` before writing any code. Do not redo the preprocessing; use the delivered matrices.
- Keep `kode8` as text. Do not use `interpretation_columns.csv` as model input unless the user explicitly decides to.
- Do not present clusters as real or as 'types' before stability and structure checks; the first look suggests a continuum. State uncertainty plainly.
- Do not describe flood differences as hazard evidence. Do not silently drop or impute `place_later` villages.
- If a change to the preparation is needed, propose it as a new decision with its reason and a measured effect, and tell the user.
- If something in this folder contradicts `BACKGROUND.md`, this README and `decision_log.csv` win.

## Provenance and reproducibility

- Built by `master.ipynb`: Step 1 (structural relations), Step 2 (features), Step 3 (robust preparation), Step 3b (anomaly audit), Step 4 (cells 4-1 to 4-11). Run the notebook top to bottom with `desa.xlsx` in `data/`. Packages: numpy, pandas, matplotlib, and scipy (pandas uses it for Spearman correlations in earlier steps).
- Environment when built: Python 3.11.16, pandas 3.0.5, numpy 2.4.6. Parameters: `RARE_AREA_SHARE` 0.01, `RATIO_CAP` 10, `ZERO_THRESH` 0.5, `STRAY_MAX` 5, `SEED` 42.
- Created 2026-11-26 03:35:20.
