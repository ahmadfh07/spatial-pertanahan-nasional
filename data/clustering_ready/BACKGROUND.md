# Background: how this data was prepared

This is the story behind `clustering_ready`. For the rules of use and the open decisions, read `README.md` first.

## 1. The dataset

- `desa.xlsx`: 79,842 villages (desa and kelurahan) x 33 columns, one row per village, computed 2026-10-17 in one batch (a snapshot, not a time series).
- Per village: village area, the number and area of land parcels under each of 8 kinds of land right, flood-hazard areas (low / medium / high), the area covered by a detailed spatial plan (RDTR), and the minimum / median / maximum registration year.
- The 8 rights are a complete partition: they add up exactly to the village's parcel count and parcel area in every row.

## 2. Data quality: what was found and what was done

| issue (flag name in the notebook) | rows | share of rows | treatment |
|---|---|---|---|
| placeholder records (not villages) (`is_pseudo`) | 2 | 0.0% | excluded (not a village) |
| village area is zero (`is_zero_area`) | 46 | 0.06% | excluded (every ratio is undefined) |
| parcel area more than 10x the village area (`is_ratio_outlier`) | 74 | 0.09% | excluded (almost certainly an error) |
| parcel area between 1x and 10x the village area (`is_overshoot`) | 10,935 | 13.7% | kept in the fit set |
| village has no parcels (`is_zero_parcels`) | 1,996 | 2.5% | not fitted (shares undefined); listed in place_later as a group of its own |
| province code disagrees with the province name (`prov_code_mismatch`) | 17 | 0.02% | kept (label problem only) |
| no flood area in any class (`flood_all_zero`) | 17,415 | 21.81% | kept, but flood is interpretation-only until the zeros are explained |
| minor rule breaks (kosong count without area; titled parcels without a year) (`is_minor_rule_break`) | 12 | 0.02% | kept (immaterial) |

- **Placeholder records.** Two rows are not villages: one named HGU (kode 33000000) and one whose name and kecamatan are '-' (kode 16030000). They are excluded.
- **Area outliers.** 74 villages have a parcel area more than 10x the village area. They are scattered across provinces (the top province holds 15%),
  49 of them are at least 90% `kosong` land, and in 67 the village area looks normal for its kabupaten,
  so the parcel area is the likely inflated side (a heuristic, not proof).
- **Zero village area** (46 rows) is concentrated in Bengkulu (22 rows), which points to a local source problem.
- **Parcels larger than the village** (1x to 10x, 10,935 rows) are kept: they look like ordinary, denser villages with overlapping parcels, and dropping them would bias the sample toward sparse villages.
- **Flood zeros.** 21.8% of villages have no flood area. The pattern is regional (kabupaten explains 28% of the variance, province 11%) and is not just tiny villages missing a map.
  11 kabupaten have at least 90% of villages at zero, mostly highland, volcanic or small-island areas, so real zeros are plausible. It cannot be settled from this file.
- **Province code mismatches** (17 rows) are a label problem only; the numbers are fine.
- **Names and codes.** Casing is inconsistent; a kabupaten name can hide a Kabupaten and a Kota; a few kabupaten codes are shared by two names (many look like a regency and the one it was split from). `kab_key` combines province, normalized name and code, and merges stray legacy codes.

## 3. Relationships that exist by construction (so they are not 'discoveries')

- Parcel count and parcel area are the sums over the 8 rights; for every right the count is zero exactly when the area is zero.
- Flood areas and the RDTR area never exceed the village area. A village has registration years exactly when it has at least one titled parcel, apart from 6 villages with titled parcels and no year.
- Titled share = 1 - kosong share. And log10(parcels per hectare) + log10(mean parcel size) = log10(parcel area / village area) + 4 exactly, so coverage is not an independent third column.

## 4. What the early analysis showed

- Village area and parcel count are almost unrelated (Spearman between -0.019 and 0.042 across every exclusion scenario): larger villages do not have proportionally more parcels.
- Medians and rank correlations barely move with the exclusion choices; means, sums and Pearson do (for example the Pearson correlation of village area and parcel area is 0.55 on the cleaned rows and 0.01 without exclusions).
- All area columns are extremely right-skewed; the work uses medians, ranks and log scales.

## 5. The pipeline in one page (`master.ipynb`)

- **Step 1, structural relations:** a rule book of identities, inequalities and null patterns; the 8-digit `kode8`; normalized names; hierarchy checks.
- **Step 2, size-neutral features:** shares, mean sizes, density, coverage, flood and RDTR shares, years; undefined ratios are left as NaN, never imputed.
- **Step 3, robust preparation:** flags, `analysis_ok`, a cut-off sensitivity table, presence flags for zero-heavy columns, log columns. 122 rows are excluded from analysis.
- **Step 3b, anomaly audit:** overlap and regional concentration of every anomaly, the flood-zero investigation, the area-outlier triage, `parcel_status`, `kab_key`, a sensitivity table.
- **Step 4, clustering-ready data:** column roles, redundancy removal, rare-rights grouping, sqrt transform, fit / place-later split, scaling, evidence, readiness checks, decision log, export.

## 6. Still unresolved

- Whether zero flood area means 'no hazard' or 'not computed' (ask the data owner, or compare with an elevation layer).
- The villages with no parcels, concentrated in a few provinces, and the zero-area villages concentrated in one province: coverage gaps or real?
- The meaning of `kosong`, the units, and the exact definition of the flood and RDTR columns (see the assumptions in `README.md`).
- Whether the data contains discrete clusters or a gradient (the first look suggests a continuum).

## 7. How to reproduce

Open `master.ipynb`, put `desa.xlsx` in `data/`, run all cells from the top (about a minute; needs numpy, pandas, matplotlib and scipy). Step 4 writes this folder. Environment when built: Python 3.11.16, pandas 3.0.5.
