"""
dashboard/filters.py
=====================
Sidebar filter rendering and data loading.

Schema alignment (mci_scores actual columns):
  canonical_state  — normalised state key used for all joins
  statename        — human-readable state name for display
  districtname     — the geographic unit (replaces old 'city' and 'area')
  districtcode     — numeric district identifier
  statecode        — numeric state identifier
  year

Old columns REMOVED (do not reference):
  city, area, city_tier, area_type, population_m, area_km2,
  Profile_label (not in mci_scores — comes from cluster join)
"""

from __future__ import annotations
import duckdb
import pandas as pd
import streamlit as st

from config import DB_PATH, CLASS_ORDER


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_all_data(db_path: str = DB_PATH) -> dict:
    con = duckdb.connect(db_path, read_only=True)

    # ── mci_scores: select only columns that actually exist ───────────────────
    scores = con.execute("""
        SELECT
            canonical_state,
            statename,
            statecode,
            districtname,
            districtcode,
            year,
            ROUND(IFS, 1)  AS IFS,
            ROUND(DLS, 1)  AS DLS,
            ROUND(SES, 1)  AS SES,
            ROUND(WDI, 1)  AS WDI,
            ROUND(MCI, 1)  AS MCI,
            ROUND(WSI, 1)  AS WSI,
            ROUND(WEI, 1)  AS WEI,
            MCI_class,
            Safety_risk,
            Employment_gap,
            cluster_id,
            cluster_label,
            -- raw sub-variables used by policy_engine/rules.py
            mobile_only_pct,
            no_phone_pct,
            any_phone_pct,
            illiteracy_percent,
            gender_vulnerability_index,
            crime_against_women_rate,
            msme_female_share_pct,
            share_of_slum_population,
            dependent_women_percent,
            wireless_rural_teledensity_pct,
            e_transactions_per_1000_population,
            maternal_mortality_rate,
            destitute_pct,
            non_agri_enterprise_pct,
            income_lt5k_pct
        FROM mci_scores
        ORDER BY MCI ASC
    """).df()

    # ── timeseries: join on canonical_state + districtname ────────────────────
    timeseries = con.execute("""
        SELECT
            canonical_state,
            statename,
            districtname,
            year,
            ROUND(MCI, 1) AS MCI,
            ROUND(IFS, 1) AS IFS,
            ROUND(DLS, 1) AS DLS,
            ROUND(SES, 1) AS SES,
            ROUND(WDI, 1) AS WDI,
            ROUND(WSI, 1) AS WSI,
            ROUND(WEI, 1) AS WEI
        FROM mci_timeseries_scores
        ORDER BY canonical_state, districtname, year ASC
    """).df()

    # ── subcomponents: join on canonical_state + districtname ─────────────────
    subcomponents = con.execute("""
        SELECT
            canonical_state,
            districtname,
            year,
            factor,
            subcomponent,
            sub_score,
            weight_in_factor
        FROM factor_subcomponent_scores
    """).df()

    # ── rf importance ─────────────────────────────────────────────────────────
    importance = con.execute("""
        SELECT feature, importance, rank, pct
        FROM rf_feature_importance
        ORDER BY rank ASC
    """).df()

    # ── cluster profiles ──────────────────────────────────────────────────────
    clusters = con.execute("""
        SELECT
            cluster_id, label, weakest_factor, mean_score, severity,
            IFS_centroid, DLS_centroid, SES_centroid, WDI_centroid,
            area_count, area_list, intervention
        FROM cluster_profiles
        ORDER BY mean_score ASC
    """).df()

    con.close()
    return {
        "scores":        scores,
        "timeseries":    timeseries,
        "subcomponents": subcomponents,
        "importance":    importance,
        "clusters":      clusters,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR FILTERS
# Filters map to new schema columns:
#   state   → statename (display) / canonical_state (joins)
#   district → districtname
#   No city_tier — replaced by state-level grouping
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar(scores_df: pd.DataFrame) -> dict:
    with st.sidebar:
        st.markdown(
            """
            <div class='sidebar-panel'>
                <div class='sidebar-title'>Operational Control</div>
                <div class='sidebar-subtitle'>Digital Desert command center</div>
                <div class='sidebar-subtitle' style='margin-top:0.7rem;'>Filter by year, state, district, or MCI band, then inspect charts, policy recommendations, and AI insights.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.get("reset_filters", False):
            defaults = {
                "year_filter": "All",
                "state_filter": "All",
                "district_filter": "All",
                "cls_filter": "All",
                "mci_range": (0, 100),
                "desert_only": False,
            }
            for key, value in defaults.items():
                st.session_state[key] = value
            st.session_state["reset_filters"] = False

        st.markdown("---")

        # Year filter
        year_options = ["All"] + sorted(
            scores_df["year"].dropna().astype(int).unique().tolist()
        )
        selected_year = st.selectbox("Year", year_options, key="year_filter")

        # State filter (uses statename for display, canonical_state for filtering)
        state_options = ["All"] + sorted(
            scores_df["statename"].dropna().unique().tolist()
        )
        selected_state = st.selectbox("State", state_options, key="state_filter")

        # District filter (replaces old city filter)
        district_pool = scores_df.copy()
        if selected_state != "All":
            district_pool = district_pool[
                district_pool["statename"] == selected_state
            ]
        district_options = ["All"] + sorted(
            district_pool["districtname"].dropna().unique().tolist()
        )
        selected_district = st.selectbox(
            "District", district_options, key="district_filter"
        )

        # MCI classification
        cls_options = ["All"] + CLASS_ORDER
        selected_cls = st.selectbox(
            "MCI classification", cls_options, key="cls_filter"
        )

        # MCI score range
        mci_range = st.slider(
            "MCI score range", min_value=0, max_value=100,
            value=(0, 100), step=1, key="mci_range",
        )

        # Desert-only toggle
        desert_only = st.checkbox("Show digital deserts only", key="desert_only")

        if st.button("♻️ Reset filters", use_container_width=True, key="reset_filters_btn"):
            st.session_state["reset_filters"] = True

        st.markdown("---")
        st.markdown(
            """
            <div class='sidebar-panel'>
                <div class='sidebar-title'>Data Definitions</div>
                <div class='sidebar-subtitle'><strong>MCI</strong> — Minimum Connectivity Index (0–100)</div>
                <div class='sidebar-subtitle' style='margin-top:0.5rem;'>
                <span style='color:#cbd5e1;'>• < 25: Severe desert</span><br>
                <span style='color:#cbd5e1;'>• 25–45: Moderate desert</span><br>
                <span style='color:#cbd5e1;'>• 46–60: Partial connectivity</span><br>
                <span style='color:#cbd5e1;'>• 61–75: Near-connected</span><br>
                <span style='color:#cbd5e1;'>• > 75: Connected</span>
                </div>
                <div class='sidebar-subtitle' style='margin-top:0.75rem;'>
                    <strong>WSI</strong> — Women Safety Index<br>
                    <strong>WEI</strong> — Women Employment Index
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        if st.button("🔄 Reload data"):
            st.cache_data.clear()
            st.rerun()

    return {
        "year":        selected_year,
        "state":       selected_state,
        "district":    selected_district,
        "cls":         selected_cls,
        "mci_range":   mci_range,
        "desert_only": desert_only,
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    f = df.copy()
    if filters["year"] != "All":
        f = f[f["year"] == int(filters["year"])]
    if filters["state"] != "All":
        f = f[f["statename"] == filters["state"]]
    if filters["district"] != "All":
        f = f[f["districtname"] == filters["district"]]
    if filters["cls"] != "All":
        f = f[f["MCI_class"] == filters["cls"]]
    f = f[
        (f["MCI"] >= filters["mci_range"][0]) &
        (f["MCI"] <= filters["mci_range"][1])
    ]
    if filters["desert_only"]:
        f = f[f["MCI_class"].isin(["Severe desert", "Moderate desert"])]
    return f