# Clustering-ready data: desa

Built by master.ipynb (Step 4). Fit sets: variant A = 77,770 villages, variant B = 77,098 villages.

## Files
- X_A.csv / X_A_scaled.csv: variant A (land-tenure profile only), unscaled and scaled. Index = kode8.
- X_B.csv / X_B_scaled.csv: variant B (A + log village area + registration age).
- village_ids.csv: names and keys for every village (kode8, kode, nama, kecamatan, kabupaten, provinsi, tipe, kab_key).
- interpretation_columns.csv: columns NOT used to build clusters (raw shares, flood, RDTR, years, flags). Use them to profile clusters.
- place_later.csv: villages not in a fit set, with the reason, the unscaled columns and the A-scaled columns where defined.
- excluded_rows.csv: the rows removed in Step 3 (placeholders, zero area, area outliers).
- decision_log.csv: every decision, the alternatives, the reason and the measured evidence.
- transform_recipe.json: every parameter needed to reproduce or re-apply the transform.

## Columns
- s_*: square root of the area share of each right (Hellinger geometry). Rights below 1% of total area are grouped into s_other.
- log_parcel_density, log_mean_parcel: log10 parcels per hectare and log10 mean parcel size (m2). Coverage is derivable from these two.
- Variant B only: log_luas_desa (log10 village area) and log1p_age_median (log of 1 + years since the median registration year).

## Notes
- Read kode8 as TEXT. It is an 8-digit code with a leading zero; spreadsheets drop the zero.
- The scaled composition block carries 5 units of variance (6 parts - 1), not 1 unit per column.
- Zero flood area is ambiguous ('no hazard' versus 'not computed') and strongly regional: do not read flood differences between clusters as proven hazard differences.
- Villages in place_later have no tenure profile (no parcels) or unreliable areas (excluded). Assign them after fitting if needed, using transform_recipe.json.