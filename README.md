# MCI Digital Desert Dashboard
### BridgingBytes — AI-Powered Meaningful Connectivity Intelligence & Policy Simulation Platform

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Setup](#setup)
3. [Database Tables](#database-tables)
4. [Run Order](#run-order)
5. [Chatbot Agents](#chatbot-agents)
6. [Simulation System](#simulation-system)
   - [Architecture](#architecture)
   - [Intervention Cost Model](#intervention-cost-model)
   - [Deployment Speed Logic](#deployment-speed-logic)
   - [Feasibility Logic](#feasibility-logic)
   - [Optimization Strategies & Scoring](#optimization-strategies--scoring)
   - [Budget Allocation Algorithm](#budget-allocation-algorithm)
   - [Factor Score Weights in MCI](#factor-score-weights-in-mci)
   - [Social Outcome Metric Derivation](#social-outcome-metric-derivation)
   - [Confidence Estimation](#confidence-estimation)
   - [Root Cause Attribution](#root-cause-attribution)
   - [Tradeoff Table Logic](#tradeoff-table-logic)
   - [Cost Efficiency Labelling](#cost-efficiency-labelling)
   - [Policy Recommendation Ranking](#policy-recommendation-ranking)
   - [Why-Selected Rationale Rules](#why-selected-rationale-rules)
7. [Config](#config)
8. [Deployment](#deployment)
9. [Extending the Policy Engine](#extending-the-policy-engine)

---

## Project Structure

```
mci_project/
├── config.py                           # DB path, weights, model names, schema
├── requirements.txt
│
├── pipeline/
│   ├── preprocessor.py                 # Step 0 — raw data ingestion & cleaning
│   ├── mci_pipeline.py                 # Step 1 — compute all scores (timeseries-aware)
│   └── store_dashboard_tables.py       # Step 2 — build dashboard tables
│
├── simulation/
│   ├── engine.py                       # Intervention definitions, factor recomputation
│   ├── cost_model.py                   # Cost, deployment speed, feasibility per intervention
│   ├── optimizer.py                    # Deterministic budget-constrained greedy optimizer
│   ├── tradeoff.py                     # Tradeoff table data (5 dimensions per intervention)
│   ├── root_cause.py                   # Gap-weighted attribution of MCI underperformance
│   ├── recommendations.py              # Ranked policy recommendation engine
│   └── copilot.py                      # AI copilot (LLaMA 3.1 via Ollama, structured fallback)
│
├── policy_engine/
│   └── rules.py                        # Rule-based policy suggestion engine
│
├── agents/
│   ├── data_query_agent.py             # Agent 1 — SQL generation + data retrieval
│   ├── policy_agent.py                 # Agent 2 — impact analysis + recommendations
│   └── orchestrator.py                 # Routes user messages to correct agent
│
└── dashboard/
    ├── app.py                          # Main Streamlit entry point + tab navigation
    ├── filters.py                      # Sidebar filters + data loading
    ├── charts.py                       # All Plotly chart builders
    ├── area_detail.py                  # Drill-down panel + policy suggestions
    ├── simulation_page.py              # Simulation UI (dual-mode, budget bar, lever cards)
    └── chatbot.py                      # Chatbot UI component
```

> **Key principle:** All computation lives in `simulation/` and `pipeline/`. The dashboard only renders — no scoring, optimization, or attribution logic lives in any `dashboard/` file.

---

## Setup

### 1. Install Python dependencies
```bash
pip install -r requirements.txt --break-system-packages
```

### 2. Configure AI provider

This app supports two AI backends:

- `GROQ_API_KEY` — Groq hosted API (recommended for deployment and free cloud hosting)
- `OLLAMA_BASE_URL` — local Ollama (recommended for development and offline testing)

If `GROQ_API_KEY` is set, the app calls Groq first. If unavailable, it falls back to a local Ollama instance if `OLLAMA_BASE_URL` is reachable.

```bash
# Optional: Install Ollama for local testing
curl -fsSL https://ollama.com/install.sh | sh

# Pull local models
ollama pull mistral      # Data Query Agent (~4GB)
ollama pull llama3.1     # Policy Agent + Copilot (~4.7GB)

# Start Ollama server
ollama serve
```

> **Without any AI backend:** The dashboard and simulation system work fully. A deterministic fallback handles chatbot and copilot features. Data queries use keyword-based SQL; policy suggestions use the rule-based engine.

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `mci_scores` | Latest year scores per area — primary dashboard table |
| `mci_timeseries_scores` | All years — trend charts and policy agent context |
| `factor_subcomponent_scores` | Sub-component scores — radar charts |
| `rf_feature_importance` | Random Forest feature importance — intervention levers |
| `cluster_profiles` | K-Means cluster centroids and labels |

---

## Run Order

```bash
# 1. Install dependencies
pip install streamlit plotly duckdb pandas scikit-learn requests numpy --break-system-packages

# 2. Optional: start AI copilot backend
ollama pull mistral
ollama pull llama3.1
ollama serve

# 3. Pipeline (data processing — run in order)
python -m pipeline.preprocessor           # Raw data ingestion & cleaning
python -m pipeline.mci_pipeline           # Compute factor scores + MCI (all years)
python -m pipeline.store_dashboard_tables # Build cluster, RF importance, subcomponent tables

# 4. Launch dashboard
streamlit run dashboard/app.py
```

### File dependency graph

```
simulation_page.py
  ├── engine.py           (simulation computation)
  ├── cost_model.py       (cost / speed / feasibility)
  ├── optimizer.py        (uses engine + cost_model)
  ├── root_cause.py       (attribution)
  ├── recommendations.py  (uses engine + cost_model + tradeoff)
  ├── tradeoff.py         (tradeoff table data)
  └── copilot.py          (uses engine, root_cause)
```

No circular dependencies. All `simulation/` modules are pure Python with no Streamlit imports.

---

## Chatbot Agents

### Agent 1 — Data Query Agent
- **Model:** Mistral 7B (via Ollama) / `llama-3.1-8b-instant` (via Groq)
- **Fallback:** Keyword-based SQL builder (no AI backend needed)
- **Does:** Converts natural language questions to SQL, executes against DuckDB, suggests chart type
- **Example queries:** `"Which areas have the lowest MCI?"`, `"Show trend for Mumbai"`, `"Compare Tier 2 cities"`

### Agent 2 — Policy Suggestion Agent
- **Model:** LLaMA 3.1 8B (via Ollama) / `llama-3.3-70b-versatile` (via Groq)
- **Fallback:** Rule-based engine (`policy_engine/rules.py`)
- **Does:** Root cause analysis, scheme-specific recommendations, expected impact
- **Example queries:** `"Why is Dharavi low?"`, `"How can we improve women employment here?"`

### Orchestrator
Classifies user intent (data vs. policy) using keyword matching. Falls back to policy mode if an area is selected in the dashboard.

---

## Simulation System

The simulation system is the core analytical layer of the platform. It provides dual-mode policy intervention simulation, budget-constrained optimisation, root cause attribution, and explainable policy recommendations. All design decisions are documented below.

---

### Architecture

```
simulation/
  engine.py          — intervention definitions, factor recomputation, simulation
  cost_model.py      — cost, deployment speed, feasibility per intervention
  optimizer.py       — deterministic budget-constrained greedy optimizer
  tradeoff.py        — tradeoff table data (5 dimensions per intervention)
  root_cause.py      — gap-weighted attribution of MCI underperformance
  recommendations.py — ranked policy recommendation engine
  copilot.py         — AI copilot (LLaMA 3.1 via Ollama, structured fallback)

dashboard/
  simulation_page.py — Streamlit UI (dual-mode, budget bar, lever cards)
  app.py             — tab navigation entry point
```

---

### Intervention Cost Model

Costs are expressed as **₹ Crore per intensity point** (1–100 scale) for an average Indian district (~2 lakh households, ~200 gram panchayats, ~500 km²).

Cost is **linear with intensity**: `total cost = cost_per_point × intensity`. This is a deliberate simplification — real programmes have fixed overhead plus variable costs. Linear is used because it is transparent and auditable, avoids false precision given district-level aggregation, and enables straightforward budget enforcement in the optimizer.

| Intervention | Cost/pt (₹ Cr) | Source basis |
|---|---|---|
| Tower Deployment | 0.06 | BharatNet Phase-II: ~₹25–30 Cr per 1,000 GPs. 200 GPs per district ≈ ₹5–6 Cr at full deployment. |
| Fibre Backhaul | 0.20 | OFC laying ~₹3–5 lakh/km. 500 km district coverage ≈ ₹15–25 Cr. |
| Public WiFi (PM-WANI) | 0.02 | ₹2–5 lakh per hotspot × 50 hotspots = ₹1–2.5 Cr. |
| Device Subsidy | 0.90 | ₹2,500–3,500 per device × 30k BPL HH = ₹75–105 Cr. |
| Data Subsidy | 0.50 | ₹100–200/month × 12 months × 30k HH = ₹36–72 Cr/year. |
| Digital Literacy (PMGDISHA) | 0.04 | ₹1,000–1,500 per trainee × 30k trainees = ₹3–4.5 Cr. |
| Women Digital Skilling | 0.03 | Same unit cost, smaller cohort (~20k SHG members). |
| Community Internet Centre | 0.15 | ₹5–10 lakh/centre × 200 centres = ₹10–20 Cr. |
| Women Safety Digital | 0.02 | 181 helpline upgrades + CCTV: ₹0.5–2 Cr/district. |
| SHG Microfinance + Digital | 0.06 | NRLM revolving fund ₹15k × 300 SHGs + ₹1.5 Cr onboarding ≈ ₹6 Cr. |

> **Note on device subsidy:** This is the most expensive intervention per point due to direct asset transfer at district scale. Despite the high cost, it may still rank highly for "Women Employment" objectives because of its strong WDI uplift.

---

### Deployment Speed Logic

Speed is assigned based on **procurement complexity** and **institutional readiness**.

#### Fast (< 6 months to first measurable impact)
- No new physical infrastructure procurement
- Uses existing delivery channels (CSCs, SHGs, Jan Dhan, PMGDISHA)
- No spectrum allocation, RoW clearance, or civil works

*Assigned to:* device subsidy, data subsidy, digital literacy, women skilling, women safety digital, public WiFi (partial — PDO registration is fast).

#### Medium (6–18 months)
- Requires cross-department coordination
- Some procurement using framework contracts
- Building or space identification needed

*Assigned to:* public WiFi (full PM-WANI rollout), community internet centres, SHG microfinance onboarding.

#### Slow (18–36 months)
- New physical infrastructure
- Spectrum allocation + RoW clearance + contractor tendering
- Civil works (tower foundations, OFC trenching)

*Assigned to:* tower deployment, fibre backhaul.

> **Why this matters for optimization:** The "Fast Deployment" strategy applies a 0.45 weight to deployment speed vs 0.20 for impact — appropriate for policy contexts where visible outcomes within an electoral or budget cycle are required.

---

### Feasibility Logic

Feasibility reflects **implementation risk** — the probability that a programme achieves planned outcomes given institutional, political, and operational constraints.

| Label | Meaning | Criteria |
|---|---|---|
| High | Low risk, proven model | Single department, existing delivery infrastructure, no new legislation required |
| Medium | Moderate risk | Multi-department coordination, procurement needed, some political dependency |
| Low | High risk | New legislation, spectrum issues, major procurement, unclear accountability |

All interventions in this system are `high` or `medium`. Low feasibility interventions are excluded — they are not appropriate for district-level planning without higher-level enablers.

*Classification follows the Ministry of Finance GFMIS project classification rubric and NITI Aayog programme implementation risk ratings.*

---

### Optimization Strategies & Scoring

The optimizer scores each intervention using a **weighted linear combination** of four sub-scores, all normalised to [0, 1].

#### Sub-scores

| Sub-score | Formula |
|---|---|
| `impact_score` | `clamp(mci_delta / 20.0, 0, 1)` — max expected single-intervention delta is ~15–20 pts at 70% intensity |
| `eff_score` | `clamp((mci_delta / cost_cr) / 5.0, 0, 1)` — max expected efficiency ~5 MCI pts/₹ Crore |
| `speed_score` | `{Fast: 1.0, Medium: 0.5, Slow: 0.1}` — slow is not 0 to avoid fully excluding infra interventions |
| `feasibility_score` | `{high: 1.0, medium: 0.6, low: 0.2}` |

#### Strategy weights

| Sub-score | Cost Efficient | Balanced | Fast Deployment | High Feasibility |
|---|---|---|---|---|
| impact_score | 0.10 | 0.40 | 0.20 | 0.30 |
| eff_score | 0.55 | 0.25 | 0.15 | 0.15 |
| speed_score | 0.20 | 0.20 | 0.45 | 0.15 |
| feasibility_score | 0.15 | 0.15 | 0.20 | 0.40 |

**Cost Efficient:** `eff_score` dominates (0.55) — the goal is MCI uplift per rupee. Raw impact weight is low (0.10) because high absolute impact often comes with high cost.

**Fast Deployment:** `speed_score` dominates (0.45). Impact is still valued (0.20) to avoid fast but low-value interventions.

#### Objective alignment multiplier

Each intervention score is multiplied by `(0.5 + obj_weight)` where `obj_weight` is the selected objective's weight for the intervention's primary factor. This shifts the score range from 0.5× to 1.5× based on objective alignment.

| Objective | IFS | DLS | SES | WDI |
|---|---|---|---|---|
| Women Safety | 0.30 | 0.15 | 0.20 | 0.35 |
| Women Employment | 0.20 | 0.25 | 0.25 | 0.30 |
| Education | 0.35 | 0.35 | 0.20 | 0.10 |
| Healthcare | 0.40 | 0.20 | 0.25 | 0.15 |
| General Connectivity | 0.35 | 0.30 | 0.20 | 0.15 |
| Affordability | 0.20 | 0.35 | 0.30 | 0.15 |

*Weights are set by expert judgement. For example, Women Safety requires strong WDI (0.35) because gender vulnerability and crime barriers are the primary constraints on women's safe digital participation.*

---

### Budget Allocation Algorithm

The optimizer uses a **greedy descending allocation** approach.

#### Algorithm (budget-constrained mode)

```
1. Score all interventions at 70% intensity using selected strategy.
2. Sort by final score descending.
3. remaining_budget = total_budget_cr
4. For each intervention (best → worst):
   a. max_affordable_intensity = remaining_budget / cost_per_point_cr
   b. intensity = min(100, max_affordable_intensity)
   c. Round intensity DOWN to nearest 10 (clean slider values)
   d. If intensity < MIN_MEANINGFUL_INTENSITY (20%): skip
   e. Allocate this intensity
   f. remaining_budget -= cost_per_point_cr × intensity
5. Stop when budget exhausted or all interventions processed.
```

#### Why greedy instead of linear programming

1. **Interpretability** — Every allocation decision is traceable to a score. A policymaker can ask "why was tower deployment ranked first?" and get a clear answer.
2. **Scale** — With 10 interventions and intensity steps of 10 (11 options each), exhaustive search is 11¹⁰ ≈ 25 billion combinations. Integer LP would work but is a black box.
3. **Accuracy** — Greedy is within 5–10% of optimal here because costs are linear, there are no hard combinatorial constraints, and score ordering is stable across intensity levels.
4. **Auditability** — The allocation rationale list in `OptimizationResult` shows exactly what was allocated and why.

#### MIN_MEANINGFUL_INTENSITY = 20%

Below 20% intensity, most interventions produce < 1 pt MCI delta. Deploying 5 interventions at 10% each produces less total impact than 2 at 50% each, due to the diminishing-returns curve `√(intensity/100)`. The 20% floor enforces resource concentration.

#### Unlimited budget mode

Top 3 interventions by score → 70% intensity. Remaining interventions → 40% intensity if score ≥ 40% of the top score. This mirrors realistic "full programme" deployment.

---

### Factor Score Weights in MCI

MCI uses a **weighted geometric mean** (not arithmetic):

```
MCI = ((IFS+1)^0.35 × (DLS+1)^0.30 × (SES+1)^0.20 × (WDI+1)^0.15) - 1
```

The geometric mean ensures a score of 0 on any factor collapses the composite near zero — an area with fibre but no literate users is still a digital desert.

| Factor | Weight | Rationale |
|---|---|---|
| IFS | 0.35 | Infrastructure is the physical prerequisite. No other intervention works without connectivity. |
| DLS | 0.30 | Digital literacy is the demand-side prerequisite. Infrastructure without skills produces low utilisation. |
| SES | 0.20 | Structural enabler/barrier. Lower weight because SES changes slowly and is not directly addressable in a connectivity programme. |
| WDI | 0.15 | Satellite factor capturing the gender dimension. Kept separate from DLS because the policy mechanisms (SHG skilling, GVI reduction) are distinct from general literacy programmes. |

> **Analyst override:** Advanced Analyst Mode allows custom weight adjustment. Weights are normalised to sum to 1.0 before use.

---

### Social Outcome Metric Derivation

Six social outcome metrics are computed from simulated factor scores and proxy variable values. All are on a 0–100 scale.

```
women_connectivity     = 0.50×WDI + 0.30×any_phone_pct + 0.20×e_transactions
women_employment_score = 0.40×WEI + 0.35×msme_female_share + 0.25×(100-dependent_women_pct)
service_access_score   = 0.40×MCI + 0.35×e_transactions + 0.25×any_phone_pct
safe_digital_access    = 0.50×WSI + 0.30×(100-crime_rate) + 0.20×wireless_rural_td
women_msme_access      = 0.45×msme_female_share + 0.30×WDI + 0.25×non_agri_enterprise
digital_access_score   = 0.40×MCI + 0.30×any_phone_pct + 0.30×(100-illiteracy)
```

`women_connectivity` is WDI-dominated (0.50) because WDI directly captures gender-disaggregated access. `service_access_score` is MCI-dominated (0.40) because MCI already integrates infrastructure and literacy. Proxy variables add specificity that MCI alone cannot capture.

---

### Confidence Estimation

Confidence is a scalar in [0.30, 0.95]. It is **not a statistical confidence interval** — it is a policy-readability indicator of projection reliability.

**Base confidence: 0.75**

| Condition | Adjustment | Rationale |
|---|---|---|
| feasibility = high | +0.10 | Proven delivery model reduces implementation risk |
| MCI delta > 20 pts | −0.15 | Beyond observed programme outcomes in India |
| MCI delta > 15 pts | −0.08 | High end of observed outcomes |
| Baseline MCI < 25 | −0.08 | Severe desert — physical prerequisites not met |
| Reference evidence exists | +0.05 | Documented comparable outcome |
| Deployment speed = Fast | +0.05 | Less time for execution failures |

Minimum: 0.30. Maximum: 0.95.

> A regression-based confidence interval would require historical programme outcome data linked to district-level MCI scores — data that does not currently exist. Rule-based confidence is more honest than a spuriously precise ML confidence score trained on a small sample.

---

### Root Cause Attribution

Attribution computes each variable's contribution to the district's MCI gap.

**Gap definition:** `MCI gap = max(0, 75 - district_MCI)` — distance from the "Connected" threshold.

**Per-variable contribution:**
```
weighted_contribution = gap_score × factor_weight × (1 + rf_importance_boost)
```

Where:
- `gap_score` = `max(0, 75 - variable_score)` — how far below "connected"
- `factor_weight` = MCI factor weight for the variable's parent factor (IFS: 0.35, DLS: 0.30, SES: 0.20, WDI: 0.15)
- `rf_importance_boost` = `rf_importance × 5.0` if RF data available, else 0

**Contribution percentage:**
```
contribution_pct = weighted_contribution / sum(all weighted contributions) × 100
```

Factor weight ensures that an IFS variable at the same gap level as a WDI variable is rated more important. The RF importance boost means empirically predictive variables rank higher even if their absolute gap is moderate. If RF data is unavailable, the system degrades gracefully to `gap × factor_weight`.

---

### Tradeoff Table Logic

The tradeoff table compares interventions on five dimensions. The two most distinct are:

**Inclusion Gain (digital equity focus)**
- **High** — directly expands access for excluded groups (no-phone households, women, slums). Device subsidy eliminates the device barrier; women skilling closes the gender gap.
- **Medium** — improves access broadly but does not target specific excluded groups. Tower density expands coverage but does not address affordability or skills.
- **Low** — quality improvement for existing users only; does not expand who can connect. Fibre backhaul improves speed for connected users only.

**QoS Gain (quality of service)**
- **High** — measurable throughput/latency improvement (≥ 25% speed increase). Tower density, fibre backhaul.
- **Medium** — moderate quality improvement as a side effect. Public WiFi (shared bandwidth), community internet centres.
- **Low** — negligible network quality impact; demand/skills intervention. Device subsidy, digital literacy, SHG microfinance.

> Inclusion and QoS are intentionally orthogonal — they capture the **supply-demand duality** of digital exclusion. An area can have excellent QoS but low inclusion (high-speed network, low phone ownership), or high inclusion but poor QoS (many connected users, poor speeds). Policy must address both.

---

### Cost Efficiency Labelling

```
efficiency = mci_delta / total_cost_cr   (MCI pts per ₹ Crore)

HIGH   if efficiency ≥ 1.0 pts/Cr
MEDIUM if efficiency ≥ 0.3 pts/Cr
LOW    if efficiency < 0.3 pts/Cr
```

**Threshold rationale:**
- 1.0 pt/Cr: achievable by literacy programmes (₹0.04 Cr/pt, ~5 pts delta ≈ 125 pts/Cr).
- 0.3 pt/Cr: minimum acceptable efficiency — below this, less than 1 pt MCI per ₹3 Crore invested.
- Device subsidy (~0.06 pts/Cr at full cost) rates LOW because although its absolute impact is significant, the cost per point is very high.

---

### Policy Recommendation Ranking

Recommendations are scored using:

```
final_score = objective_alignment_score
            + feasibility_bonus
            + mci_delta × 0.01

objective_alignment_score =
  Σ(objective_weight[f] × factor_gap[f] × |delta[f]| / max(factor_gap[f], 1))
  for f in {IFS, DLS, SES, WDI}
```

This ensures:
1. Interventions addressing **actually weak factors** score higher (`factor_gap[f]` amplifies weak factors).
2. Interventions aligned with the **selected objective's priorities** score higher (`objective_weight[f]` amplifies relevant factors).
3. Interventions producing **larger deltas** score higher (`|delta[f]|` term).

The `0.01 × mci_delta` term is a small absolute-impact tie-breaker.

```
feasibility_bonus = {high: +0.15, medium: +0.05, low: -0.05}
```

**Primary gap penalty:** If an intervention's primary factor gap < 5 pts, its score is multiplied by 0.6. This prevents recommending, for example, tower deployment to a district where infrastructure is already adequate.

---

### Why-Selected Rationale Rules

The "why this was recommended" bullets are generated by rule-based checks. Each rule tests a measurable condition and produces one sentence. Up to 4 reasons per recommendation, in priority order:

1. **Primary factor weakness:** `factor_gap[primary_factor] > 5`
   → *"X is a primary weak factor (driver: Y) — this intervention addresses it."*

2. **Objective alignment:** `objective_weight[primary_factor] ≥ 0.25`
   → *"Strongly aligned with [objective] (factor weight Z%)."*

3. **Cost efficiency:**
   - HIGH → *"High impact per ₹ invested (cost tier, +X MCI pts at 70%)."*
   - MEDIUM → *"Moderate cost efficiency; +X MCI pts projected."*

4. **Deployment speed:**
   - Fast → *"Rapid deployment possible (timeline) via existing channels."*
   - Medium → *"Deployable within [timeline]."*

5. **District-specific:**
   - MCI < 25 + IFS primary → *"Severe desert — infrastructure is prerequisite."*
   - women_digital_skilling + GVI > 40 → *"High GVI indicates women-specific exclusion."*

---

## Config

Edit `config.py` to change:

| Key | Default | Description |
|---|---|---|
| `DB_PATH` | `"database.duckdb"` | Path to your DuckDB database |
| `BASELINE_YEAR` | `2021` | Normalisation anchor year |
| `LATEST_YEAR` | `2024` | Default display year |
| `MCI_WEIGHTS` | `{IFS:0.35, DLS:0.30, SES:0.20, WDI:0.15}` | Factor weights in the geometric mean |
| `DATA_AGENT_MODEL` | `"llama-3.1-8b-instant"` | Groq model for data query generation |
| `POLICY_AGENT_MODEL` | `"llama-3.3-70b-versatile"` | Groq model for policy/copilot output |
| `OLLAMA_BASE_URL` | `"http://localhost:11434"` | Ollama host if running on a different port |
| `GROQ_API_KEY` | — | Groq API key for hosted LLM inference |

---

## Deployment

### Recommended: Streamlit Community Cloud (fastest — ~5 minutes)

- Free tier: unlimited apps, fast cold starts (~5–10 seconds), zero config files
- Auto-redeploys on `git push`
- See `DEPLOY_TO_STREAMLIT_CLOUD.md` for step-by-step guide

```bash
# 1. Push to GitHub
git add . && git commit -m "Deploy" && git push origin main

# 2. Go to https://streamlit.io/cloud → Sign up with GitHub
# 3. Click "New app" → Select repo → Deploy
# Done — URL: https://your-app.streamlit.app
```

### Alternative: Docker + Render (~15 minutes)

- Requires `Dockerfile`, `.dockerignore`, `requirements-runtime.txt`
- Free tier auto-sleeps (cold starts ~30s); $7/month for always-on
- See `DEPLOY_TO_RENDER.md` for step-by-step guide

### Alternative: Cloud Run (Google Cloud)

- Pay-per-request (~$0–5/month)
- Better cold-start performance than Render free tier

### How DuckDB access works (local vs. deployed)

```python
# config.py — same line works in both environments
DB_PATH = "database.duckdb"

# Local:   resolves to  ./database.duckdb  (your project folder)
# Deployed: resolves to /app/database.duckdb (cloned from GitHub)
```

See `DEPLOYMENT_DB_GUIDE.md` for the full technical walkthrough, and `COMPARISON_STREAMLIT_VS_DOCKER.md` for a detailed comparison of deployment options.

---

## Extending the Policy Engine

Add new rules in `policy_engine/rules.py` by appending to the `RULES` list:

```python
{
    "condition":   lambda s: s.get("YOUR_SCORE_KEY", 100) < YOUR_THRESHOLD,
    "priority":    1,        # 1=urgent, 2=moderate, 3=advisory
    "category":    "IFS",    # factor this targets
    "short_title": "Your intervention title",
    "action":      "What specifically to do",
    "rationale":   "Why this score triggers this rule",
    "scheme":      "Government scheme name",
}
```