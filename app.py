"""
dashboard/app.py
=================
Main Streamlit entry point.

Two top-level tabs:
  📊 Dashboard     — existing analysis dashboard
  🔬 Policy Simulation — new policy simulation module
"""

import sys
import pandas as pd
import importlib.metadata
import streamlit as st

packages = sorted([
    (dist.metadata["Name"], dist.version)
    for dist in importlib.metadata.distributions()
])

# Debug-only metadata logging is disabled so the UI stays clean.
# st.write(packages)
# st.write(sys.version)

from config import FACTOR_LABELS
from dashboard.filters import load_all_data, render_sidebar, apply_filters
from dashboard.charts import (
    classification_bar, factor_avg_bar, mci_scatter,
    wsi_wei_quadrant, cluster_centroid_chart,
    rf_importance_bar, spearman_heatmap,
)
from dashboard.area_detail import render_area_detail
from dashboard.chatbot import render_chatbot
from dashboard.simulation_page import render_simulation_page

st.set_page_config(
    page_title="MCI — Digital Desert Index",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        color-scheme: dark;
        font-family: 'Inter', sans-serif;
        background-color: #020408;
        color: #e5e7eb;
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .main {
        background-color: #020408 !important;
        color: #e5e7eb !important;
        font-family: 'Inter', sans-serif !important;
    }

    body::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image: radial-gradient(circle at 22% 14%, rgba(77, 210, 255, 0.14), transparent 18%),
                          radial-gradient(circle at 84% 8%, rgba(255, 163, 61, 0.10), transparent 20%),
                          linear-gradient(180deg, rgba(255,255,255,0.02) 0%, transparent 18%),
                          repeating-linear-gradient(0deg, rgba(255,255,255,0.035) 0px, rgba(255,255,255,0.035) 1px, transparent 2px, transparent 4px);
        pointer-events: none;
        opacity: 0.16;
        z-index: 9999;
        mix-blend-mode: screen;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020408 0%, #071017 100%) !important;
        border-right: 1px solid rgba(77, 210, 255, 0.18) !important;
        box-shadow: inset 2px 0 20px rgba(77, 210, 255, 0.08);
    }

    [data-testid="stSidebar"] .css-1d391kg, [data-testid="stSidebar"] .css-1d6wzja {
        background: transparent !important;
    }

    .css-18e3th9 { padding-top: 1rem !important; }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    .stMarkdown strong, .stMarkdown span, .stMarkdown p {
        font-family: 'Sora', 'Inter', sans-serif !important;
        color: #f8fafc !important;
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        letter-spacing: 0.18em !important;
        text-transform: uppercase !important;
    }

    .metric-label,
    .metric-value,
    .stMetric > div {
        font-family: 'JetBrains Mono', monospace !important;
        letter-spacing: 0.04em !important;
    }

    [data-testid="metric-container"] {
        background: rgba(8, 12, 18, 0.92) !important;
        border: 1px solid rgba(77, 210, 255, 0.16) !important;
        box-shadow: 0 0 30px rgba(77, 210, 255, 0.06) !important;
        border-radius: 12px !important;
    }

    [data-testid="metric-container"] .metric-label,
    [data-testid="metric-container"] .metric-value {
        color: #e5e7eb !important;
    }

    .stButton>button, .stDownloadButton>button {
        background: rgba(5, 9, 15, 0.95) !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(77, 210, 255, 0.18) !important;
        box-shadow: inset 0 0 0 1px rgba(77, 210, 255, 0.06), 0 0 24px rgba(77, 210, 255, 0.08) !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stButton>button:hover, .stDownloadButton>button:hover {
        border-color: #4dd2ff !important;
        box-shadow: inset 0 0 0 1px rgba(77, 210, 255, 0.12), 0 0 30px rgba(77, 210, 255, 0.16) !important;
    }

    .css-1d391kg, .css-1d6wzja, .css-1tqdw7f, .css-1q8dd3e, .css-12w0q3s {
        background-color: rgba(10, 12, 18, 0.95) !important;
        border-color: rgba(77, 210, 255, 0.14) !important;
        border-radius: 12px !important;
        box-shadow: inset 0 0 24px rgba(0, 0, 0, 0.25) !important;
    }

    .stSelectbox div[data-baseweb="select"] input,
    .stTextInput input,
    .stNumberInput input,
    .stSlider>div>div>div>div,
    .stCheckbox>div>label,
    .stRadio>div {
        background: rgba(6, 10, 16, 0.95) !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(77, 210, 255, 0.16) !important;
    }

    .stSidebar [data-testid="stMarkdownContainer"] h2, .stSidebar [data-testid="stMarkdownContainer"] h3 {
        color: #9aedff !important;
        font-family: 'Sora', sans-serif !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
    }

    .stSidebar [data-testid="stMarkdownContainer"] p,
    .stSidebar [data-testid="stMarkdownContainer"] span {
        color: #cbd5e1 !important;
        font-family: 'Inter', sans-serif !important;
    }

    .sidebar-panel {
        background: rgba(11, 15, 22, 0.92);
        border: 1px solid rgba(77, 210, 255, 0.16);
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .sidebar-title {
        color: #4dd2ff;
        font-family: 'Sora', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        margin-bottom: 0.6rem;
        font-size: 0.82rem;
    }

    .sidebar-subtitle {
        color: #a8bcec;
        font-family: 'Inter', sans-serif;
        font-size: 0.86rem;
        line-height: 1.5;
    }

    .hud-card { background: linear-gradient(180deg, rgba(8, 12, 18, 0.94), rgba(5, 9, 16, 0.92)); border: 1px solid rgba(77, 210, 255, 0.28); border-radius: 16px; padding: 1.3rem; margin-bottom: 1.3rem; box-shadow: 0 0 45px rgba(77, 210, 255, 0.12), inset 0 0 28px rgba(77, 210, 255, 0.08); }
    .hud-card h2 { margin: 0 0 0.35rem; font-size: 1rem; font-family: 'Sora', sans-serif; color: #8efaff; letter-spacing: 0.18em; text-transform: uppercase; text-shadow: 0 0 14px rgba(77, 210, 255, 0.32); }
    .hud-card p { margin: 0; color: #c9e6ff; font-family: 'Inter', sans-serif; }
    .hud-card-panel { background: linear-gradient(135deg, rgba(77, 210, 255, 0.14), rgba(23, 44, 70, 0.85)); border: 1px solid rgba(77, 210, 255, 0.22); border-radius: 14px; padding: 0.95rem 1rem; min-width: 160px; }
    .hud-card-panel strong { color: #d7f7ff; }
    .hud-divider { display: block; height: 1px; margin: 1rem 0; background: linear-gradient(90deg, transparent, rgba(77,210,255,0.45), transparent); }
    .hud-scoreboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.1rem; }
    .stTabs [role="tab"] { font-family: 'Sora', sans-serif !important; text-transform: uppercase !important; letter-spacing: 0.18em !important; color: #ccd6f6 !important; border-radius: 12px !important; }
    .stTabs [role="tab"][aria-selected="true"] { background: rgba(77,210,255,0.12) !important; box-shadow: 0 0 22px rgba(77,210,255,0.18) !important; border: 1px solid rgba(77,210,255,0.28) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

tab_dashboard, tab_simulation = st.tabs(["📊 Dashboard", "🔬 Policy Simulation"])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

with tab_dashboard:

    data          = load_all_data()
    scores_df     = data["scores"]
    timeseries_df = data["timeseries"]
    sub_df        = data["subcomponents"]
    imp_df        = data["importance"]
    cluster_df    = data["clusters"]

    filters     = render_sidebar(scores_df)
    filtered_df = apply_filters(scores_df, filters)
    n_total     = len(filtered_df)

    st.markdown(
        """
        <div class='hud-card'>
            <div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;'>
                <div>
                    <div style='font-size:0.8rem;letter-spacing:0.22em;color:#4dd2ff;margin-bottom:0.65rem;'>SIGNAL | DIGITAL DESERT COMMAND CENTER</div>
                    <div style='font-size:2.15rem;font-weight:700;color:#f8fbff;line-height:1.05;'>DIGITAL DESERT DASHBOARD</div>
                    <div style='margin-top:0.55rem;font-size:0.95rem;color:#b4c6dd;max-width:760px;'>Minimum Connectivity Index (MCI) operations hub for cross-state and district intelligence, policy simulation, and AI command analytics.</div>
                </div>
                <div style='display:grid;grid-template-columns:repeat(2,minmax(160px,1fr));gap:0.75rem;margin-top:1rem;'>
                    <div class='hud-card-panel'>
                        <div style='font-size:0.7rem;letter-spacing:0.22em;color:#9aedff;text-transform:uppercase;'>Granularity</div>
                        <div style='font-size:1.1rem;font-weight:700;color:#f8fbff;margin-top:0.45rem;'>State × District</div>
                    </div>
                    <div class='hud-card-panel'>
                        <div style='font-size:0.7rem;letter-spacing:0.22em;color:#d0d8ff;text-transform:uppercase;'>Data posture</div>
                        <div style='font-size:1.1rem;font-weight:700;color:#b3f0ff;margin-top:0.45rem;'>Neon command</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='hud-divider'></div>", unsafe_allow_html=True)

    st.markdown("#### DATA COMMAND METRICS", unsafe_allow_html=True)
    st.markdown(
        "**Minimum Connectivity Index (MCI)** — identifying digital deserts "
        "and their impact on women's safety and employment across India.  \n"
        "Granularity: **State × District**"
    )
    st.markdown("---")

    # ── KPI row ───────────────────────────────────────────────────────────────
    n_deserts = len(
        filtered_df[filtered_df["MCI_class"].isin(["Severe desert", "Moderate desert"])]
    )
    n_severe  = len(filtered_df[filtered_df["MCI_class"] == "Severe desert"])
    avg_mci   = filtered_df["MCI"].mean() if n_total else 0.0
    avg_wsi   = filtered_df["WSI"].mean() if n_total else 0.0
    avg_wei   = filtered_df["WEI"].mean() if n_total else 0.0
    high_risk = (
        len(filtered_df[filtered_df["Safety_risk"] == "High safety risk"])
        if "Safety_risk" in filtered_df.columns else 0
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Districts",        n_total)
    c2.metric("Digital deserts",  n_deserts,
              delta=f"{n_severe} severe", delta_color="inverse")
    c3.metric("Avg MCI",          f"{avg_mci:.1f}")
    c4.metric("Avg WSI",          f"{avg_wsi:.1f}",
              help="Women Safety Index — lower = higher risk")
    c5.metric("Avg WEI",          f"{avg_wei:.1f}",
              help="Women Employment Index — lower = fewer opportunities")
    c6.metric("High safety risk", high_risk, delta_color="inverse")
    st.markdown("---")

    # ── Row 1: Classification + Factor averages ───────────────────────────────
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### District classification breakdown")
        if n_total:
            st.plotly_chart(classification_bar(filtered_df), use_container_width=True)
    with col_r:
        st.markdown("#### Average factor scores")
        if n_total:
            st.plotly_chart(factor_avg_bar(filtered_df), use_container_width=True)

    # ── Row 2: MCI scatter + WSI/WEI quadrant ────────────────────────────────
    col_l2, col_r2 = st.columns(2)
    with col_l2:
        st.markdown("#### MCI by district")
        if n_total:
            st.plotly_chart(mci_scatter(filtered_df), use_container_width=True, config={"displayModeBar": False})
    with col_r2:
        st.markdown("#### WSI vs WEI — women impact quadrant")
        if n_total and "WSI" in filtered_df.columns:
            st.plotly_chart(wsi_wei_quadrant(filtered_df), use_container_width=True, config={"displayModeBar": False})

    # ── Row 3: District table ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### District-level scores")
    if n_total:
        display_cols = [
            "districtname", "statename",
            "MCI", "IFS", "DLS", "SES", "WDI", "WSI", "WEI",
            "MCI_class", "cluster_label",
        ]
        display_cols = [c for c in display_cols if c in filtered_df.columns]
        table_df = filtered_df[display_cols].copy().rename(columns={
            "districtname":  "District",
            "statename":     "State",
            "cluster_label": "Cluster profile",
        })
        score_cols = [c for c in ["MCI","IFS","DLS","SES","WDI","WSI","WEI"]
                      if c in table_df.columns]

        def _color_score(val):
            try:
                v = float(val)
            except (TypeError, ValueError):
                return ""
            if v < 25:   c = "#E24B4A"
            elif v < 45: c = "#EF9F27"
            elif v < 60: c = "#378ADD"
            elif v < 75: c = "#639922"
            else:        c = "#1D9E75"
            return f"background-color:{c}18;color:{c};font-weight:500"

        st.dataframe(
            table_df.style.applymap(_color_score, subset=score_cols),
            use_container_width=True, height=320,
        )
    else:
        st.info("No districts match the current filters.")

    # ── Row 4: Drill-down ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### District drill-down")
    selected_area_scores = None

    if n_total:
        filtered_df["_select_label"] = (
            filtered_df["districtname"] + "  (" + filtered_df["statename"] + ")"
        )
        selected_label = st.selectbox(
            "Select district to inspect",
            ["— select —"] + filtered_df["_select_label"].tolist(),
        )
        if selected_label != "— select —":
            row = filtered_df[filtered_df["_select_label"] == selected_label]
            if not row.empty:
                area_row_dict        = row.iloc[0].to_dict()
                selected_area_scores = area_row_dict
                render_area_detail(
                    area_row=area_row_dict,
                    sub_df=sub_df,
                    timeseries_df=timeseries_df,
                )

    # ── Row 5: Cluster profiles ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Connectivity profile clusters")
    if not cluster_df.empty:
        st.plotly_chart(cluster_centroid_chart(cluster_df), use_container_width=True)
        CLUSTER_COLORS = [
            "#E24B4A","#EF9F27","#378ADD","#7F77DD","#1D9E75","#639922","#D4537E",
        ]
        n_cls = min(3, len(cluster_df))
        c_cols = st.columns(n_cls)
        for i, (_, cl) in enumerate(cluster_df.iterrows()):
            cc = CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
            with c_cols[i % n_cls]:
                st.markdown(
                    f"<div style='border-left:3px solid {cc};padding:.6rem .8rem;"
                    f"background:{cc}08;border-radius:0 8px 8px 0;margin-bottom:8px'>"
                    f"<div style='font-size:13px;font-weight:600;color:{cc}'>"
                    f"{cl['label']}</div>"
                    f"<div style='font-size:11px;color:gray;margin:.3rem 0'>"
                    f"{cl['area_count']} district{'s' if cl['area_count']!=1 else ''} · "
                    f"avg score {cl['mean_score']:.0f}</div>"
                    f"<div style='font-size:12px;margin-bottom:.4rem'>"
                    f"{cl['intervention']}</div>"
                    f"<div style='font-size:11px;color:gray'>"
                    f"Districts: {cl['area_list']}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # ── Row 6: RF importance ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Intervention levers — random forest feature importance")
    st.caption(
        "Variables ranked by contribution to predicting MCI. "
        "Higher importance = higher-leverage policy intervention target."
    )
    if not imp_df.empty:
        st.plotly_chart(rf_importance_bar(imp_df), use_container_width=True)
        st.info(
            "**Key finding:** No-phone household rate and illiteracy are the top "
            "predictors of MCI in this dataset — physical access and structural "
            "literacy are the primary barriers, not just network infrastructure."
        )

    # ── Row 7: Spearman heatmap ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Factor Spearman correlation matrix")
    st.caption(
        "High DLS↔WDI and DLS↔SES correlation is expected — "
        "kept separate for policy-narrative clarity."
    )
    if n_total >= 5:
        st.plotly_chart(spearman_heatmap(filtered_df), use_container_width=True)

    # ── Chatbot ───────────────────────────────────────────────────────────────
    render_chatbot(selected_area_scores=selected_area_scores)

    st.markdown("---")
    st.caption(
        "MCI = weighted geometric mean: IFS×0.35, DLS×0.30, SES×0.20, WDI×0.15. "
        "Normalisation anchored to baseline year p5/p95. "
        "Granularity: state × district. "
        "Chatbot: Mistral + LLaMA 3.1 via Ollama."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — POLICY SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

with tab_simulation:
    render_simulation_page()