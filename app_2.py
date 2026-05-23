"""
dashboard/app_2.py
===================
Premium neon AI command center redesign for the Digital Desert dashboard.
This version refocuses the analytics experience into a matte black, glassmorphism,
neon-cyber command center with polished MCI and WSI/WEI widgets.
"""

import sys
import pandas as pd
import importlib.metadata
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import FACTOR_LABELS
from dashboard.filters import load_all_data, render_sidebar, apply_filters
from dashboard.area_detail import render_area_detail
from dashboard.simulation_page import render_simulation_page

TRANSPARENT = "rgba(0,0,0,0)"
BG_COLOR = "#03060f"
CARD_BG = "rgba(8, 12, 22, 0.80)"
BORDER_BG = "rgba(77, 210, 255, 0.18)"
NEON_CYAN = "#4dd2ff"
NEON_PURPLE = "#9d7cff"
NEON_ORANGE = "#fb923c"
NEON_GREEN = "#22c55e"
NEON_YELLOW = "#facc15"
NEON_RED = "#f43f5e"
AXIS_COLOR = "#9bb7d8"
GRID_COLOR = "rgba(157, 191, 221, 0.12)"
FONT_FAMILY = "Orbitron, 'Space Grotesk', sans-serif"
MONO_FONT = "JetBrains Mono, monospace"


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

        :root {{
            color-scheme: dark;
            font-family: {FONT_FAMILY};
            background-color: {BG_COLOR};
            color: #e7efff;
        }}

        html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .main {{
            background: {BG_COLOR} !important;
            color: #e7efff !important;
            font-family: {FONT_FAMILY} !important;
        }}

        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            background-image:
              radial-gradient(circle at 16% 12%, rgba(77,210,255,0.14), transparent 18%),
              radial-gradient(circle at 80% 8%, rgba(148, 255, 255, 0.08), transparent 16%),
              repeating-linear-gradient(0deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 2px, transparent 4px);
            opacity: 0.14;
            pointer-events: none;
            z-index: 0;
        }}

        #MainMenu, footer, header {{ visibility: hidden; }}

        [data-testid="stSidebar"] {{
            background: rgba(6, 10, 18, 0.96) !important;
            border-right: 1px solid rgba(77,210,255,0.14) !important;
            box-shadow: inset 2px 0 32px rgba(77,210,255,0.08);
        }}

        .css-18e3th9 {{ padding-top: 1rem !important; }}

        .glass-card {{
            background: {CARD_BG};
            border: 1px solid {BORDER_BG};
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35), inset 0 0 1px rgba(255,255,255,0.03);
            backdrop-filter: blur(18px);
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        }}

        .glass-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 28px 80px rgba(0, 0, 0, 0.45), inset 0 0 4px rgba(77,210,255,0.08);
            border-color: rgba(77,210,255,0.28);
        }}

        .hero-card {{
            background: linear-gradient(180deg, rgba(11, 16, 30, .94), rgba(7, 10, 18, .88));
            border: 1px solid rgba(77,210,255,0.18);
        }}

        .hero-eyebrow {{
            letter-spacing: 0.22em;
            font-size: 0.78rem;
            text-transform: uppercase;
            color: rgba(77,210,255,0.95);
            margin-bottom: 0.9rem;
        }}

        .hero-title {{
            font-size: clamp(2.4rem, 2.2vw, 3.4rem);
            margin: 0;
            line-height: 1.05;
            color: #f8fbff;
        }}

        .hero-copy {{
            color: rgba(232, 246, 255, 0.8);
            max-width: 720px;
            line-height: 1.75;
            letter-spacing: 0.01em;
        }}

        .mini-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.85rem 1rem;
            border-radius: 999px;
            border: 1px solid rgba(77,210,255,0.18);
            background: rgba(77,210,255,0.08);
            color: #d7f7ff;
            font-size: 0.88rem;
            font-weight: 600;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }}

        .section-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 1.05rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: #bde7ff;
            margin-bottom: 0.55rem;
        }}

        .section-subtitle {{
            color: rgba(216, 237, 255, 0.72);
            font-size: 0.95rem;
            line-height: 1.7;
            margin-bottom: 1.1rem;
        }}

        .rank-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1rem;
        }}

        .rank-card {{
            padding: 1rem 1.1rem;
            border-radius: 20px;
            background: rgba(10, 14, 22, 0.88);
            border: 1px solid rgba(77,210,255,0.16);
            box-shadow: inset 0 0 1px rgba(255,255,255,0.03);
            transition: transform 0.25s ease, border-color 0.25s ease;
        }}

        .rank-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(77,210,255,0.26);
        }}

        .rank-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2.4rem;
            height: 2.4rem;
            border-radius: 14px;
            font-family: {MONO_FONT};
            font-size: 0.95rem;
            font-weight: 700;
            color: #eff6ff;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(77,210,255,0.25);
            margin-bottom: 0.85rem;
        }}

        .rank-title {{
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0.35rem 0 0.4rem;
            color: #f8fbff;
        }}

        .rank-meta {{
            color: rgba(222, 234, 255, 0.78);
            font-size: 0.88rem;
            line-height: 1.6;
            margin-bottom: 0.9rem;
        }}

        .chip-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.8rem;
        }}

        .chip-tag {{
            padding: 0.38rem 0.72rem;
            border-radius: 999px;
            font-size: 0.78rem;
            background: rgba(77,210,255,0.08);
            border: 1px solid rgba(77,210,255,0.16);
            color: #d7f7ff;
            transition: transform 0.2s ease;
        }}

        .chip-tag:hover {{
            transform: translateY(-1px);
            background: rgba(77,210,255,0.14);
        }}

        .neon-panel {{
            padding: 1rem 1.1rem;
            border-radius: 22px;
            border: 1px solid rgba(77,210,255,0.24);
            background: rgba(8, 12, 20, 0.86);
            box-shadow: inset 0 0 5px rgba(77,210,255,0.08);
        }}

        .mini-label {{
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.21em;
            color: rgba(175, 235, 255, 0.8);
        }}

        .metric-box {{
            border-radius: 18px;
            padding: 1rem 1rem 1.05rem;
            background: rgba(10, 14, 24, 0.86);
            border: 1px solid rgba(77,210,255,0.14);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
            transition: transform 0.22s ease, border-color 0.22s ease;
        }}

        .metric-box:hover {{
            transform: translateY(-2px);
            border-color: rgba(77,210,255,0.22);
        }}

        .metric-value {{
            color: #f8fbff;
            font-family: {MONO_FONT};
            font-size: 2rem;
            font-weight: 700;
            margin-top: 0.3rem;
            line-height: 1.05;
        }}

        .metric-label-small {{
            color: rgba(219, 239, 255, 0.75);
            font-size: 0.85rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }}

        .plotly-graph-div .modebar {{ display: none !important; }}

        .stTabs [role="tab"] {{
            font-family: 'Orbitron', sans-serif !important;
            text-transform: uppercase !important;
            letter-spacing: 0.18em !important;
            color: #c7e7ff !important;
            border-radius: 14px !important;
        }}
        .stTabs [role="tab"][aria-selected="true"] {{
            background: rgba(77,210,255,0.14) !important;
            box-shadow: 0 0 22px rgba(77,210,255,0.18) !important;
            border: 1px solid rgba(77,210,255,0.32) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def format_count(value: int) -> str:
    return f"{value:,}"

def get_mci_color(value: float) -> str:
    if value >= 60:
        return NEON_CYAN
    if value >= 45:
        return NEON_PURPLE
    return NEON_ORANGE

def build_mci_rank_chart(df: pd.DataFrame) -> go.Figure:
    rank_df = df.copy()
    rank_df = rank_df.sort_values("MCI", ascending=False).head(14)
    rank_df["_color"] = rank_df["MCI"].apply(get_mci_color)
    fig = go.Figure(go.Bar(
        x=rank_df["MCI"],
        y=rank_df["districtname"],
        orientation="h",
        marker=dict(color=rank_df["_color"], line=dict(color="rgba(255,255,255,0.12)", width=1.5)),
        text=rank_df["MCI"].round(1),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>MCI: %{x:.1f}<extra></extra>",
    ))
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=24, t=24, b=24),
        plot_bgcolor=TRANSPARENT,
        paper_bgcolor=TRANSPARENT,
        xaxis=dict(range=[0, 110], title="MCI score", color=AXIS_COLOR, gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, showgrid=True),
        yaxis=dict(autorange="reversed", title="", color=AXIS_COLOR, ticks="outside", gridcolor=TRANSPARENT),
        font=dict(family=MONO_FONT, color="#edf4ff"),
        showlegend=False,
    )
    fig.update_yaxes(tickfont=dict(size=12))
    return fig

def build_wsi_wei_chart(df: pd.DataFrame) -> go.Figure:
    quadrant_df = df.copy()
    if "WSI" not in quadrant_df.columns or "WEI" not in quadrant_df.columns:
        quadrant_df["WSI"] = quadrant_df["MCI"].fillna(0)
        quadrant_df["WEI"] = quadrant_df["MCI"].fillna(0)

    def quadrant_label(row: pd.Series) -> str:
        if row["WSI"] >= 60 and row["WEI"] >= 60:
            return "Women Growth Leaders"
        if row["WSI"] >= 60 and row["WEI"] < 60:
            return "Infrastructure Ready"
        if row["WSI"] < 60 and row["WEI"] >= 60:
            return "Socially Strong"
        return "Critical Attention"

    quadrant_df["status"] = quadrant_df.apply(quadrant_label, axis=1)
    color_map = {
        "Women Growth Leaders": NEON_GREEN,
        "Infrastructure Ready": NEON_YELLOW,
        "Socially Strong": NEON_CYAN,
        "Critical Attention": NEON_RED,
    }
    fig = px.scatter(
        quadrant_df,
        x="WSI",
        y="WEI",
        color="status",
        color_discrete_map=color_map,
        hover_name="districtname",
        hover_data={"statename": True, "MCI": ":.1f", "WSI": ":.1f", "WEI": ":.1f"},
        size="MCI",
        size_max=22,
    )
    fig.update_traces(marker=dict(line=dict(width=1.5, color="#07111f"), opacity=0.9), selector=dict(mode="markers"))
    fig.update_layout(
        height=440,
        margin=dict(l=24, r=24, t=24, b=24),
        plot_bgcolor=TRANSPARENT,
        paper_bgcolor=TRANSPARENT,
        xaxis=dict(range=[0, 105], title="Women Safety Index (WSI)", titlefont=dict(color="#f472b6"), color=AXIS_COLOR, gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, showgrid=True),
        yaxis=dict(range=[0, 105], title="Women Employment Index (WEI)", titlefont=dict(color="#60a5fa"), color=AXIS_COLOR, gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, showgrid=True),
        font=dict(family=MONO_FONT, color="#edf4ff"),
        legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_layout(shapes=[
        dict(type="rect", x0=50, x1=100, y0=50, y1=100, fillcolor="rgba(34,197,94,0.08)", line_width=0),
        dict(type="rect", x0=50, x1=100, y0=0, y1=50, fillcolor="rgba(250,204,21,0.08)", line_width=0),
        dict(type="rect", x0=0, x1=50, y0=50, y1=100, fillcolor="rgba(77,210,255,0.08)", line_width=0),
        dict(type="rect", x0=0, x1=50, y0=0, y1=50, fillcolor="rgba(244,63,94,0.08)", line_width=0),
        dict(type="line", x0=50, x1=50, y0=0, y1=100, line=dict(color="rgba(255,255,255,0.18)", dash="dash")),
        dict(type="line", x0=0, x1=100, y0=50, y1=50, line=dict(color="rgba(255,255,255,0.18)", dash="dash")),
    ])
    fig.add_annotation(x=75, y=82, text="Women Growth Leaders", showarrow=False, font=dict(size=10, color="#d8ffea"), align="center")
    fig.add_annotation(x=75, y=32, text="Infrastructure Ready", showarrow=False, font=dict(size=10, color="#fff3b0"), align="center")
    fig.add_annotation(x=25, y=82, text="Socially Strong", showarrow=False, font=dict(size=10, color="#bef4ff"), align="center")
    fig.add_annotation(x=25, y=25, text="Critical Attention", showarrow=False, font=dict(size=10, color="#ffb3c6"), align="center")
    return fig

def build_insight_cards(df: pd.DataFrame) -> str:
    severe = df[df.get("MCI_class") == "Severe desert"]
    moderate = df[df.get("MCI_class") == "Moderate desert"]
    stable = df[(df.get("MCI_class") == "Connected") | (df.get("MCI_class") == "Near-connected")]
    severe_names = severe["districtname"].head(6).tolist()
    moderate_names = moderate["districtname"].head(6).tolist()
    stable_names = stable["districtname"].head(6).tolist()

    def make_chip_list(names):
        return "".join([f"<span class='chip-tag'>{name}</span>" for name in names])

    return f"""
    <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-top:1rem;'>
      <div class='glass-card neon-panel'>
        <div class='mini-label'>Critical Attention</div>
        <div class='rank-title' style='color:{NEON_RED};'>Severe digital deserts</div>
        <div class='rank-meta'>{format_count(len(severe))} districts · urgent coverage gap</div>
        <div class='chip-row'>{make_chip_list(severe_names)}</div>
      </div>
      <div class='glass-card neon-panel'>
        <div class='mini-label'>Enterprise response</div>
        <div class='rank-title' style='color:{NEON_ORANGE};'>Moderate digital deserts</div>
        <div class='rank-meta'>{format_count(len(moderate))} districts · policy escalation required</div>
        <div class='chip-row'>{make_chip_list(moderate_names)}</div>
      </div>
      <div class='glass-card neon-panel'>
        <div class='mini-label'>AI signal</div>
        <div class='rank-title' style='color:{NEON_CYAN};'>Connected leadership</div>
        <div class='rank-meta'>{format_count(len(stable))} districts · stable signal</div>
        <div class='chip-row'>{make_chip_list(stable_names)}</div>
      </div>
    </div>
    """

def render_hero_section() -> None:
    st.markdown(
        """
        <div class='glass-card hero-card'>
          <div style='display:flex;flex-wrap:wrap;justify-content:space-between;gap:1.5rem;'>
            <div style='max-width:760px;'>
              <div class='hero-eyebrow'>SIGNAL | DIGITAL DESERT COMMAND CENTER</div>
              <h1 class='hero-title'>Digital Desert Command Center</h1>
              <p class='hero-copy'>Premium AI analytics for Minimum Connectivity Index monitoring, quadrant policy intelligence, and enterprise-level district performance.</p>
            </div>
            <div style='display:flex;flex-wrap:wrap;gap:0.85rem;align-items:flex-start;'>
              <div class='mini-pill'>State × District</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_kpi_row(n_total: int, n_deserts: int, n_severe: int, avg_mci: float, avg_wsi: float, avg_wei: float, high_risk: int) -> None:
    cols = st.columns(6, gap='small')
    metrics = [
        ("Districts", format_count(n_total), "Total district units under review"),
        ("Digital deserts", format_count(n_deserts), f"{format_count(n_severe)} severe"),
        ("Avg MCI", f"{avg_mci:.1f}", "Average index strength"),
        ("Avg WSI", f"{avg_wsi:.1f}", "Women Safety index"),
        ("Avg WEI", f"{avg_wei:.1f}", "Women Employment index"),
        ("High risk", format_count(high_risk), "Critical districts"),
    ]
    for col, (label, value, subtitle) in zip(cols, metrics):
        col.markdown(
            f"""
            <div class='metric-box'>
              <div class='metric-label-small'>{label}</div>
              <div class='metric-value'>{value}</div>
              <div class='rank-meta'>{subtitle}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_district_rank_cards(filtered_df: pd.DataFrame) -> None:
    top = filtered_df.sort_values("MCI", ascending=False).head(5)
    if top.empty:
        return
    card_html = ""
    for rank, row in enumerate(top.itertuples(index=False), start=1):
        chip_items = []
        if hasattr(row, 'MCI_class') and row.MCI_class:
            chip_items.append(row.MCI_class)
        if hasattr(row, 'WSI'):
            chip_items.append(f"WSI {row.WSI:.0f}")
        if hasattr(row, 'WEI'):
            chip_items.append(f"WEI {row.WEI:.0f}")
        chip_html = "".join([f"<span class='chip-tag'>{item}</span>" for item in chip_items])
        card_html += (
            f"<div class='rank-card'><div class='rank-badge'>#{rank}</div>"
            f"<div class='rank-title' style='color:{get_mci_color(row.MCI)};'>{row.districtname}</div>"
            f"<div class='rank-meta'>State: {row.statename} · MCI {row.MCI:.1f}</div>"
            f"<div class='chip-row'>{chip_html}</div>"
            f"</div>"
        )
    st.markdown(f"<div class='rank-grid'>{card_html}</div>", unsafe_allow_html=True)

def render_quadrant_selector(filtered_df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    districts = filtered_df["districtname"].dropna().unique().tolist()
    search = st.text_input("Search district", placeholder="Type district name to filter chart...")
    if search:
        filtered_df = filtered_df[filtered_df["districtname"].str.contains(search, case=False, na=False)]
    selected = st.selectbox("Drill into district", ["— select —"] + districts)
    return selected, filtered_df

def render_insights_panel(filtered_df: pd.DataFrame) -> None:
    st.markdown(build_insight_cards(filtered_df), unsafe_allow_html=True)

def render_footer() -> None:
    st.markdown(
        """
        <div style='padding:1rem 0 1.2rem;color:rgba(208,220,255,0.65);font-size:0.9rem;line-height:1.7;'>
            Premium analytics platform · AI command center experience · interactive policy intelligence with neon visual signals.
        </div>
        """,
        unsafe_allow_html=True,
    )

def main() -> None:
    st.set_page_config(
        page_title="MCI AI Command Center",
        page_icon="??️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()

    tab_dashboard, tab_simulation = st.tabs(["?? Dashboard", "?? Policy Simulation"])

    with tab_dashboard:
        with st.spinner("Activating command center..."):
            data = load_all_data()

        scores_df = data["scores"]
        timeseries_df = data["timeseries"]
        sub_df = data["subcomponents"]
        imp_df = data["importance"]
        cluster_df = data["clusters"]

        filters = render_sidebar(scores_df)
        filtered_df = apply_filters(scores_df, filters)

        selected_district, filtered_df = render_quadrant_selector(filtered_df)
        n_total = len(filtered_df)

        render_hero_section()
        render_kpi_row(
            n_total,
            len(filtered_df[filtered_df.get("MCI_class")] if "MCI_class" in filtered_df.columns else []),
            len(filtered_df[filtered_df.get("MCI_class")] == "Severe desert" if "MCI_class" in filtered_df.columns else []),
            filtered_df["MCI"].mean() if n_total else 0.0,
            filtered_df["WSI"].mean() if n_total and "WSI" in filtered_df.columns else 0.0,
            filtered_df["WEI"].mean() if n_total and "WEI" in filtered_df.columns else 0.0,
            len(filtered_df[filtered_df.get("Safety_risk")] == "High safety risk" if "Safety_risk" in filtered_df.columns else []),
        )

        st.markdown("<div class='section-title'>Core analytics</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Interactive neon widgets highlighting top MCI districts, quadrant policy signals, and rapid drill-down workflows.</div>", unsafe_allow_html=True)

        left_col, right_col = st.columns([1.05, 1], gap='large')
        with left_col:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>MCI by district</div>", unsafe_allow_html=True)
            if n_total:
                st.plotly_chart(build_mci_rank_chart(filtered_df), use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No districts match the current filters.")
            st.markdown("</div>", unsafe_allow_html=True)
        with right_col:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>WSI vs WEI — women impact quadrant</div>", unsafe_allow_html=True)
            if n_total and "WSI" in filtered_df.columns and "WEI" in filtered_df.columns:
                st.plotly_chart(build_wsi_wei_chart(filtered_df), use_container_width=True, config={"displayModeBar": False})
            else:
                st.warning("WSI / WEI data is unavailable for this dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        render_district_rank_cards(filtered_df)
        render_insights_panel(filtered_df)

        if selected_district != "— select —" and n_total:
            selected_row = filtered_df[filtered_df["districtname"] == selected_district]
            if not selected_row.empty:
                st.markdown("<div class='section-title'>District drill-down</div>", unsafe_allow_html=True)
                render_area_detail(
                    area_row=selected_row.iloc[0].to_dict(),
                    sub_df=sub_df,
                    timeseries_df=timeseries_df,
                )

        render_footer()

    with tab_simulation:
        render_simulation_page()


if __name__ == "__main__":
    main()
