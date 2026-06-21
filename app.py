import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from io import BytesIO

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Myntra Pricing Intel",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── KPI strip ── */
    .kpi-section-title {
        font-size: 13px; font-weight: 700; color: #1A1A2E;
        text-transform: uppercase; letter-spacing: .8px;
        margin: 18px 0 10px; padding-left: 4px;
    }
    .kpi-brand-label-mine {
        display: inline-block; background: #FFF1F4; color: #FF3F6C;
        border: 1.5px solid #FECDD3; border-radius: 20px;
        padding: 3px 12px; font-size: 12px; font-weight: 600;
        margin-bottom: 10px;
    }
    .kpi-brand-label-comp {
        display: inline-block; background: #EFF6FF; color: #3B82F6;
        border: 1.5px solid #BFDBFE; border-radius: 20px;
        padding: 3px 12px; font-size: 12px; font-weight: 600;
        margin-bottom: 10px;
    }
    .kpi-row { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:22px; }
    .kpi-card {
        background:#fff; border:1px solid #ECEEF2; border-radius:12px;
        padding:16px 20px; flex:1; min-width:140px;
        box-shadow:0 1px 3px rgba(0,0,0,.04);
    }
    .kpi-value { font-size:26px; font-weight:700; color:#1A1A2E; margin:0; letter-spacing:-0.5px; }
    .kpi-label { font-size:11px; font-weight:600; color:#8A8FA8; margin:4px 0 0; text-transform:uppercase; letter-spacing:.6px; }
    .kpi-sub   { font-size:12px; color:#6B7280; margin-top:3px; }

    /* ── Side-by-side panel headers ── */
    .panel-hdr {
        font-size:13px; font-weight:600; padding:9px 16px;
        border-radius:10px 10px 0 0; text-align:center;
        letter-spacing:.2px;
    }
    .panel-mine { background:#FFF1F4; color:#FF3F6C; border:1.5px solid #FECDD3; border-bottom:none; }
    .panel-comp { background:#EFF6FF; color:#3B82F6; border:1.5px solid #BFDBFE; border-bottom:none; }

    /* ── Section headers ── */
    .sec-title { font-size:14px; font-weight:600; color:#1A1A2E; margin:22px 0 4px; }
    .sec-sub   { font-size:12px; color:#8A8FA8; margin:0 0 14px; }

    /* ── Alert boxes ── */
    .box-ok   { background:#F0FDF4; border-left:3px solid #22C55E; padding:10px 14px; border-radius:0 8px 8px 0; font-size:13px; color:#1A1A2E; margin-top:8px; line-height:1.6; }
    .box-warn { background:#FFF7ED; border-left:3px solid #F97316; padding:10px 14px; border-radius:0 8px 8px 0; font-size:13px; color:#1A1A2E; margin-top:8px; line-height:1.6; }
    .box-info { background:#EFF6FF; border-left:3px solid #3B82F6; padding:10px 14px; border-radius:0 8px 8px 0; font-size:13px; color:#1A1A2E; margin-top:8px; line-height:1.6; }

    /* ── Sticky grid table ── */
    .grid-wrap {
        overflow-x: auto;
        overflow-y: auto;
        max-height: 520px;
        border-radius: 12px;
        border: 1px solid #ECEEF2;
        margin-top: 8px;
    }
    .pg { width:100%; border-collapse:collapse; font-size:13px; font-family:'Inter',sans-serif; }
    .pg thead tr th {
        position: sticky; top: 0; z-index: 3;
        padding:10px 16px; font-size:11px; font-weight:600; letter-spacing:.4px;
        border:1px solid #ECEEF2; white-space:nowrap;
    }
    .pg th.cat-h {
        background:#F8FAFC; color:#4B5563; text-align:left; min-width:180px;
        position: sticky; top: 0; left: 0; z-index: 4;
    }
    .pg th.my-h  { background:#FFF1F4; color:#FF3F6C; text-align:center; }
    .pg th.co-h  { background:#EFF6FF; color:#3B82F6; text-align:center; }
    .pg td { padding:9px 16px; border:1px solid #ECEEF2; text-align:center;
             font-variant-numeric:tabular-nums; }
    .pg td.cat-td {
        text-align:left; font-weight:500; color:#374151; background:#F8FAFC;
        white-space:nowrap;
        position: sticky; left: 0; z-index: 2;
    }
    .pg td.nil  { color:#CBD5E1; }
    .pg tfoot tr td {
        font-weight:700; background:#F1F5F9;
        position: sticky; bottom: 0; z-index: 2;
        border: 1px solid #ECEEF2;
    }
    .pg tfoot tr td.cat-td {
        position: sticky; left: 0; bottom: 0; z-index: 5;
        background: #E8EDF5;
    }
    .pg tbody tr:hover td { filter:brightness(.95); }

    /* ── Legend pill ── */
    .legend-pill {
        display:inline-flex; align-items:center; gap:6px;
        background:#F8FAFC; border:1px solid #ECEEF2;
        border-radius:20px; padding:4px 12px 4px 8px;
        font-size:12px; color:#374151; margin-right:8px; margin-bottom:8px;
    }
    .dot { width:10px; height:10px; border-radius:50%; display:inline-block; }

    /* ── Misc ── */
    [data-testid="stSidebar"] { background:#FAFAFA; border-right:1px solid #ECEEF2; }
    .stTabs [data-baseweb="tab"] { font-size:13px; font-weight:500; padding:8px 16px; }
    .stTabs [aria-selected="true"] { color:#FF3F6C !important; border-bottom-color:#FF3F6C !important; }
    .divider { border:none; border-top:1px solid #ECEEF2; margin:24px 0; }
    div[data-testid="stDownloadButton"] button {
        padding:4px 10px !important; font-size:12px !important; min-height:0 !important;
        height:28px !important; border-radius:6px !important;
        background:#F4F4F6 !important; border:1px solid #ECEEF2 !important; color:#4B5563 !important;
    }

    /* ── Horizontal scrollable bar chart container ── */
    .chart-scroll-wrap {
        overflow-x: auto;
        border: 1px solid #ECEEF2;
        border-radius: 12px;
        padding: 12px 0 0 0;
        background: #fff;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
MY_COLOR   = "#FF3F6C"
COMP_POOL  = ["#3B82F6","#8B5CF6","#F59E0B","#10B981","#6366F1","#EC4899","#14B8A6","#F97316","#64748B"]

CANONICAL = {
    "link":"Link","subcategory":"Subcategory","brand":"Brand","title":"Title",
    "discount_price":"Discount_Price","mrp":"MRP","image_src":"Image_Src",
    "rating":"Rating","ratings":"Rating","ranking":"Ranking",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def normalise(df_in):
    d = df_in.copy()
    d.columns = [str(c).strip() for c in d.columns]
    d.rename(columns={c: CANONICAL.get(c.lower(), c) for c in d.columns}, inplace=True)
    return d

def clean_df(df_in):
    d = df_in.copy()
    for col in ["Discount_Price","MRP","Ranking"]:
        if col in d.columns:
            d[col] = pd.to_numeric(d[col], errors="coerce")
    if "Rating" in d.columns:
        d["Rating"] = pd.to_numeric(d["Rating"], errors="coerce")
        d.loc[d["Rating"] == 0, "Rating"] = np.nan
    if "Brand" in d.columns:
        d["Brand"] = d["Brand"].astype(str).str.strip().str.upper()
    if "Subcategory" in d.columns:
        d["Subcategory"] = d["Subcategory"].astype(str).str.strip().str.lower()
    return d

def build_color_map(brands, my_set):
    cm = {}; ci = 0
    for b in sorted(brands):
        if b in my_set:
            cm[b] = MY_COLOR
        else:
            cm[b] = COMP_POOL[ci % len(COMP_POOL)]; ci += 1
    return cm

def dl_csv(df_dl, fname):
    st.download_button(
        "⬇ Export CSV",
        df_dl.to_csv(index=False).encode("utf-8-sig"),
        file_name=fname, mime="text/csv",
        key=f"dl_{fname}_{id(df_dl)}"
    )

def price_bg(v, vmin, vmax):
    if pd.isna(v): return "#F8FAFC"
    r = (v - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    if r < 0.5:
        t = r * 2
        return f"rgba({int(134+t*119)},{int(239-t*15)},{int(172-t*101)},0.55)"
    else:
        t = (r - 0.5) * 2
        return f"rgba({int(253-t*5)},{int(224-t*111)},{int(71+t*42)},0.55)"

def rating_bg(v, vmin, vmax):
    if pd.isna(v): return "#F8FAFC"
    r = (v - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    return f"rgba({int(253-r*119)},{int(224+r*15)},{int(71+r*101)},0.55)"

def build_grid_html(pivot_df, my_set, fmt_fn):
    """Render a Category × Brand pivot as a styled HTML table.
    Sticky: header row (top), Subcategory column (left-0),
    each my-brand column (left = cumulative offset), footer row (bottom).
    All sticky cells get an explicit solid background so scrolled content
    does not bleed through.
    """
    vals = pivot_df.values.flatten(); vals = vals[~pd.isna(vals)]
    vmin, vmax = (vals.min(), vals.max()) if len(vals) > 0 else (0, 1)

    # ── Column pixel widths for sticky offset calculation ─────────────────
    SUBCAT_W = 180   # matches min-width on cat-h / cat-td
    MY_COL_W = 145   # width allocated per my-brand sticky column

    my_brand_cols = [c for c in pivot_df.columns if c in my_set]

    def sticky_left(col_name):
        """Return px offset for sticky my-brand columns, or None if not sticky."""
        if col_name not in my_brand_cols:
            return None
        return SUBCAT_W + my_brand_cols.index(col_name) * MY_COL_W

    # ── Header ────────────────────────────────────────────────────────────
    th_cells = [
        f'<th class="cat-h" style="min-width:{SUBCAT_W}px;background:#F8FAFC">Subcategory</th>'
    ]
    for col in pivot_df.columns:
        left = sticky_left(col)
        if left is not None:
            th_cells.append(
                f'<th style="position:sticky;top:0;left:{left}px;z-index:5;'
                f'min-width:{MY_COL_W}px;padding:10px 16px;font-size:11px;font-weight:600;'
                f'letter-spacing:.4px;border:1px solid #ECEEF2;white-space:nowrap;'
                f'background:#FFF1F4;color:#FF3F6C;text-align:center;">{col}</th>'
            )
        else:
            th_cells.append(f'<th class="co-h">{col}</th>')
    header = f'<tr>{"".join(th_cells)}</tr>'

    # ── Body rows ─────────────────────────────────────────────────────────
    body_rows = []
    for cat, row in pivot_df.iterrows():
        tds = [
            f'<td class="cat-td" style="min-width:{SUBCAT_W}px;background:#F8FAFC">'
            f'{str(cat).title()}</td>'
        ]
        for col in pivot_df.columns:
            v    = row[col]
            left = sticky_left(col)
            if pd.isna(v):
                if left is not None:
                    # Sticky nil cell — must have solid bg
                    tds.append(
                        f'<td style="position:sticky;left:{left}px;z-index:2;'
                        f'min-width:{MY_COL_W}px;background:#F8FAFC;'
                        f'color:#CBD5E1;padding:9px 16px;border:1px solid #ECEEF2;text-align:center;">—</td>'
                    )
                else:
                    tds.append('<td class="nil">—</td>')
            else:
                bg, label = fmt_fn(v, vmin, vmax)
                if left is not None:
                    # Sticky data cell — solid opaque background (no rgba transparency)
                    solid_bg = bg.replace("0.55)", "1)") if "rgba" in bg else bg
                    tds.append(
                        f'<td style="position:sticky;left:{left}px;z-index:2;'
                        f'min-width:{MY_COL_W}px;background:{solid_bg};'
                        f'padding:9px 16px;border:1px solid #ECEEF2;'
                        f'text-align:center;font-variant-numeric:tabular-nums;">{label}</td>'
                    )
                else:
                    tds.append(f'<td style="background:{bg}">{label}</td>')
        body_rows.append(f'<tr>{"".join(tds)}</tr>')

    # ── Footer / avg row ──────────────────────────────────────────────────
    avg_tds = [
        f'<td style="position:sticky;left:0;bottom:0;z-index:5;'
        f'min-width:{SUBCAT_W}px;background:#E8EDF5;font-weight:700;'
        f'padding:9px 16px;border:1px solid #ECEEF2;text-align:left;'
        f'color:#374151;">Overall Avg</td>'
    ]
    for col in pivot_df.columns:
        col_vals = pivot_df[col].dropna()
        left     = sticky_left(col)
        if col_vals.empty:
            if left is not None:
                avg_tds.append(
                    f'<td style="position:sticky;left:{left}px;bottom:0;z-index:4;'
                    f'min-width:{MY_COL_W}px;background:#E8EDF5;'
                    f'padding:9px 16px;border:1px solid #ECEEF2;'
                    f'color:#CBD5E1;text-align:center;">—</td>'
                )
            else:
                avg_tds.append('<td class="nil" style="background:#F1F5F9;font-weight:700;">—</td>')
        else:
            v = col_vals.mean()
            bg, label = fmt_fn(v, vmin, vmax)
            if left is not None:
                solid_bg = bg.replace("0.55)", "1)") if "rgba" in bg else bg
                avg_tds.append(
                    f'<td style="position:sticky;left:{left}px;bottom:0;z-index:4;'
                    f'min-width:{MY_COL_W}px;background:{solid_bg};font-weight:700;'
                    f'padding:9px 16px;border:1px solid #ECEEF2;text-align:center;">{label}</td>'
                )
            else:
                avg_tds.append(
                    f'<td style="background:{bg};font-weight:700;'
                    f'padding:9px 16px;border:1px solid #ECEEF2;text-align:center;">{label}</td>'
                )
    footer = f'<tr>{"".join(avg_tds)}</tr>'

    return (
        f'<div class="grid-wrap">'
        f'<table class="pg">'
        f'<thead>{header}</thead>'
        f'<tbody>{"".join(body_rows)}</tbody>'
        f'<tfoot>{footer}</tfoot>'
        f'</table></div>'
    )

# (No sample data — upload required)

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🛍️ Myntra Pricing Intel")
    st.markdown("---")

    st.markdown("**📂 Upload your Excel file**")
    st.caption("Sheet A = Competitor products · Sheet B = Your brand(s)")
    uf = st.file_uploader("xlsx", type=["xlsx","xls"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Your brand name(s)**")
    st.caption("Comma-separated · case-insensitive · must match exactly as in Sheet B")
    brand_input = st.text_input(
        "brands", value="LONDON RAG, RAG & CO",
        label_visibility="collapsed",
        placeholder="e.g. LONDON RAG, RAG & CO",
    )
    my_set = {b.strip().upper() for b in brand_input.split(",") if b.strip()}

    # ── Load data ──────────────────────────────────────────────────────────
    if uf:
        raw = uf.read()
        try:
            xls    = pd.ExcelFile(BytesIO(raw), engine="openpyxl")
            snames = xls.sheet_names
            sa = next(
                (s for s in snames if s.lower().replace(" ","") in
                 ["sheeta","a","competitors","competitor","comp"]),
                snames[0]
            )
            sb = next(
                (s for s in snames if s.lower().replace(" ","") in
                 ["sheetb","b","mybrand","mybrands","brand","brands"]),
                snames[min(1, len(snames)-1)]
            )
            df_a = normalise(pd.read_excel(BytesIO(raw), sheet_name=sa, engine="openpyxl"))
            df_b = normalise(pd.read_excel(BytesIO(raw), sheet_name=sb, engine="openpyxl"))
            st.success(f"✅ **{sa}**: {len(df_a)} rows · **{sb}**: {len(df_b)} rows")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.stop()
    else:
        st.warning("⬆️ Please upload your XLSX file above to get started.")
        st.stop()

    df_a = clean_df(df_a); df_b = clean_df(df_b)
    df_a["Source"] = "Competitor"
    df_b["Source"] = "My Brand"
    if "Ranking" not in df_b.columns:
        df_b["Ranking"] = np.nan

    df_all = pd.concat([df_a, df_b], ignore_index=True)
    df_all = df_all.dropna(subset=["Brand","Discount_Price"])
    df_all["Is_My"] = df_all["Brand"].isin(my_set)
    df_all["Discount_Pct"] = np.where(
        df_all["MRP"] > 0,
        ((df_all["MRP"] - df_all["Discount_Price"]) / df_all["MRP"] * 100).round(1),
        np.nan
    )

    # ── Filters ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Filter by Subcategory**")
    all_cats = sorted(df_all["Subcategory"].dropna().unique())
    ca, cb = st.columns(2)
    if ca.button("All", use_container_width=True, key="ca"):
        st.session_state.sel_cats = list(all_cats)
    if cb.button("None", use_container_width=True, key="cn"):
        st.session_state.sel_cats = []
    if "sel_cats" not in st.session_state:
        st.session_state.sel_cats = list(all_cats)
    sel = st.multiselect("cats", all_cats, key="sel_cats", label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Filter by Other Brands (competitors)**")
    st.caption("Controls which competitor brands appear across the whole dashboard. Your own brand(s) are always shown.")
    all_comp_brands = sorted(df_all.loc[~df_all["Is_My"], "Brand"].dropna().unique())
    ba, bn = st.columns(2)
    if ba.button("All", use_container_width=True, key="ba"):
        st.session_state.sel_comp_brands = list(all_comp_brands)
    if bn.button("None", use_container_width=True, key="bn"):
        st.session_state.sel_comp_brands = []
    if "sel_comp_brands" not in st.session_state:
        st.session_state.sel_comp_brands = list(all_comp_brands)
    sel_brands = st.multiselect("comp_brands", all_comp_brands, key="sel_comp_brands", label_visibility="collapsed")

    df = df_all[df_all["Subcategory"].isin(sel)].copy() if sel else df_all.copy()
    df = df[df["Is_My"] | df["Brand"].isin(sel_brands)].copy()
    df_mine = df[df["Is_My"]].copy()
    df_comp = df[~df["Is_My"]].copy()

    st.markdown("---")
    st.caption(f"**{len(df_comp)}** competitor products · **{df_comp['Brand'].nunique() if not df_comp.empty else 0}** brands")
    st.caption(f"**{len(df_mine)}** your brand products · **{df_mine['Brand'].nunique() if not df_mine.empty else 0}** brands")

# ── Color map ─────────────────────────────────────────────────────────────────
color_map = build_color_map(df["Brand"].unique().tolist(), my_set)

# ════════════════════════════════════════════════════════════════════════════
# HEADER + KPI STRIP — Per Brand
# ════════════════════════════════════════════════════════════════════════════
st.markdown("# Myntra Pricing Intelligence")

if df.empty:
    st.warning("No data matches your filters. Adjust the sidebar.")
    st.stop()

c_avg  = df_comp["Discount_Price"].mean() if not df_comp.empty else 0
c_med  = df_comp["Discount_Price"].median() if not df_comp.empty else 0
c_disc = df_comp["Discount_Pct"].mean() if not df_comp.empty else 0

# ── KPI for each of MY brands ─────────────────────────────────────────────
my_brands_list = sorted([b for b in my_set if b in df["Brand"].unique()])

for brand_name in my_brands_list:
    brand_df = df_mine[df_mine["Brand"] == brand_name]
    if brand_df.empty:
        continue

    b_avg = brand_df["Discount_Price"].mean()
    b_med = brand_df["Discount_Price"].median()
    b_rating = brand_df["Rating"].mean() if "Rating" in brand_df.columns else np.nan
    b_off = brand_df["Discount_Pct"].mean() if "Discount_Pct" in brand_df.columns else np.nan
    b_count = len(brand_df)

    dp    = ((b_avg - c_avg) / c_avg * 100) if c_avg > 0 else 0
    sgn   = "+" if dp >= 0 else ""
    pc    = "#F97316" if dp > 3 else ("#22C55E" if dp < -3 else "#10B981")
    pl    = "above" if dp > 0 else "below"

    rating_str = f"⭐ {b_rating:.2f}" if not pd.isna(b_rating) else "N/A"
    off_str    = f"{b_off:.1f}%" if not pd.isna(b_off) else "N/A"

    st.markdown(f'<div class="kpi-brand-label-mine">📦 {brand_name}</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card" style="border-top:3px solid {pc}">
    <p class="kpi-value" style="color:{pc}">{sgn}{dp:.1f}%</p>
    <p class="kpi-label">vs. Market Avg</p>
    <p class="kpi-sub">{'↑' if dp>0 else '↓'} {abs(dp):.1f}% {pl} competitor avg</p>
  </div>
  <div class="kpi-card" style="border-top:3px solid {MY_COLOR}">
    <p class="kpi-value" style="color:{MY_COLOR}">₹{b_avg:,.0f}</p>
    <p class="kpi-label">Avg Sale Price</p>
    <p class="kpi-sub">Median ₹{b_med:,.0f}</p>
  </div>
  <div class="kpi-card" style="border-top:3px solid #8B5CF6">
    <p class="kpi-value" style="color:#8B5CF6">{rating_str}</p>
    <p class="kpi-label">Avg Rating</p>
    <p class="kpi-sub">{b_count} products listed</p>
  </div>
  <div class="kpi-card" style="border-top:3px solid #F59E0B">
    <p class="kpi-value" style="color:#F59E0B">{off_str}</p>
    <p class="kpi-label">Avg Discount %</p>
    <p class="kpi-sub">Competitor avg: {c_disc:.1f}%</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Competitor summary KPI ─────────────────────────────────────────────────
st.markdown('<div class="kpi-brand-label-comp">🏷️ COMPETITOR MARKET</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card" style="border-top:3px solid #3B82F6">
    <p class="kpi-value">₹{c_avg:,.0f}</p>
    <p class="kpi-label">Competitor Avg Price</p>
    <p class="kpi-sub">Median ₹{c_med:,.0f}</p>
  </div>
  <div class="kpi-card" style="border-top:3px solid #3B82F6">
    <p class="kpi-value">{df_comp['Brand'].nunique() if not df_comp.empty else 0}</p>
    <p class="kpi-label">Competitor Brands</p>
    <p class="kpi-sub">{len(df_comp)} products</p>
  </div>
  <div class="kpi-card" style="border-top:3px solid #3B82F6">
    <p class="kpi-value">{df_comp['Subcategory'].nunique() if not df_comp.empty else 0}</p>
    <p class="kpi-label">Categories Tracked</p>
    <p class="kpi-sub">Across all competitor data</p>
  </div>
  <div class="kpi-card" style="border-top:3px solid #3B82F6">
    <p class="kpi-value">{c_disc:.1f}%</p>
    <p class="kpi-label">Competitor Avg Discount</p>
    <p class="kpi-sub">Avg markdown from MRP</p>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tab1, tab2 = st.tabs([
    "📋 Side-by-Side",
    "📐 Category × Brand Grid",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — SIDE-BY-SIDE
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="sec-title">My Brand vs. Competitors — product by product</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Select a subcategory to compare within the same segment. Both panels sorted by sale price (low → high). Scroll right inside each panel to see all columns — Photo and Brand columns stay pinned.</p>', unsafe_allow_html=True)

    cat_opts = ["All categories"] + list(all_cats)
    t1_cat   = st.selectbox("Subcategory", cat_opts, key="t1_cat")

    t1m = df_mine.copy(); t1c = df_comp.copy()
    if t1_cat != "All categories":
        t1m = t1m[t1m["Subcategory"] == t1_cat]
        t1c = t1c[t1c["Subcategory"] == t1_cat]
    t1m = t1m.sort_values("Discount_Price").reset_index(drop=True)
    t1c = t1c.sort_values("Discount_Price").reset_index(drop=True)

    # ── Exclude Ranking from side-by-side ─────────────────────────────────
    SHOW_COLS = [c for c in
                 ["Image_Src","Brand","Title","Subcategory","Discount_Price","MRP","Discount_Pct","Rating"]
                 if c in df.columns]

    COL_CFG = {
        "Image_Src":      st.column_config.ImageColumn("Photo", width="small"),
        "Brand":          st.column_config.TextColumn("Brand", width="small"),
        "Title":          st.column_config.TextColumn("Title", width="medium"),
        "Subcategory":    st.column_config.TextColumn("Category", width="small"),
        "Discount_Price": st.column_config.NumberColumn("Sale ₹",  format="₹%.0f"),
        "MRP":            st.column_config.NumberColumn("MRP ₹",   format="₹%.0f"),
        "Discount_Pct":   st.column_config.NumberColumn("Off %",   format="%.1f%%"),
        "Rating":         st.column_config.NumberColumn("Rating ⭐", format="%.1f"),
    }

    # Use full-width single columns with 50% each for maximum width
    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown(
            f'<div class="panel-hdr panel-mine">⭐ YOUR BRANDS — {len(t1m)} products</div>',
            unsafe_allow_html=True
        )
        if t1m.empty:
            st.info("No products in this filter.")
        else:
            sm = [c for c in SHOW_COLS if c in t1m.columns]
            try:
                st.dataframe(
                    t1m[sm],
                    column_config={k: v for k, v in COL_CFG.items() if k in sm},
                    use_container_width=True,
                    hide_index=True,
                    height=max(200, min(1000, len(t1m) * 63 + 38)),
                    row_height=60,
                    column_order=sm,
                )
            except TypeError:
                st.dataframe(
                    t1m[sm],
                    column_config={k: v for k, v in COL_CFG.items() if k in sm},
                    use_container_width=True,
                    hide_index=True,
                    height=max(200, min(1000, len(t1m) * 63 + 38)),
                )

    with col_r:
        st.markdown(
            f'<div class="panel-hdr panel-comp">🏷️ COMPETITORS — {len(t1c)} products</div>',
            unsafe_allow_html=True
        )
        if t1c.empty:
            st.info("No products in this filter.")
        else:
            sc = [c for c in SHOW_COLS if c in t1c.columns]
            try:
                st.dataframe(
                    t1c[sc],
                    column_config={k: v for k, v in COL_CFG.items() if k in sc},
                    use_container_width=True,
                    hide_index=True,
                    height=max(200, min(1000, len(t1c) * 63 + 38)),
                    row_height=60,
                    column_order=sc,
                )
            except TypeError:
                st.dataframe(
                    t1c[sc],
                    column_config={k: v for k, v in COL_CFG.items() if k in sc},
                    use_container_width=True,
                    hide_index=True,
                    height=max(200, min(1000, len(t1c) * 63 + 38)),
                )

    if not t1m.empty and not t1c.empty:
        gap = t1m["Discount_Price"].mean() - t1c["Discount_Price"].mean()
        if gap > 200:
            st.markdown(
                f'<div class="box-warn">⚠️ In <b>{t1_cat if t1_cat != "All categories" else "this selection"}</b>, '
                f'your brand avg is <b>₹{abs(gap):,.0f} above</b> competitor avg. '
                f'Competitor avg: ₹{t1c["Discount_Price"].mean():,.0f} · Yours: ₹{t1m["Discount_Price"].mean():,.0f}</div>',
                unsafe_allow_html=True
            )
        elif gap < -200:
            st.markdown(
                f'<div class="box-ok">💚 In <b>{t1_cat if t1_cat != "All categories" else "this selection"}</b>, '
                f'your brand avg is <b>₹{abs(gap):,.0f} below</b> competitor avg — '
                f'potential room to improve margins. '
                f'Competitor avg: ₹{t1c["Discount_Price"].mean():,.0f} · Yours: ₹{t1m["Discount_Price"].mean():,.0f}</div>',
                unsafe_allow_html=True
            )

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — CATEGORY × BRAND GRID
# ════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown(
        '<span class="legend-pill"><span class="dot" style="background:#FFF1F4;border:1.5px solid #FECDD3"></span> Pink header = your brand</span>'
        '<span class="legend-pill"><span class="dot" style="background:#EFF6FF;border:1.5px solid #BFDBFE"></span> Blue header = competitor</span>'
        '<span class="legend-pill"><span class="dot" style="background:#86EFAC"></span> Lower value</span>'
        '<span class="legend-pill"><span class="dot" style="background:#F87171"></span> Higher value</span>'
        '<span class="legend-pill" style="background:#FFF7ED;border-color:#FDE68A">📌 Subcategory & headers stay pinned while scrolling</span>',
        unsafe_allow_html=True
    )

    # ── Price grid ────────────────────────────────────────────────────────
    st.markdown('<p class="sec-title">Average Discount Price — Category × Brand</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Scroll right → to see all brands · Scroll down ↓ to see all categories · Subcategory column and headers stay pinned</p>', unsafe_allow_html=True)

    pivot_p = df.groupby(["Subcategory","Brand"])["Discount_Price"].mean().round(0).unstack("Brand")
    my_cols = sorted([c for c in pivot_p.columns if c in my_set])
    co_cols = sorted([c for c in pivot_p.columns if c not in my_set])
    pivot_p = pivot_p[my_cols + co_cols].sort_index()

    def fmt_price(v, vmin, vmax):
        return price_bg(v, vmin, vmax), f"₹{int(v):,}"

    st.markdown(build_grid_html(pivot_p, my_set, fmt_price), unsafe_allow_html=True)
    st.markdown("")
    dl_csv(pivot_p.reset_index(), "grid_avg_price.csv")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Rating grid ───────────────────────────────────────────────────────
    st.markdown('<p class="sec-title">Average Rating — Category × Brand</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Scroll right → to see all brands · Scroll down ↓ to see all categories · Subcategory column and headers stay pinned · Ratings of 0 excluded · Higher rating = deeper green</p>', unsafe_allow_html=True)

    pivot_r = df.groupby(["Subcategory","Brand"])["Rating"].mean().round(2).unstack("Brand")
    pivot_r = pivot_r[[c for c in my_cols if c in pivot_r.columns] +
                       [c for c in co_cols if c in pivot_r.columns]].sort_index()

    def fmt_rating(v, vmin, vmax):
        return rating_bg(v, vmin, vmax), f"⭐ {v:.2f}"

    st.markdown(build_grid_html(pivot_r, my_set, fmt_rating), unsafe_allow_html=True)
    st.markdown("")
    dl_csv(pivot_r.reset_index(), "grid_avg_rating.csv")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Discount % grid ───────────────────────────────────────────────────
    st.markdown('<p class="sec-title">Average Discount % — Category × Brand</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Scroll right → to see all brands · Higher % = deeper markdown from MRP</p>', unsafe_allow_html=True)

    pivot_d = df.groupby(["Subcategory","Brand"])["Discount_Pct"].mean().round(1).unstack("Brand")
    pivot_d = pivot_d[[c for c in my_cols if c in pivot_d.columns] +
                       [c for c in co_cols if c in pivot_d.columns]].sort_index()

    def fmt_disc(v, vmin, vmax):
        return price_bg(v, vmin, vmax), f"{v:.1f}%"

    st.markdown(build_grid_html(pivot_d, my_set, fmt_disc), unsafe_allow_html=True)
    st.markdown("")
    dl_csv(pivot_d.reset_index(), "grid_avg_discount_pct.csv")

    st.markdown(
        '<p style="font-size:12px;color:#8A8FA8;margin-top:20px">'
        'Myntra Pricing Intel · Upload Sheet A (competitors) + Sheet B (your brand) in one XLSX weekly for trend tracking</p>',
        unsafe_allow_html=True
    )
