"""Dashboard Interaktif: Tipologi Pertanahan Nasional (Phase 6 Deployment)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Tipologi Pertanahan Nasional",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "modeling" / "outputs"

SEG_ORDER = [
    "S1_PADAT_TRANSISI",
    "S2_SHM_PARSIAL",
    "S3_PRIORITAS_PTSL",
    "S4_PERKEBUNAN_HGU",
    "S5_HAK_PAKAI_AWAL",
    "G6_BELUM_TERPETAKAN",
    "G7_ANOMALI_AUDIT",
]

SEG_LABELS = {
    "S1_PADAT_TRANSISI": "S1: Padat Urban-Jawa/Bali (Penuntasan Sisa)",
    "S2_SHM_PARSIAL": "S2: Dominan SHM Parsial (Cakupan Peta Rendah)",
    "S3_PRIORITAS_PTSL": "S3: Dominan Belum Bersertifikat (Prioritas #1 PTSL)",
    "S4_PERKEBUNAN_HGU": "S4: Kantong Perkebunan Skala Besar (HGU)",
    "S5_HAK_PAKAI_AWAL": "S5: Kantong Aset Pemerintah / Hak Pakai (Pemetaan Awal)",
    "G6_BELUM_TERPETAKAN": "G6: Belum Terpetakan (Nol Persil)",
    "G7_ANOMALI_AUDIT": "G7: Anomali Data (Perlu Audit Spasial)",
}

SEG_SHORT = {
    "S1_PADAT_TRANSISI": "S1: Padat Urban–Transisi",
    "S2_SHM_PARSIAL": "S2: SHM Parsial",
    "S3_PRIORITAS_PTSL": "S3: Prioritas PTSL",
    "S4_PERKEBUNAN_HGU": "S4: Perkebunan HGU",
    "S5_HAK_PAKAI_AWAL": "S5: Hak Pakai Awal",
    "G6_BELUM_TERPETAKAN": "G6: Nol Persil",
    "G7_ANOMALI_AUDIT": "G7: Anomali Audit",
}

# Palet Tableau 10 (bersih, natural, bebas neon/ungu)
SEG_COLORS = {
    "S1_PADAT_TRANSISI": "#4e79a7",
    "S2_SHM_PARSIAL": "#59a14f",
    "S3_PRIORITAS_PTSL": "#f28e2b",
    "S4_PERKEBUNAN_HGU": "#76b7b2",
    "S5_HAK_PAKAI_AWAL": "#9c755f",
    "G6_BELUM_TERPETAKAN": "#bab0ac",
    "G7_ANOMALI_AUDIT": "#e15759",
}

RIGHT_COLORS = {
    "Hak Milik": "#4e79a7",
    "Kosong": "#f28e2b",
    "HGU": "#59a14f",
    "Hak Pakai": "#9c755f",
    "HGB": "#edc948",
    "Lainnya": "#bab0ac",
}

CLUSTER_TO_SEG = {
    2: "S1_PADAT_TRANSISI",
    4: "S2_SHM_PARSIAL",
    1: "S3_PRIORITAS_PTSL",
    3: "S4_PERKEBUNAN_HGU",
    0: "S5_HAK_PAKAI_AWAL",
}


@st.cache_data(show_spinner="Memuat data 79.842 desa...")
def load_desa_data() -> pd.DataFrame:
    df = pd.read_csv(OUT_DIR / "desa_tipologi_final.csv", dtype={"kode8": str})
    df["kode8"] = df["kode8"].str.zfill(8)
    df["segment_short"] = df["segment_code"].map(SEG_SHORT)
    return df


@st.cache_data
def load_kab_data() -> pd.DataFrame:
    return pd.read_csv(OUT_DIR / "kabupaten_prioritas.csv")


@st.cache_data
def load_summaries() -> dict:
    summaries = {}
    for step in (1, 3, 4, 5):
        with open(OUT_DIR / f"step{step}_summary.json", encoding="utf-8") as f:
            summaries[f"step{step}"] = json.load(f)
    return summaries


desa_df = load_desa_data()
kab_df = load_kab_data()
summaries = load_summaries()

# --- Sidebar Filters ---
st.sidebar.title("Filter Wilayah & Segmen")

all_provinces = sorted(desa_df["provinsi"].dropna().unique().tolist())
sel_provs = st.sidebar.multiselect(
    "Provinsi (kosong = semua 34 provinsi)",
    options=all_provinces,
    default=[],
)

kab_scope = kab_df if not sel_provs else kab_df[kab_df["provinsi"].isin(sel_provs)]
kab_options_df = kab_scope[["kab_key", "kabupaten", "provinsi"]].sort_values(["provinsi", "kabupaten"])
kab_display_map = {
    row["kab_key"]: f"{row['kabupaten']} ({row['provinsi']})"
    for _, row in kab_options_df.iterrows()
}
sel_kabs = st.sidebar.multiselect(
    "Kabupaten/Kota (opsional)",
    options=list(kab_display_map.keys()),
    format_func=lambda k: kab_display_map[k],
    default=[],
)

sel_segs = st.sidebar.multiselect(
    "Segmen / Grup",
    options=SEG_ORDER,
    format_func=lambda s: SEG_SHORT[s],
    default=SEG_ORDER,
)

sel_tipe = st.sidebar.radio(
    "Tipe Wilayah",
    options=["Semua", "Desa", "Kelurahan"],
    horizontal=True,
)

sel_overshoot = st.sidebar.selectbox(
    "Status Luas Persil (Overshoot 1–10x)",
    options=["Semua", "Hanya Overshoot (1–10x)", "Non-Overshoot"],
)

st.sidebar.divider()
st.sidebar.info(
    "**Info Dataset & Model**\n"
    "- Sumber: `desa.xlsx` (snapshot 17 Okt 2026)\n"
    "- Total: **79.842** desa/kelurahan\n"
    "- Model utama: **K-Means (k = 5)** pada **Variant A** (`77.770` desa) + **2 grup `place_later`** (`2.072` desa)\n"
    "- `kode8` dijaga sebagai teks 8 digit"
)

# Apply Filters
mask = pd.Series(True, index=desa_df.index)
if sel_provs:
    mask &= desa_df["provinsi"].isin(sel_provs)
if sel_kabs:
    mask &= desa_df["kab_key"].isin(sel_kabs)
if sel_segs:
    mask &= desa_df["segment_code"].isin(sel_segs)
else:
    mask &= False
if sel_tipe != "Semua":
    mask &= desa_df["tipe"] == sel_tipe
if sel_overshoot == "Hanya Overshoot (1–10x)":
    mask &= desa_df["is_overshoot"] == True  # noqa: E712
elif sel_overshoot == "Non-Overshoot":
    mask &= desa_df["is_overshoot"] == False  # noqa: E712

flt = desa_df.loc[mask]

# --- Header & KPI Cards ---
st.title("Dashboard Tipologi Pertanahan Nasional")
st.caption(
    "Segmentasi Kematangan Kadastral & Prioritas Kebijakan ATR/BPN Tingkat Desa/Kelurahan se-Indonesia (Phase 6: Deployment)"
)

n_total = len(flt)
n_s3 = int((flt["segment_code"] == "S3_PRIORITAS_PTSL").sum())
n_s1 = int((flt["segment_code"] == "S1_PADAT_TRANSISI").sum())
n_g6 = int((flt["segment_code"] == "G6_BELUM_TERPETAKAN").sum())
n_g7 = int((flt["segment_code"] == "G7_ANOMALI_AUDIT").sum())
n_ov = int(flt["is_overshoot"].sum())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Desa / Kelurahan Terfilter", f"{n_total:,}", f"{n_total / len(desa_df) * 100:.1f}% dari 79.842")
c2.metric(
    "Prioritas #1 PTSL (S3)",
    f"{n_s3:,}",
    f"{(n_s3 / n_total * 100) if n_total else 0:.1f}% terfilter",
)
c3.metric(
    "Padat Penuntasan Sisa (S1)",
    f"{n_s1:,}",
    f"{(n_s1 / n_total * 100) if n_total else 0:.1f}% terfilter",
)
c4.metric(
    "Belum Terpetakan (G6)",
    f"{n_g6:,}",
    f"{(n_g6 / n_total * 100) if n_total else 0:.1f}% (0 persil)",
)
c5.metric(
    "Perlu Audit Spasial",
    f"{n_g7 + n_ov:,}",
    f"{n_g7:,} eksklusi + {n_ov:,} overshoot",
)

if n_total == 0:
    st.warning("Tidak ada desa yang cocok dengan kombinasi filter saat ini. Ubah filter di sidebar.")
    st.stop()

# --- 5 Interactive Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Ringkasan Nasional",
    "Prioritas Kabupaten/Kota",
    "Cari & Profil Desa",
    "Profil 5 Segmen (S1–S5)",
    "Metodologi & Batasan Jujur",
])

# ==============================================================================
# TAB 1: RINGKASAN NASIONAL
# ==============================================================================
with tab1:
    col_left, col_right = st.columns([1.05, 1.15])

    seg_counts = flt["segment_code"].value_counts().reindex(SEG_ORDER, fill_value=0)
    policy_map = (
        desa_df.drop_duplicates("segment_code")
        .set_index("segment_code")[["segment_label", "fit_status", "arahan_kebijakan"]]
    )
    seg_summary_df = pd.DataFrame({
        "segment_code": SEG_ORDER,
        "Segmen / Grup": [SEG_LABELS[s] for s in SEG_ORDER],
        "Pendek": [SEG_SHORT[s] for s in SEG_ORDER],
        "Jumlah Desa": [int(seg_counts[s]) for s in SEG_ORDER],
        "Persen (%)": [round(seg_counts[s] / n_total * 100.0, 2) for s in SEG_ORDER],
        "Status": [str(policy_map.loc[s, "fit_status"]) for s in SEG_ORDER],
        "Arahan Kebijakan": [str(policy_map.loc[s, "arahan_kebijakan"]) for s in SEG_ORDER],
    })

    with col_left:
        st.subheader("Distribusi 7 Segmen / Grup")
        plot_seg = seg_summary_df.iloc[::-1]
        fig_nat = go.Figure(
            go.Bar(
                x=plot_seg["Jumlah Desa"],
                y=plot_seg["Pendek"],
                orientation="h",
                marker_color=[SEG_COLORS[s] for s in plot_seg["segment_code"]],
                text=[f"{n:,} ({p:.1f}%)" for n, p in zip(plot_seg["Jumlah Desa"], plot_seg["Persen (%)"])],
                textposition="outside",
                customdata=np.stack([plot_seg["Segmen / Grup"], plot_seg["Arahan Kebijakan"]], axis=-1),
                hovertemplate="<b>%{customdata[0]}</b><br>Jumlah: %{x:,} desa<br>Arahan: %{customdata[1]}<extra></extra>",
            )
        )
        fig_nat.update_layout(
            height=420,
            margin=dict(l=10, r=60, t=10, b=20),
            xaxis_title="Jumlah Desa / Kelurahan",
            yaxis_title="",
            xaxis=dict(range=[0, max(plot_seg["Jumlah Desa"].max() * 1.25, 10)]),
        )
        st.plotly_chart(fig_nat, width="stretch")

    with col_right:
        st.subheader("Komposisi Segmen per Provinsi")
        sort_by_seg = st.selectbox(
            "Urutkan provinsi berdasarkan persentase tertinggi:",
            options=["S1_PADAT_TRANSISI", "S2_SHM_PARSIAL", "S3_PRIORITAS_PTSL", "S4_PERKEBUNAN_HGU", "S5_HAK_PAKAI_AWAL", "G6_BELUM_TERPETAKAN"],
            format_func=lambda s: SEG_SHORT[s],
            index=2,
        )
        prov_ct = pd.crosstab(flt["provinsi"], flt["segment_code"]).reindex(columns=SEG_ORDER, fill_value=0)
        prov_pct = prov_ct.div(prov_ct.sum(axis=1), axis=0) * 100.0
        prov_pct["total"] = prov_ct.sum(axis=1)
        prov_pct = prov_pct.sort_values(sort_by_seg, ascending=True)

        fig_prov = go.Figure()
        y_prov = [f"{p} (n={int(prov_pct.loc[p, 'total']):,})" for p in prov_pct.index]
        for s in SEG_ORDER:
            fig_prov.add_trace(
                go.Bar(
                    name=SEG_SHORT[s],
                    x=prov_pct[s],
                    y=y_prov,
                    orientation="h",
                    marker_color=SEG_COLORS[s],
                    hovertemplate=f"<b>%{{y}}</b><br>{SEG_SHORT[s]}: %{{x:.1f}}%<extra></extra>",
                )
            )
        fig_prov.update_layout(
            barmode="stack",
            height=max(420, 22 * len(prov_pct) + 90),
            margin=dict(l=10, r=10, t=40, b=20),
            xaxis=dict(title="Proporsi (%)", range=[0, 100]),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5, font=dict(size=10)),
        )
        st.plotly_chart(fig_prov, width="stretch")

    st.subheader("Ringkasan & Arahan Kebijakan per Segmen")
    st.dataframe(
        seg_summary_df[["Segmen / Grup", "Jumlah Desa", "Persen (%)", "Status", "Arahan Kebijakan"]],
        width="stretch",
        hide_index=True,
    )

# ==============================================================================
# TAB 2: PRIORITAS KABUPATEN/KOTA
# ==============================================================================
with tab2:
    st.subheader("Pemeringkatan 506 Kabupaten/Kota (`kab_key`)")

    k_flt = kab_df.copy()
    if sel_provs:
        k_flt = k_flt[k_flt["provinsi"].isin(sel_provs)]
    if sel_kabs:
        k_flt = k_flt[k_flt["kab_key"].isin(sel_kabs)]

    col_m1, col_m2 = st.columns([2, 1])
    mission = col_m1.radio(
        "Pilih Misi Prioritas Intervensi:",
        options=[
            "Prioritas #1 Sertifikasi PTSL (S3)",
            "Prioritas Pemetaan Awal (G6 Nol Persil)",
            "Prioritas Audit Data & Batas Spasial (G7 + Overshoot)",
        ],
        horizontal=True,
    )
    top_n = col_m2.slider("Jumlah Top Kabupaten/Kota:", min_value=5, max_value=30, value=10, step=5)

    if "PTSL" in mission:
        rank_col, pct_col, bar_col, label_txt = (
            "S3_PRIORITAS_PTSL",
            "S3_PRIORITAS_PTSL_pct",
            SEG_COLORS["S3_PRIORITAS_PTSL"],
            "Jumlah Desa S3 (Prioritas PTSL)",
        )
        k_sorted = k_flt.sort_values([rank_col, pct_col], ascending=[False, False])
    elif "Pemetaan Awal" in mission:
        rank_col, pct_col, bar_col, label_txt = (
            "G6_BELUM_TERPETAKAN",
            "G6_BELUM_TERPETAKAN_pct",
            SEG_COLORS["G6_BELUM_TERPETAKAN"],
            "Jumlah Desa G6 (Nol Persil)",
        )
        k_sorted = k_flt.sort_values([rank_col, pct_col], ascending=[False, False])
    else:
        rank_col, pct_col, bar_col, label_txt = (
            "n_audit_total",
            None,
            SEG_COLORS["G7_ANOMALI_AUDIT"],
            "Total Desa Audit (G7 Eksklusi + Overshoot 1–10x)",
        )
        k_sorted = k_flt.sort_values(["G7_ANOMALI_AUDIT", "n_audit_total"], ascending=[False, False])

    top_k = k_sorted.head(top_n).iloc[::-1]
    y_k = [f"{r['kabupaten']} ({r['provinsi']})" for _, r in top_k.iterrows()]
    if pct_col:
        txt_k = [f"{int(r[rank_col])} desa ({r[pct_col]:.1f}%)" for _, r in top_k.iterrows()]
    else:
        txt_k = [f"{int(r['G7_ANOMALI_AUDIT'])} eksklusi + {int(r['n_overshoot'])} overshoot" for _, r in top_k.iterrows()]

    fig_kab = go.Figure(
        go.Bar(
            x=top_k[rank_col],
            y=y_k,
            orientation="h",
            marker_color=bar_col,
            text=txt_k,
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>" + label_txt + ": %{x:,}<extra></extra>",
        )
    )
    fig_kab.update_layout(
        height=max(360, 32 * len(top_k) + 80),
        margin=dict(l=10, r=110, t=20, b=30),
        xaxis_title=label_txt,
        xaxis=dict(range=[0, max(top_k[rank_col].max() * 1.32, 10)]),
    )
    st.plotly_chart(fig_kab, width="stretch")

    st.subheader(f"Tabel Lengkap Kabupaten/Kota ({len(k_sorted):,} wilayah)")
    display_kab_cols = [
        "kab_key", "kabupaten", "provinsi", "total_desa",
        "S1_PADAT_TRANSISI", "S2_SHM_PARSIAL", "S3_PRIORITAS_PTSL",
        "S4_PERKEBUNAN_HGU", "S5_HAK_PAKAI_AWAL", "G6_BELUM_TERPETAKAN",
        "G7_ANOMALI_AUDIT", "n_overshoot", "S3_PRIORITAS_PTSL_pct", "dominant_segment",
    ]
    st.dataframe(k_sorted[display_kab_cols], width="stretch", hide_index=True)

    st.download_button(
        label="Unduh Tabel Kabupaten/Kota Terfilter (CSV)",
        data=k_sorted.to_csv(index=False).encode("utf-8"),
        file_name="kabupaten_prioritas_filtered.csv",
        mime="text/csv",
    )

# ==============================================================================
# TAB 3: CARI & PROFIL DESA
# ==============================================================================
with tab3:
    st.subheader("Cari & Inspeksi Profil Desa Individual")

    q = st.text_input(
        "Cari kode8, nama desa/kelurahan, kecamatan, kabupaten, atau provinsi (contoh: Arjowilangun, Mulupan, 06010903):",
        value="",
    ).strip()

    if q:
        q_low = q.lower()
        search_mask = (
            flt["kode8"].str.lower().str.contains(q_low, regex=False, na=False)
            | flt["nama"].str.lower().str.contains(q_low, regex=False, na=False)
            | flt["kecamatan"].str.lower().str.contains(q_low, regex=False, na=False)
            | flt["kabupaten"].str.lower().str.contains(q_low, regex=False, na=False)
            | flt["provinsi"].str.lower().str.contains(q_low, regex=False, na=False)
        )
        res_df = flt.loc[search_mask]
    else:
        res_df = flt

    st.caption(f"Ditemukan **{len(res_df):,}** desa/kelurahan (menampilkan 100 baris pertama di tabel).")
    preview_cols = [
        "kode8", "nama", "tipe", "kecamatan", "kabupaten", "provinsi",
        "segment_short", "jumlah_persil", "coverage", "hak_milik_share_luas", "kosong_share_luas",
    ]
    st.dataframe(res_df[preview_cols].head(100), width="stretch", hide_index=True)

    if len(res_df) > 0:
        pick_candidates = res_df.head(100)
        option_labels = {
            row["kode8"]: f"{row['kode8']} — {row['nama']} ({row['tipe']}, {row['kabupaten']}, {row['provinsi']})"
            for _, row in pick_candidates.iterrows()
        }
        chosen_k8 = st.selectbox(
            "Pilih desa untuk melihat Kartu Profil Lengkap:",
            options=list(option_labels.keys()),
            format_func=lambda k: option_labels[k],
        )
        v = res_df[res_df["kode8"] == chosen_k8].iloc[0]

        st.markdown(f"### Kartu Profil: {v['nama']} (`{v['kode8']}`)")
        st.markdown(
            f"**Wilayah:** {v['tipe']} | Kec. {v['kecamatan']}, {v['kabupaten']}, {v['provinsi']}  \n"
            f"**Segmen:** `{v['segment_label']}` *(Status: {v['fit_status']})*  \n"
            f"**Arahan Kebijakan:** {v['arahan_kebijakan']}"
        )

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Luas Desa", f"{v['luas_desa'] / 10000.0:,.1f} ha")
        m2.metric("Jumlah Persil", f"{int(v['jumlah_persil']):,}")
        m3.metric("Coverage Peta", f"{v['coverage']:.3f}" if pd.notna(v["coverage"]) else "N/A")
        m4.metric("Cakupan RDTR", f"{v['rdtr_share'] * 100:.1f}%" if pd.notna(v["rdtr_share"]) else "N/A")
        m5.metric(
            "Stabilitas Bootstrap",
            f"{v['bootstrap_agreement_pct']:.1f}%" if pd.notna(v["bootstrap_agreement_pct"]) else "Non-fit",
        )

        if v["jumlah_persil"] > 0 and pd.notna(v["hak_milik_share_luas"]):
            other_sh = max(
                0.0,
                1.0
                - (
                    float(v["hak_milik_share_luas"])
                    + float(v["kosong_share_luas"])
                    + float(v["hgu_share_luas"])
                    + float(v["hak_pakai_share_luas"])
                    + float(v["hgb_share_luas"])
                ),
            )
            shares_v = pd.DataFrame({
                "Hak": ["Hak Milik", "Kosong", "HGU", "Hak Pakai", "HGB", "Lainnya"],
                "Hak Tanah": ["Hak Milik (SHM)", "Kosong (Belum Hak)", "HGU", "Hak Pakai", "HGB", "Lainnya (<1%)"],
                "Proporsi (%)": [
                    float(v["hak_milik_share_luas"]) * 100.0,
                    float(v["kosong_share_luas"]) * 100.0,
                    float(v["hgu_share_luas"]) * 100.0,
                    float(v["hak_pakai_share_luas"]) * 100.0,
                    float(v["hgb_share_luas"]) * 100.0,
                    other_sh * 100.0,
                ],
            }).iloc[::-1]
            fig_v = go.Figure(
                go.Bar(
                    x=shares_v["Proporsi (%)"],
                    y=shares_v["Hak Tanah"],
                    orientation="h",
                    marker_color=[RIGHT_COLORS[k] for k in shares_v["Hak"]],
                    text=[f"{x:.1f}%" for x in shares_v["Proporsi (%)"]],
                    textposition="outside",
                )
            )
            fig_v.update_layout(
                height=260,
                margin=dict(l=10, r=50, t=25, b=10),
                title="Komposisi Luas Hak Tanah di Desa Ini (%)",
                xaxis=dict(range=[0, 112]),
            )
            st.plotly_chart(fig_v, width="stretch")
        else:
            st.info("Desa ini memiliki **0 persil** atau termasuk **baris anomali** sehingga komposisi hak tanah tidak dihitung.")

        yr_txt = f"{int(v['tahun_median'])}" if pd.notna(v["tahun_median"]) else "Tidak ada (belum bersertifikat)"
        fl_txt = "Ya (nilai 0 di semua kelas — ambigu secara regional)" if bool(v["flood_all_zero"]) else "Tidak (ada area banjir tercatat)"
        st.caption(
            f"Tahun Median Sertifikat: **{yr_txt}** | Overshoot (1–10x): **{'Ya' if bool(v['is_overshoot']) else 'Tidak'}** | "
            f"Flood All-Zero*: **{fl_txt}**"
        )

        export_limit = min(len(res_df), 50000)
        st.download_button(
            label=f"Unduh Hasil Pencarian ({export_limit:,} baris pertama, CSV)",
            data=res_df.head(export_limit).to_csv(index=False).encode("utf-8"),
            file_name="desa_tipologi_filtered.csv",
            mime="text/csv",
        )

# ==============================================================================
# TAB 4: PROFIL 5 SEGMEN (S1-S5)
# ==============================================================================
with tab4:
    st.subheader("Anatomi 5 Segmen Hasil K-Means (k = 5)")

    mp_df = pd.DataFrame(summaries["step4"]["master_profile"])
    mp_df["segment_code"] = mp_df["cluster_id"].map(CLUSTER_TO_SEG)
    mp_df["Segmen"] = mp_df["segment_code"].map(SEG_SHORT)
    mp_df = mp_df.sort_values("segment_code")

    mc_df = pd.DataFrame(summaries["step4"]["mean_composition"])
    cid_by_geng = dict(zip(mp_df["geng"], mp_df["segment_code"]))
    mc_df["segment_code"] = mc_df["geng"].map(cid_by_geng)
    mc_df["Segmen"] = mc_df["segment_code"].map(SEG_SHORT)
    mc_df = mc_df.sort_values("segment_code", ascending=False)

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        fig_comp = go.Figure()
        r_cols = ["Hak Milik", "Kosong", "HGU", "Hak Pakai", "HGB", "Lainnya"]
        for rc in r_cols:
            fig_comp.add_trace(
                go.Bar(
                    name=rc,
                    x=mc_df[rc],
                    y=mc_df["Segmen"],
                    orientation="h",
                    marker_color=RIGHT_COLORS[rc],
                    text=[f"{v:.0f}%" if v >= 8 else "" for v in mc_df[rc]],
                    textposition="inside",
                )
            )
        fig_comp.update_layout(
            barmode="stack",
            height=380,
            margin=dict(l=10, r=10, t=40, b=20),
            title="Rata-rata Komposisi Luas Hak Tanah (%)",
            xaxis=dict(range=[0, 100], title="Proporsi (%)"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_comp, width="stretch")

    with c_p2:
        mp_rev = mp_df.sort_values("segment_code", ascending=False)
        fig_ext = go.Figure()
        for col_e, lbl_e, col_hex in [
            ("Kelurahan%", "% Kelurahan", "#4e79a7"),
            ("rdtr_has%", "% Punya RDTR", "#59a14f"),
            ("overshoot%", "% Overshoot (1–10x)", "#f28e2b"),
            ("flood_all_zero%", "% Flood All-Zero*", "#bab0ac"),
        ]:
            fig_ext.add_trace(
                go.Bar(name=lbl_e, x=mp_rev[col_e], y=mp_rev["Segmen"], orientation="h", marker_color=col_hex)
            )
        fig_ext.update_layout(
            barmode="group",
            height=380,
            margin=dict(l=10, r=10, t=40, b=20),
            title="Indikator Eksternal (*Flood Nol Bersifat Ambigu)",
            xaxis=dict(title="Persentase Desa (%)"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_ext, width="stretch")

    st.info(
        "**Temuan Kunci (*Coverage* vs Komposisi):** `S1: Padat Urban–Transisi` (DKI Jakarta `93,6%`, Bali `89,9%`, DIY `82,6%`) "
        "memiliki kepadatan persil tertinggi (**median `2.088` persil**, **`coverage 0,896`**, RDTR tertinggi `28,1%`) dengan sisa ~31% bidang `Kosong`. "
        "Sebaliknya `S2: SHM Parsial` (Bengkulu `60,7%`, Sulbar `55,3%`) memiliki median SHM `92,4%` di antara persil tergambar, tetapi **`coverage`-nya baru `0,163`** (median `368` persil). "
        "*Catatan Banjir:* Variasi `% Flood All-Zero` (`6,1%` di S4 hingga `38,7%` di S5) mencerminkan pola regional dan **tidak boleh** dibaca sebagai bukti perbedaan bahaya banjir."
    )

    show_mp_cols = [
        "Segmen", "n_desa", "pct_fit", "Kelurahan%", "med_luas_ha", "med_persil",
        "med_coverage", "overshoot%", "med_SHM%", "med_Kosong%", "med_HGU%",
        "med_Pakai%", "rdtr_has%", "med_tahun_min", "med_tahun_median", "med_tahun_max", "flood_all_zero%",
    ]
    st.dataframe(mp_df[show_mp_cols], width="stretch", hide_index=True)

# ==============================================================================
# TAB 5: METODOLOGI & BATASAN JUJUR
# ==============================================================================
with tab5:
    st.subheader("Bukti Validasi Teknis & Keamanan Metodologi")

    s1 = summaries["step1"]
    s3 = summaries["step3"]
    s4 = summaries["step4"]
    prov_assoc = next(a for a in s4["associations"] if a["variabel"] == "provinsi")

    v1, v2, v3, v4, v5 = st.columns(5)
    v1.metric("Hopkins (Simplex Null)", f"{s1['tendency']['hopkins_simplex_null']['mean']:.3f}", "Jauh di atas 0.75")
    v2.metric("Multi-Seed ARI (10x)", f"{s3['multi_seed']['k5']['ari_mean']:.3f}", "Min 0.972")
    v3.metric("Bootstrap ARI (20x)", f"{s3['bootstrap']['k5']['boot_ari_mean']:.3f}", f"{s3['village_stability_k5']['pct_exact_100']:.1f}% tepat 20/20")
    v4.metric("Cramér's V Provinsi", f"{prov_assoc['cramers_v_corr']:.3f}", f"NMI {prov_assoc['nmi']:.3f} (bukan fotokopi)")
    v5.metric("Variant A vs B (ARI)", f"{s3['variant_a_vs_b']['k5']['ari_A_vs_B']:.3f}", "HGU/Kosong/Pakai >93% stabil")

    st.markdown(
        """
### Alur CRISP-DM yang Dijalankan
1. **Business & Data Understanding:** Audit `data/desa.xlsx` (`79.842` baris × `33` kolom), verifikasi identitas struktural hak tanah (`pre_processing/master.ipynb`).
2. **Data Preparation (`data/clustering_ready/`):** Pembuatan fitur *size-neutral*, transformasi akar kuadrat (*Hellinger*), dan penskalaan 5 DoF untuk blok komposisi (`decision_log.csv` D1–D14).
3. **Modeling:** Uji *cluster tendency* (PCA, 3 varian Hopkins), perbandingan **K-Means**, **GMM Full**, dan **HDBSCAN**, dengan **`K-Means (k = 5)`** sebagai pemenang (`Davies-Bouldin 1,060`, `Silhouette 0,294`).
4. **Evaluation:** Uji ketahanan (*multi-seed*, *bootstrap*, Variant A vs B, bobot D11), uji bias geografis, serta profiling independen menggunakan `interpretation_columns.csv`.
5. **Deployment:** Rekonsiliasi penuh **79.842 desa** (`5` segmen model + `1.950` `G6` nol persil + `122` `G7` anomali), agregasi `506` `kab_key`, serta dashboard interaktif ini.

### 4 Batasan Jujur (*Honest Limitations*)
1. **Spektrum Kontinu, bukan Pulau Terpisah:** `S1`–`S2`–`S3` adalah segmentasi kebijakan di atas kontinum SHM ↔ Kosong (terlihat di PCA & HDBSCAN), sedangkan `S4 (HGU)` dan `S5 (Hak Pakai)` membentuk kantong kepadatan nyata.
2. **Sensitivitas Pilihan Desain:** Batas zona transisi `S1` bergeser jika ukuran desa & usia registrasi dimasukkan (**Variant B**, `ARI = 0,645`), dan hasil akan berbeda jika memakai proporsi *jumlah persil* alih-alih *luas persil* (`rho = 0,621`).
3. **Ambiguitas Banjir Nol (`21,8%` desa):** Nilai nol banjir bersifat regional (*not hazardous* vs *not computed*) sehingga tidak dipakai dalam pemodelan dan tidak boleh diklaim sebagai bukti bebas banjir.
4. **Kunci Kabupaten & Asumsi Kolom:** `kab_key` masih membagi Kab. Bogor ke dua kode lama, dan arti kolom sumber (`kosong`, satuan $m^2$, `rdtr_luas`, `banjir_*`, `tahun_*`) menunggu konfirmasi final pemilik data.
"""
    )
