"""
dashboard/charts.py
====================
All Plotly chart builder functions.

Schema alignment:
  districtname  — the geographic unit (replaces old 'area' and 'city')
  statename     — human-readable state name
  canonical_state — normalised state key (used for joins, not display)
  No area_type, city_tier, city, or area columns exist.
"""

from __future__ import annotations
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from config import CLASS_ORDER, CLASS_COLORS, FACTOR_COLORS, FACTOR_LABELS

TRANSPARENT = "rgba(0,0,0,0)"
CHART_FONT = "JetBrains Mono, monospace"
DARK_AXIS_COLOR = "#9fbacb"
DARK_GRID_COLOR = "rgba(159, 186, 203, 0.08)"
NEON_CYAN = "#4dd2ff"
NEON_LIME = "#9efd13"
NEON_AMBER = "#ffb33d"
NEON_RED = "#ff4b5c"
NEON_MAGENTA = "#ff4cff"


def classification_bar(df: pd.DataFrame) -> go.Figure:
    counts = (
        df["MCI_class"].value_counts()
        .reindex(CLASS_ORDER, fill_value=0)
        .reset_index()
    )
    counts.columns = ["Classification", "Count"]
    fig = px.bar(
        counts, x="Count", y="Classification", orientation="h",
        color="Classification", color_discrete_map=CLASS_COLORS, text="Count",
    )
    fig.update_traces(textposition="outside", marker_line_width=1.5, marker_line_color="rgba(255,255,255,0.06)")
    fig.update_layout(
        showlegend=False, height=260,
        margin=dict(l=0, r=20, t=10, b=10),
        xaxis_title="", yaxis_title="",
        font=dict(family=CHART_FONT, color="#edf4ff"),
        plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT,
        xaxis=dict(color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
        yaxis=dict(categoryorder="array",
                   categoryarray=list(reversed(CLASS_ORDER)),
                   color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
    )
    return fig


def factor_avg_bar(df: pd.DataFrame) -> go.Figure:
    avgs = {
        FACTOR_LABELS[k]: round(df[k].mean(), 1)
        for k in FACTOR_LABELS if k in df.columns
    }
    fig = go.Figure(go.Bar(
        x=list(avgs.values()), y=list(avgs.keys()),
        orientation="h",
        marker_color=[NEON_CYAN, NEON_LIME, NEON_AMBER, NEON_MAGENTA][: len(avgs)],
        marker_line_width=1.2,
        marker_line_color="rgba(255,255,255,0.12)",
        text=[f"{v:.1f}" for v in avgs.values()],
        textposition="outside",
        textfont=dict(color="#f1fbff", family=CHART_FONT),
    ))
    fig.add_vline(x=45, line_dash="dash", line_color=NEON_RED,
                  annotation_text="desert threshold", annotation_position="top right",
                  annotation_font=dict(color="#ffccd2", family=CHART_FONT))
    fig.update_layout(
        height=260, showlegend=False,
        xaxis=dict(range=[0, 110], title="", color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
        yaxis_title="",
        margin=dict(l=0, r=20, t=10, b=10),
        font=dict(family=CHART_FONT, color="#edf4ff"),
        plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT,
        yaxis=dict(color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
    )
    return fig


def mci_scatter(df: pd.DataFrame) -> go.Figure:
    """MCI scatter plot — x-axis is districtname, coloured by classification."""
    plot_df = df.copy().sort_values("MCI")
    plot_df["label"] = plot_df["districtname"] + " (" + plot_df["statename"] + ")"

    hover = {k: True for k in ["IFS", "DLS", "SES", "WDI", "MCI_class"]
             if k in plot_df.columns}

    fig = px.scatter(
        plot_df, x="label", y="MCI",
        color="MCI_class", color_discrete_map=CLASS_COLORS,
        hover_name="label",
        hover_data=hover,
        size="MCI", size_max=18,
    )
    fig.update_traces(marker=dict(line=dict(width=1.2, color="#0b1320"), opacity=0.92, sizemode="area"))
    fig.add_hline(y=45, line_dash="dash", line_color=NEON_RED,
                  annotation_text="desert threshold (45)", annotation_font=dict(color="#ffb3c1", family=CHART_FONT))
    fig.add_hline(y=25, line_dash="dot", line_color="#ff7b8a",
                  annotation_text="severe (25)", annotation_font=dict(color="#ffb3c1", family=CHART_FONT))
    fig.update_layout(
        height=340, showlegend=False,
        xaxis=dict(showticklabels=False, title="", color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
        yaxis=dict(range=[0, 105], title="MCI score", color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
        margin=dict(l=30, r=20, t=20, b=30),
        font=dict(family=CHART_FONT, color="#edf4ff"),
        plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT,
    )
    return fig


def wsi_wei_quadrant(df: pd.DataFrame) -> go.Figure:
    """WSI vs WEI scatter — hover shows districtname and statename."""
    hover_data = {
        k: True for k in ["statename", "MCI"]
        if k in df.columns
    }
    fig = px.scatter(
        df, x="WSI", y="WEI",
        color="MCI_class", color_discrete_map=CLASS_COLORS,
        hover_name="districtname",
        hover_data=hover_data,
        size="MCI", size_max=16,
    )
    fig.update_traces(marker=dict(line=dict(width=1.4, color="#08101d"), opacity=0.88, sizemode="area"))
    fig.add_vline(x=35, line_dash="dash", line_color=NEON_RED,
                  annotation_text="safety risk threshold", annotation_font=dict(color="#ffccd2", family=CHART_FONT))
    fig.add_hline(y=40, line_dash="dash", line_color=NEON_AMBER,
                  annotation_text="employment gap threshold", annotation_font=dict(color="#ffe1a8", family=CHART_FONT))
    for txt, x, y in [
        ("High risk / Low opportunity",  18, 18),
        ("Low risk / High opportunity",  78, 78),
        ("High risk / Moderate opp.",    18, 72),
        ("Low risk / Low opportunity",   72, 18),
    ]:
        fig.add_annotation(x=x, y=y, text=txt, showarrow=False,
                           font=dict(size=9, color="rgba(146, 166, 195, 0.72)"), align="center")
    fig.update_layout(
        height=340,
        xaxis=dict(range=[0, 105], title="Women Safety Index (WSI)", color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR, ticks="outside"),
        yaxis=dict(range=[0, 105], title="Women Employment Index (WEI)", color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR, ticks="outside"),
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family=CHART_FONT, color="#edf4ff"),
        plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT,
    )
    return fig


def mci_trend_line(trend_df: pd.DataFrame, district_label: str) -> go.Figure:
    """Line chart of MCI and factor scores over years for a single district."""
    fig = go.Figure()
    cols = [c for c in ["MCI", "IFS", "DLS", "SES", "WDI"] if c in trend_df.columns]
    colors_map = {"MCI": NEON_CYAN, **FACTOR_COLORS}
    widths_map  = {"MCI": 3, "IFS": 1.5, "DLS": 1.5, "SES": 1.5, "WDI": 1.5}
    for col in cols:
        fig.add_trace(go.Scatter(
            x=trend_df["year"], y=trend_df[col].round(1),
            mode="lines+markers", name=col,
            line=dict(color=colors_map.get(col, "#9fbacb"), width=widths_map.get(col, 1.5)),
            marker=dict(size=6, line=dict(width=1, color="#08101d")),
        ))
    fig.add_hline(y=45, line_dash="dash", line_color=NEON_RED,
                  annotation_text="desert threshold", annotation_font=dict(color="#ffc6cd", family=CHART_FONT))
    fig.update_layout(
        title=f"MCI trend — {district_label}",
        height=300,
        xaxis=dict(title="Year", tickmode="linear", color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
        yaxis=dict(range=[0, 105], title="Score", color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
        margin=dict(l=0, r=10, t=40, b=10),
        font=dict(family=CHART_FONT, color="#edf4ff"),
        plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT,
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


def area_radar(area_row: dict, sub_df: pd.DataFrame) -> go.Figure:
    """
    Radar of sub-component scores for the selected district.
    Looks up sub_df on canonical_state + districtname.
    Falls back to factor scores if subcomponent data unavailable.
    """
    district = area_row.get("districtname", "")
    state    = area_row.get("canonical_state", "")

    # Filter subcomponents for this district
    mask = pd.Series([True] * len(sub_df), index=sub_df.index)
    if district and "districtname" in sub_df.columns:
        mask &= sub_df["districtname"] == district
    if state and "canonical_state" in sub_df.columns:
        mask &= sub_df["canonical_state"] == state

    area_sub = sub_df[mask]

    if not area_sub.empty:
        labels = area_sub["subcomponent"].tolist()
        values = area_sub["sub_score"].tolist()
    else:
        # Fallback: factor scores + WSI + WEI
        labels = list(FACTOR_LABELS.values()) + ["WSI", "WEI"]
        values = [
            area_row.get(k, 50)
            for k in list(FACTOR_LABELS.keys()) + ["WSI", "WEI"]
        ]

    # Close the polygon
    labels = labels + [labels[0]]
    values = values + [values[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values, theta=labels,
        fill="toself",
        fillcolor="rgba(77,210,255,0.14)",
        line=dict(color=NEON_CYAN, width=2),
        marker=dict(color=NEON_CYAN, size=6, opacity=0.85),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9, color=DARK_AXIS_COLOR), gridcolor=DARK_GRID_COLOR),
            angularaxis=dict(tickfont=dict(size=9, color=DARK_AXIS_COLOR)),
            bgcolor=TRANSPARENT,
        ),
        showlegend=False, height=300,
        margin=dict(l=40, r=40, t=20, b=20),
        font=dict(family=CHART_FONT, color="#edf4ff"),
        paper_bgcolor=TRANSPARENT,
    )
    return fig


def cluster_centroid_chart(cluster_df: pd.DataFrame) -> go.Figure:
    """Faceted bar chart of factor centroids per cluster."""
    rows = []
    for _, row in cluster_df.iterrows():
        for factor in ["IFS", "DLS", "SES", "WDI"]:
            col_name = f"{factor}_centroid"
            if col_name not in row:
                continue
            rows.append({
                "Cluster": f"C{int(row['cluster_id'])}: {row['label']}",
                "Factor":  FACTOR_LABELS[factor],
                "Score":   row[col_name],
            })
    if not rows:
        return go.Figure()

    cent_df = pd.DataFrame(rows)
    fig = px.bar(
        cent_df, x="Factor", y="Score",
        color="Factor",
        color_discrete_map={
            v: list(FACTOR_COLORS.values())[i]
            for i, v in enumerate(FACTOR_LABELS.values())
        },
        facet_col="Cluster",
        facet_col_wrap=min(4, len(cluster_df)),
        height=300,
    )
    fig.add_hline(y=45, line_dash="dash", line_color=NEON_RED, line_width=0.8)
    fig.update_traces(marker_line_width=1.2, marker_line_color="rgba(255,255,255,0.08)")
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=40, b=0),
        font=dict(family=CHART_FONT, color="#edf4ff"),
        plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT,
        yaxis=dict(range=[0, 105], color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
        xaxis=dict(color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
    )
    fig.for_each_annotation(lambda a: a.update(
        text=a.text.split("=")[-1], font=dict(size=10, color="#b6c7dd", family=CHART_FONT)
    ))
    return fig


def rf_importance_bar(imp_df: pd.DataFrame) -> go.Figure:
    top = imp_df.head(12).copy()
    top["label"] = top["pct"].apply(lambda x: f"{x:.1f}%")
    fig = px.bar(
        top, x="importance", y="feature", orientation="h",
        text="label",
        color="importance",
        color_continuous_scale=[NEON_CYAN, NEON_LIME],
    )
    fig.update_traces(textposition="outside", marker_line_width=1.2, marker_line_color="rgba(255,255,255,0.08)")
    fig.update_layout(
        height=max(300, len(top) * 36),
        showlegend=False, coloraxis_showscale=False,
        xaxis_title="Feature importance", yaxis_title="",
        yaxis=dict(autorange="reversed", color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
        xaxis=dict(color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
        margin=dict(l=0, r=60, t=10, b=10),
        font=dict(family=CHART_FONT, color="#edf4ff"),
        plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT,
    )
    return fig


def spearman_heatmap(df: pd.DataFrame) -> go.Figure:
    cols = [c for c in ["IFS", "DLS", "SES", "WDI", "MCI", "WSI", "WEI"]
            if c in df.columns]
    corr = df[cols].corr(method="spearman").round(3)
    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale=[
            [0, "#081018"],
            [0.25, "#1a57b8"],
            [0.5, "#4dd2ff"],
            [0.75, "#ffb33d"],
            [1, "#ff4b5c"],
        ],
        zmin=-1, zmax=1,
        text=corr.values.round(2), texttemplate="%{text}",
        textfont=dict(size=11, color="#edf4ff"), showscale=True,
        colorbar=dict(thickness=12, outlinecolor="rgba(255,255,255,0.12)", ticks="outside"),
    ))
    fig.update_layout(
        height=340,
        margin=dict(l=0, r=0, t=10, b=10),
        font=dict(family=CHART_FONT, color="#edf4ff"),
        plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT,
        xaxis=dict(color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
        yaxis=dict(color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
    )
    return fig


def dynamic_chart(df: pd.DataFrame, chart_type: str):
    """Render agent-suggested chart. Returns None for 'table' type."""
    if df is None or df.empty:
        return None

    if chart_type == "bar":
        num_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(exclude="number").columns.tolist()
        if num_cols and cat_cols:
            fig = px.bar(df, x=cat_cols[0], y=num_cols[0], text=num_cols[0], color=num_cols[0], color_continuous_scale=[NEON_CYAN, NEON_LIME])
            fig.update_traces(textposition="outside", marker_line_width=1.2, marker_line_color="rgba(255,255,255,0.1)")
            fig.update_layout(
                height=300, xaxis=dict(tickangle=45, color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
                font=dict(family=CHART_FONT, color="#edf4ff"),
                plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT,
                margin=dict(l=0, r=0, t=10, b=80),
            )
            return fig

    elif chart_type == "line" and "year" in df.columns:
        num_cols = [c for c in df.select_dtypes(include="number").columns
                    if c != "year"]
        if num_cols:
            fig = px.line(df, x="year", y=num_cols, markers=True)
            fig.update_traces(line=dict(width=2), marker=dict(size=6, line=dict(width=1, color="#0b1320")))
            fig.update_layout(
                height=300,
                font=dict(family=CHART_FONT, color="#edf4ff"),
                plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT,
                margin=dict(l=0, r=0, t=10, b=10),
                xaxis=dict(color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
                yaxis=dict(color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
            )
            return fig

    elif chart_type == "scatter":
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if len(num_cols) >= 2:
            fig = px.scatter(df, x=num_cols[0], y=num_cols[1],
                             hover_name=df.columns[0])
            fig.update_traces(marker=dict(size=10, line=dict(width=1, color="#08101d"), opacity=0.9))
            fig.update_layout(
                height=300,
                font=dict(family=CHART_FONT, color="#edf4ff"),
                plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT,
                xaxis=dict(color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
                yaxis=dict(color=DARK_AXIS_COLOR, gridcolor=DARK_GRID_COLOR, zerolinecolor=DARK_GRID_COLOR),
            )
            return fig

    return None