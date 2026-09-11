import sys
from pathlib import Path
import textwrap

# ============================================================
# POWERGRID PROJECT ROOT PATH
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# STREAMLIT / DATA / PLOTLY
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# ============================================================
# HTML / MARKDOWN RENDERING HELPER
# ============================================================

def render_markdown(content, **kwargs):
    """
    Render HTML safely without allowing Python indentation
    to turn HTML into a Markdown code block.
    """

    if not isinstance(content, str):
        return st.markdown(
            content,
            **kwargs
        )

    cleaned = content.strip()

    # --------------------------------------------------------
    # HTML/CSS blocks
    # --------------------------------------------------------

    if (
        cleaned.startswith("<")
        or "<div" in cleaned
        or "<style" in cleaned
        or "</div>" in cleaned
    ):

        try:

            st.html(
                cleaned
            )

            return

        except AttributeError:

            # Fallback for older Streamlit versions
            lines = cleaned.splitlines()

            cleaned = "\n".join(
                line.lstrip()
                for line in lines
            )

    return st.markdown(
        cleaned,
        **kwargs
    )


# ============================================================
# APPLICATION SERVICE
# ============================================================

from src.application_service import (
    get_projects,
    analyze_project,
    analyze_what_if,
    predict_new_project
)


# ============================================================
# POWERGRID PROJECT INTELLIGENCE
# V2 DASHBOARD
# ============================================================


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="POWERGRID Project Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# GLOBAL CSS
# ============================================================

render_markdown(
    """
    
<style>

/* ============================================================
   POWERPREDICT
   Clean Enterprise Decision-Support Interface
   ============================================================ */

:root {
    --pp-bg: #f7f9fc;
    --pp-card: #ffffff;
    --pp-primary: #1769e0;
    --pp-primary-dark: #1256b8;

    --pp-text: #172b4d;
    --pp-text-secondary: #425466;
    --pp-muted: #6b7c93;

    --pp-border: #e4e9f0;

    --pp-high: #d64545;
    --pp-medium: #d99a00;
    --pp-low: #16834a;

    --pp-shadow:
        0 2px 8px rgba(23, 43, 77, 0.05);
}

/* ============================================================
   GLOBAL
   ============================================================ */

.stApp {
    background: var(--pp-bg);
}

.main .block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
    padding-left: 2.4rem;
    padding-right: 2.4rem;
}

/* ============================================================
   TYPOGRAPHY
   ============================================================ */

html,
body,
[class*="css"] {
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

h1 {
    color: var(--pp-text) !important;
    font-size: 2rem !important;
    font-weight: 750 !important;
    letter-spacing: -0.025em;
}

h2 {
    color: var(--pp-text) !important;
    font-size: 1.45rem !important;
    font-weight: 700 !important;
}

h3 {
    color: #294766 !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
}

p {
    color: var(--pp-text-secondary);
}

/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--pp-border);
}

[data-testid="stSidebar"] * {
    color: var(--pp-text);
}

[data-testid="stSidebar"] .stRadio label {
    font-weight: 600;
    font-size: 0.9rem;
}

[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--pp-primary);
}

/* ============================================================
   SECTION LABEL
   ============================================================ */

.section-label {
    color: var(--pp-primary);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}

/* ============================================================
   DASHBOARD CARDS
   ============================================================ */

.dashboard-card {
    background: var(--pp-card);
    border: 1px solid var(--pp-border);
    border-radius: 10px;
    padding: 1.25rem;
    box-shadow: var(--pp-shadow);
}

.metric-label {
    color: var(--pp-muted);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.025em;
}

.metric-value {
    color: var(--pp-text);
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1.2;
    margin-top: 0.3rem;
}

.metric-description {
    color: var(--pp-muted);
    font-size: 0.76rem;
    margin-top: 0.4rem;
}

/* ============================================================
   HERO
   ============================================================ */

.hero {
    background: #ffffff;
    border: 1px solid var(--pp-border);
    border-radius: 12px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--pp-shadow);
}

.hero-title {
    color: var(--pp-text);
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.03em;
}

.hero-subtitle {
    color: var(--pp-muted);
    font-size: 0.95rem;
    margin-top: 0.45rem;
}

/* ============================================================
   PROJECT HEADER
   ============================================================ */

.project-header {
    background: #ffffff;
    border: 1px solid var(--pp-border);
    border-radius: 10px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: var(--pp-shadow);
}

.project-code {
    color: var(--pp-primary);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.project-name {
    color: var(--pp-text);
    font-size: 1.55rem;
    font-weight: 800;
    margin-top: 0.25rem;
}

.project-category {
    color: var(--pp-muted);
    font-size: 0.82rem;
    margin-top: 0.35rem;
}

/* ============================================================
   RISK PANELS
   ============================================================ */

.risk-panel {
    background: #ffffff;
    border: 1px solid var(--pp-border);
    border-radius: 10px;
    padding: 1.35rem;
    min-height: 145px;
    box-shadow: var(--pp-shadow);
}

.risk-panel-label {
    color: var(--pp-muted);
    font-size: 0.73rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.risk-panel-score {
    font-size: 2.35rem;
    font-weight: 850;
    margin-top: 0.5rem;
}

.risk-panel-level {
    font-size: 0.88rem;
    font-weight: 800;
    margin-top: 0.15rem;
}

/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    min-height: 42px;
    border-radius: 8px;
    border: 1px solid var(--pp-primary);
    background: var(--pp-primary);
    color: #ffffff;
    font-weight: 700;
    padding: 0.55rem 1.15rem;
}

.stButton > button:hover {
    background: var(--pp-primary-dark);
    border-color: var(--pp-primary-dark);
}

/* ============================================================
   INPUTS
   ============================================================ */

.stTextInput input,
.stNumberInput input {
    border-radius: 8px;
    border-color: var(--pp-border);
    background: #ffffff;
}

div[data-baseweb="select"] > div {
    border-radius: 8px;
    border-color: var(--pp-border);
    background: #ffffff;
}

/* ============================================================
   TABLES
   ============================================================ */

[data-testid="stDataFrame"] {
    border: 1px solid var(--pp-border);
    border-radius: 8px;
    overflow: hidden;
}

/* ============================================================
   ALERTS
   ============================================================ */

.stAlert {
    border-radius: 8px;
}

/* ============================================================
   DIVIDERS
   ============================================================ */

hr {
    border-color: var(--pp-border) !important;
}

/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 900px) {

    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    h1 {
        font-size: 1.65rem !important;
    }

    .hero-title {
        font-size: 1.65rem;
    }

    .metric-value {
        font-size: 1.5rem;
    }
}

</style>

    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_projects():

    return get_projects()


@st.cache_data
def load_analysis(project_code):

    return analyze_project(
        project_code
    )


# ============================================================
# LOAD REAL PROJECTS
# ============================================================

projects_df = load_projects()

project_codes = (
    projects_df[
        "project_code"
    ]
    .astype(str)
    .tolist()
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_markdown(
        """
        <div style="
            font-size:1.45rem;
            font-weight:850;
            letter-spacing:-0.03em;
        ">
            ⚡ POWERGRID
        </div>

        <div style="
            color:#91abc0;
            font-size:0.75rem;
            font-weight:700;
            letter-spacing:0.08em;
            margin-top:3px;
        ">
            PROJECT INTELLIGENCE
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    render_markdown(
        "### Navigation"
    )

    page = st.radio(

        "Navigation",

        [
            "Command Center",
            "New Project Prediction",
            "Project Intelligence",
            "Trajectory",
            "Scenario Lab",
            "Compare Projects",
            "Model & Methodology"
        ],

        label_visibility="collapsed"
    )

    st.divider()

    render_markdown(
        "### System Status"
    )

    st.success(
        "● V2 ML MODELS ACTIVE"
    )

    st.caption(
        "92 validated projects"
    )

    st.caption(
        "69 cost training projects"
    )

    st.caption(
        "68 schedule training projects"
    )

    st.caption(
        "23 unseen test projects"
    )

    st.divider()

    render_markdown(
        "### Final Models"
    )

    st.caption(
        "Random Forest • Cost"
    )

    st.caption(
        "Extra Trees • Schedule"
    )

    st.caption(
        "12 model features"
    )

    st.divider()

    render_markdown(
        "### Data Policy"
    )

    st.caption(
        "✓ Real POWERGRID data"
    )

    st.caption(
        "✓ No synthetic data"
    )

    st.caption(
        "✓ No PDF rows appended"
    )

    st.caption(
        "✓ Project-level validation"
    )

    st.divider()

    st.caption(
        "POWERGRID"
    )

    st.caption(
        "POWERGRID Project Risk Intelligence"
    )


# ============================================================
# ============================================================
# COMMAND CENTER
# ============================================================
# ============================================================

if page == "Command Center":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    render_markdown(
        """
        <div class="hero">

            <div class="hero-title">
                POWERGRID Project Intelligence
            </div>

            <div class="hero-subtitle">
                AI-assisted cost, schedule and risk intelligence
                for power infrastructure projects.
            </div>

            <div class="hero-status">
                ● V2 MODEL ACTIVE
                &nbsp;&nbsp;•&nbsp;&nbsp;
                REAL PROJECT DATA
                &nbsp;&nbsp;•&nbsp;&nbsp;
                PROJECT-LEVEL VALIDATION
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # PORTFOLIO ANALYSIS
    # --------------------------------------------------------

    @st.cache_data
    def build_portfolio():

        rows = []

        progress = st.progress(
            0,
            text="Building portfolio intelligence..."
        )

        total = len(project_codes)

        for i, code in enumerate(project_codes):

            try:

                result = load_analysis(
                    code
                )

                prediction = result[
                    "prediction"
                ]

                snapshot = result[
                    "snapshot"
                ]

                rows.append({

                    "project_code":
                        code,

                    "project_name":
                        str(
                            snapshot[
                                "project_name"
                            ]
                        ),

                    "risk_level":
                        prediction[
                            "cost_risk_level"
                        ],

                    "risk_score":
                        prediction[
                            "cost_risk_score"
                        ],

                    "cost_prediction":
                        prediction[
                            "cost_prediction_pct"
                        ],

                    "schedule_prediction":
                        prediction[
                            "schedule_prediction_months"
                        ],

                    "expenditure_pct":
                        prediction[
                            "expenditure_pct"
                        ],

                    "physical_progress_pct":
                        prediction[
                            "physical_progress_pct"
                        ],

                    "schedule_pressure":
                        prediction[
                            "schedule_pressure_ratio"
                        ],

                    "original_cost":
                        float(
                            snapshot[
                                "original_cost_cr"
                            ]
                        )
                })

            except Exception:
                pass

            progress.progress(
                (i + 1) / total
            )

        progress.empty()

        return pd.DataFrame(
            rows
        )


    portfolio = build_portfolio()


    # --------------------------------------------------------
    # PORTFOLIO METRICS
    # --------------------------------------------------------

    high_count = int(
        (
            portfolio[
                "risk_level"
            ] == "HIGH"
        ).sum()
    )

    medium_count = int(
        (
            portfolio[
                "risk_level"
            ] == "MEDIUM"
        ).sum()
    )

    low_count = int(
        (
            portfolio[
                "risk_level"
            ] == "LOW"
        ).sum()
    )


    # --------------------------------------------------------
    # METRIC CARDS
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">Portfolio Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(
        4,
        gap="medium"
    )


    with c1:

        render_markdown(
            f"""
            <div class="dashboard-card">

                <div class="metric-label">
                    Projects
                </div>

                <div class="metric-value">
                    {len(portfolio)}
                </div>

                <div class="metric-description">
                    Validated project portfolio
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c2:

        render_markdown(
            f"""
            <div class="dashboard-card">

                <div class="metric-label">
                    High Risk
                </div>

                <div class="metric-value"
                     style="color:#c92a38;">
                    {high_count}
                </div>

                <div class="metric-description">
                    Projects requiring attention
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c3:

        render_markdown(
            f"""
            <div class="dashboard-card">

                <div class="metric-label">
                    Medium Risk
                </div>

                <div class="metric-value"
                     style="color:#a66b00;">
                    {medium_count}
                </div>

                <div class="metric-description">
                    Projects to monitor
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c4:

        render_markdown(
            f"""
            <div class="dashboard-card">

                <div class="metric-label">
                    Low Risk
                </div>

                <div class="metric-value"
                     style="color:#16834a;">
                    {low_count}
                </div>

                <div class="metric-description">
                    Currently stable
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    st.write("")


    # --------------------------------------------------------
    # PORTFOLIO CHARTS
    # --------------------------------------------------------

    left, right = st.columns(
        [1.35, 1],
        gap="large"
    )


    # --------------------------------------------------------
    # RISK DISTRIBUTION
    # --------------------------------------------------------

    with left:

        render_markdown(
            '<div class="section-label">Portfolio Risk Distribution</div>',
            unsafe_allow_html=True
        )

        risk_counts = pd.DataFrame({

            "Risk":
                [
                    "LOW",
                    "MEDIUM",
                    "HIGH"
                ],

            "Projects":
                [
                    low_count,
                    medium_count,
                    high_count
                ]
        })

        fig = px.bar(
            risk_counts,
            x="Risk",
            y="Projects",
            text="Projects"
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(

            height=330,

            margin=dict(
                l=10,
                r=10,
                t=30,
                b=10
            ),

            plot_bgcolor="white",
            paper_bgcolor="white",

            font=dict(
                color="#173b5c"
            ),

            xaxis_title="",
            yaxis_title="Projects"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # PORTFOLIO SIGNAL
    # --------------------------------------------------------

    with right:

        render_markdown(
            '<div class="section-label">Portfolio Signal</div>',
            unsafe_allow_html=True
        )

        if high_count > 0:

            render_markdown(
                f"""
                <div class="dashboard-card">

                    <div style="
                        color:#b42332;
                        font-size:1.15rem;
                        font-weight:800;
                    ">
                        ⚠ Attention Required
                    </div>

                    <div style="
                        color:#627d98;
                        margin-top:10px;
                        line-height:1.6;
                    ">
                        <b style="
                            color:#173b5c;
                            font-size:1.2rem;
                        ">
                            {high_count}
                        </b>
                        projects are currently classified
                        as <b>HIGH RISK</b>.
                    </div>

                    <div style="
                        color:#829ab1;
                        margin-top:12px;
                        font-size:0.78rem;
                    ">
                        Select a project from Project
                        Intelligence for detailed analysis.
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.success(
                "No high-risk projects detected."
            )


    st.write("")


    # --------------------------------------------------------
    # RISK VS SCHEDULE PRESSURE
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">Portfolio Risk Landscape</div>',
        unsafe_allow_html=True
    )

    fig = px.scatter(

        portfolio,

        x="expenditure_pct",

        y="schedule_pressure",

        size="original_cost",

        hover_name="project_code",

        hover_data={
            "project_name": True,
            "risk_level": True,
            "risk_score": True,
            "cost_prediction": ":.2f",
            "schedule_prediction": ":.2f",
            "expenditure_pct": ":.2f",
            "schedule_pressure": ":.2f",
            "original_cost": ":.2f"
        },

        labels={
            "expenditure_pct":
                "Expenditure / Approved Cost (%)",

            "schedule_pressure":
                "Schedule Pressure Ratio"
        }
    )

    fig.update_layout(

        height=460,

        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),

        plot_bgcolor="white",
        paper_bgcolor="white",

        font=dict(
            color="#173b5c"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # ATTENTION TABLE
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">Projects Requiring Attention</div>',
        unsafe_allow_html=True
    )

    attention = (
        portfolio[
            portfolio[
                "risk_level"
            ] == "HIGH"
        ]
        .sort_values(
            "risk_score",
            ascending=False
        )
        .head(10)
    )

    if not attention.empty:

        display = attention[
            [
                "project_code",
                "risk_score",
                "cost_prediction",
                "schedule_prediction",
                "expenditure_pct"
            ]
        ].copy()

        display.columns = [

            "Project",

            "Risk Score",

            "Predicted Cost Overrun (%)",

            "Predicted Delay (months)",

            "Expenditure (%)"
        ]

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# ============================================================
# PROJECT INTELLIGENCE
# ============================================================
# ============================================================


# ============================================================
# NEW PROJECT PREDICTION
# ============================================================

# ============================================================
# NEW PROJECT PREDICTION
# ============================================================

elif page == "New Project Prediction":

    # ========================================================
    # PAGE-SPECIFIC CSS
    # ========================================================

    st.markdown(
        """
        <style>

        /* ----------------------------------------------------
           PAGE BACKGROUND
           ---------------------------------------------------- */

        .prediction-page {
            max-width: 1200px;
            margin: 0 auto;
        }


        /* ----------------------------------------------------
           INTRO CARD
           ---------------------------------------------------- */

        .prediction-intro {
            background: linear-gradient(
                135deg,
                #102a43 0%,
                #173b5c 100%
            );

            padding: 28px 32px;
            border-radius: 16px;
            margin-top: 10px;
            margin-bottom: 28px;

            box-shadow:
                0 8px 25px rgba(16, 42, 67, 0.12);
        }

        .prediction-intro-title {
            color: white;
            font-size: 1.55rem;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .prediction-intro-text {
            color: #d9e7f2;
            font-size: 0.95rem;
            line-height: 1.6;
            margin: 0;
        }


        /* ----------------------------------------------------
           STEP LABEL
           ---------------------------------------------------- */

        .form-step {
            color: #52718c;
            font-size: 0.75rem;
            font-weight: 850;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-top: 26px;
            margin-bottom: 5px;
        }

        .form-step-title {
            color: #102a43;
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 5px;
        }

        .form-step-description {
            color: #627d98;
            font-size: 0.88rem;
            margin-bottom: 18px;
        }


        /* ----------------------------------------------------
           INPUT LABELS
           ---------------------------------------------------- */

        div[data-testid="stNumberInput"] label,
        div[data-testid="stSelectbox"] label {
            color: #173b5c !important;
            font-weight: 700 !important;
            font-size: 0.88rem !important;
        }

        div[data-testid="stNumberInput"] [data-testid="stWidgetLabel"] p,
        div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p {
            color: #173b5c !important;
            font-weight: 700 !important;
        }


        /* ----------------------------------------------------
           INPUT BOXES
           ---------------------------------------------------- */

        div[data-testid="stNumberInput"] input {
            color: #102a43 !important;
            font-weight: 650 !important;
        }

        div[data-baseweb="select"] > div {
            background: white !important;
            border: 1px solid #cbd8e5 !important;
            border-radius: 10px !important;
        }


        /* ----------------------------------------------------
           HELP TEXT
           ---------------------------------------------------- */

        div[data-testid="stNumberInput"] small,
        div[data-testid="stSelectbox"] small {
            color: #6b8297 !important;
        }


        /* ----------------------------------------------------
           PREDICTION BUTTON
           ---------------------------------------------------- */

        .prediction-button {
            margin-top: 20px;
            margin-bottom: 20px;
        }

        .prediction-button button {
            min-height: 52px !important;
            border-radius: 10px !important;
            font-size: 1rem !important;
            font-weight: 800 !important;
        }


        /* ----------------------------------------------------
           RESULT CARDS
           ---------------------------------------------------- */

        .result-card {
            background: white;
            border: 1px solid #dce6ef;
            border-radius: 14px;
            padding: 22px;
            min-height: 145px;

            box-shadow:
                0 5px 18px rgba(16, 42, 67, 0.06);
        }

        .result-label {
            color: #627d98;
            font-size: 0.78rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .result-value {
            color: #102a43;
            font-size: 2rem;
            font-weight: 850;
            margin-top: 8px;
        }

        .result-description {
            color: #829ab0;
            font-size: 0.78rem;
            margin-top: 5px;
        }


        /* ----------------------------------------------------
           RISK CARD
           ---------------------------------------------------- */

        .risk-result {
            background: #fffaf0;
            border: 1px solid #f2d48a;
            border-radius: 14px;
            padding: 24px;
            margin-top: 22px;
        }

        .risk-result-title {
            color: #765b13;
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .risk-result-score {
            color: #102a43;
            font-size: 2.4rem;
            font-weight: 900;
            margin-top: 5px;
        }


        /* ----------------------------------------------------
           INFO BOX
           ---------------------------------------------------- */

        .input-note {
            background: #eef6fc;
            border-left: 4px solid #1683ff;
            padding: 13px 16px;
            border-radius: 8px;
            color: #36566f;
            font-size: 0.85rem;
            line-height: 1.5;
            margin-top: 8px;
            margin-bottom: 18px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # PAGE HEADER
    # ========================================================

    render_markdown(
        '<div class="section-label">DECISION SUPPORT</div>',
        unsafe_allow_html=True
    )

    st.title(
        "New Project Prediction"
    )

    render_markdown(
        """
        <div class="prediction-intro">

            <div class="prediction-intro-title">
                Predict Project Cost & Schedule Risk
            </div>

            <p class="prediction-intro-text">
                Enter the current information for a project that is
                not yet in the validated project database. The V2
                machine-learning models will estimate expected cost
                overrun, schedule delay, and explainable project risk.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # INPUT FORM
    # ========================================================

    with st.form(
        "new_project_prediction_form"
    ):

        # ----------------------------------------------------
        # STEP 1 — PROJECT INFORMATION
        # ----------------------------------------------------

        render_markdown(
            """
            <div class="form-step">
                Step 1
            </div>

            <div class="form-step-title">
                Project Information
            </div>

            <div class="form-step-description">
                Enter the basic financial information and project
                category.
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(
            2,
            gap="large"
        )


        with c1:

            original_cost = st.number_input(
                "Original Approved Cost (₹ Cr)",
                min_value=0.01,
                value=1000.0,
                step=10.0,
                help=(
                    "The original approved project cost in "
                    "crore rupees."
                )
            )


        with c2:

            project_category = st.selectbox(
                "Project Category",
                options=[
                    "Substation_Grid_Equipment",
                    "Transmission_System",
                    "Transmission_Line",
                    "Substation",
                    "Other"
                ],
                help=(
                    "Select the category that best describes "
                    "the project."
                )
            )


        # ----------------------------------------------------
        # STEP 2 — CURRENT PROJECT STATUS
        # ----------------------------------------------------

        render_markdown(
            """
            <div class="form-step">
                Step 2
            </div>

            <div class="form-step-title">
                Current Project Status
            </div>

            <div class="form-step-description">
                Tell the system how much money has been spent and
                how much physical work has been completed.
            </div>

            <div class="input-note">
                <strong>Tip:</strong>
                These two values are especially important because
                the model compares expenditure against physical
                progress to identify possible cost pressure.
            </div>
            """,
            unsafe_allow_html=True
        )


        c1, c2 = st.columns(
            2,
            gap="large"
        )


        with c1:

            cumulative_expenditure = st.number_input(
                "Cumulative Expenditure (₹ Cr)",
                min_value=0.0,
                value=600.0,
                step=10.0,
                help=(
                    "Total amount spent on the project so far, "
                    "in crore rupees."
                )
            )


        with c2:

            physical_progress = st.number_input(
                "Physical Progress (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
                step=1.0,
                help=(
                    "Approximate percentage of physical work "
                    "completed so far."
                )
            )


        # ----------------------------------------------------
        # STEP 3 — SCHEDULE
        # ----------------------------------------------------

        render_markdown(
            """
            <div class="form-step">
                Step 3
            </div>

            <div class="form-step-title">
                Schedule Information
            </div>

            <div class="form-step-description">
                Enter the planned project duration and the amount
                of time already elapsed.
            </div>
            """,
            unsafe_allow_html=True
        )


        c1, c2 = st.columns(
            2,
            gap="large"
        )


        with c1:

            planned_duration = st.number_input(
                "Planned Duration (months)",
                min_value=1.0,
                value=36.0,
                step=1.0,
                help=(
                    "Original planned duration of the project "
                    "in months."
                )
            )


        with c2:

            elapsed_duration = st.number_input(
                "Elapsed Duration (months)",
                min_value=0.0,
                value=20.0,
                step=1.0,
                help=(
                    "Number of months that have passed since "
                    "the project started."
                )
            )


        # ----------------------------------------------------
        # STEP 4 — PROJECT TRAJECTORY
        # ----------------------------------------------------

        render_markdown(
            """
            <div class="form-step">
                Step 4
            </div>

            <div class="form-step-title">
                Project Trajectory
            </div>

            <div class="form-step-description">
                Describe the current speed of physical progress
                and expenditure.
            </div>

            <div class="input-note">
                <strong>Why this matters:</strong>
                Velocity features help the model understand whether
                the project is progressing quickly enough relative
                to its current spending pattern.
            </div>
            """,
            unsafe_allow_html=True
        )


        c1, c2 = st.columns(
            2,
            gap="large"
        )


        with c1:

            progress_velocity = st.number_input(
                "Progress Velocity (% / month)",
                min_value=0.0,
                value=2.0,
                step=0.1,
                help=(
                    "Average physical progress achieved per month."
                )
            )


        with c2:

            expenditure_velocity = st.number_input(
                "Expenditure Velocity (₹ Cr / month)",
                min_value=0.0,
                value=20.0,
                step=1.0,
                help=(
                    "Average expenditure incurred per month."
                )
            )


        # ----------------------------------------------------
        # SUBMIT
        # ----------------------------------------------------

        render_markdown(
            """
            <div class="form-step">
                Step 5
            </div>

            <div class="form-step-title">
                Run Prediction
            </div>

            <div class="form-step-description">
                Review the values above and run the V2 prediction.
            </div>
            """,
            unsafe_allow_html=True
        )


        submitted = st.form_submit_button(
            "⚡ Run V2 Project Prediction",
            type="primary",
            use_container_width=True
        )


    # ========================================================
    # RUN MODEL
    # ========================================================

    if submitted:

        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        validation_errors = []


        if original_cost <= 0:

            validation_errors.append(
                "Original approved cost must be greater than zero."
            )


        if cumulative_expenditure < 0:

            validation_errors.append(
                "Cumulative expenditure cannot be negative."
            )


        if physical_progress < 0 or physical_progress > 100:

            validation_errors.append(
                "Physical progress must be between 0% and 100%."
            )


        if planned_duration <= 0:

            validation_errors.append(
                "Planned duration must be greater than zero."
            )


        if elapsed_duration < 0:

            validation_errors.append(
                "Elapsed duration cannot be negative."
            )


        if progress_velocity < 0:

            validation_errors.append(
                "Progress velocity cannot be negative."
            )


        if expenditure_velocity < 0:

            validation_errors.append(
                "Expenditure velocity cannot be negative."
            )


        if validation_errors:

            st.error(
                "Please correct the following inputs:"
            )

            for error in validation_errors:

                st.warning(
                    error
                )

        else:

            # ------------------------------------------------
            # Build user input
            # ------------------------------------------------

            new_project = {

                "original_approved_cost":
                    float(original_cost),

                "project_category":
                    project_category,

                "cumulative_expenditure":
                    float(cumulative_expenditure),

                "physical_progress_pct":
                    float(physical_progress),

                "planned_duration_months":
                    float(planned_duration),

                "elapsed_duration_months":
                    float(elapsed_duration),

                "progress_velocity":
                    float(progress_velocity),

                "expenditure_velocity":
                    float(expenditure_velocity)

            }


            # ------------------------------------------------
            # Run V2 model
            # ------------------------------------------------

            with st.spinner(
                "Running V2 cost, schedule and risk analysis..."
            ):

                try:

                    result = predict_new_project(
                        new_project
                    )

                    st.session_state[
                        "new_project_prediction"
                    ] = result

                    st.success(
                        "Prediction completed successfully."
                    )

                except Exception as e:

                    st.error(
                        "The prediction could not be completed."
                    )

                    st.exception(
                        e
                    )


    # ========================================================
    # RESULTS
    # ========================================================

    if "new_project_prediction" in st.session_state:

        result = st.session_state[
            "new_project_prediction"
        ]


        prediction = result.get(
            "prediction",
            {}
        )


        # ----------------------------------------------------
        # RESULTS HEADER
        # ----------------------------------------------------

        render_markdown(
            """
            <div class="form-step">
                Prediction Results
            </div>

            <div class="form-step-title">
                V2 Model Assessment
            </div>

            <div class="form-step-description">
                These results are generated from the project values
                you entered above.
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # COST RESULT
        # ----------------------------------------------------

        cost_prediction = prediction.get(
            "cost_prediction_pct",
            prediction.get(
                "predicted_cost_overrun_pct",
                None
            )
        )


        schedule_prediction = prediction.get(
            "schedule_prediction_months",
            prediction.get(
                "predicted_schedule_delay_months",
                None
            )
        )


        risk_score = prediction.get(
            "cost_risk_score",
            prediction.get(
                "risk_score",
                None
            )
        )


        risk_level = prediction.get(
            "cost_risk_level",
            prediction.get(
                "risk_level",
                "N/A"
            )
        )


        r1, r2, r3 = st.columns(
            3,
            gap="large"
        )


        with r1:

            cost_text = (
                f"{float(cost_prediction):.2f}%"
                if cost_prediction is not None
                else "N/A"
            )

            render_markdown(
                f"""
                <div class="result-card">

                    <div class="result-label">
                        Predicted Final Cost Overrun
                    </div>

                    <div class="result-value">
                        {cost_text}
                    </div>

                    <div class="result-description">
                        Predicted additional cost
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        with r2:

            schedule_text = (
                f"{float(schedule_prediction):.2f} months"
                if schedule_prediction is not None
                else "N/A"
            )

            render_markdown(
                f"""
                <div class="result-card">

                    <div class="result-label">
                        Predicted Final Schedule Delay
                    </div>

                    <div class="result-value">
                        {schedule_text}
                    </div>

                    <div class="result-description">
                        Predicted delay beyond schedule
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        with r3:

            risk_text = (
                f"{float(risk_score):.1f} / 100"
                if risk_score is not None
                else "N/A"
            )

            render_markdown(
                f"""
                <div class="result-card">

                    <div class="result-label">
                        Explainable Risk Score
                    </div>

                    <div class="result-value">
                        {risk_text}
                    </div>

                    <div class="result-description">
                        Risk level: {risk_level}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # RISK INTERPRETATION
        # ----------------------------------------------------

        reasons = prediction.get(
            "cost_risk_reasons",
            []
        )


        warnings = prediction.get(
            "cost_risk_warnings",
            []
        )


        render_markdown(
            """
            <div class="form-step">
                Explainable Risk
            </div>

            <div class="form-step-title">
                Why does the model see this level of risk?
            </div>
            """,
            unsafe_allow_html=True
        )


        if reasons:

            for reason in reasons:

                st.warning(
                    f"⚠ {reason}"
                )

        else:

            st.info(
                "No specific cost-risk reason was returned "
                "by the model."
            )


        if warnings:

            for warning in warnings:

                st.info(
                    f"ℹ {warning}"
                )


        # ----------------------------------------------------
        # PREPARED MODEL INPUT
        # ----------------------------------------------------

        prepared_input = result.get(
            "input",
            {}
        )


        if prepared_input:

            with st.expander(
                "View values sent to the V2 model"
            ):

                display_input = pd.DataFrame(
                    {
                        "Feature":
                            list(
                                prepared_input.keys()
                            ),

                        "Value":
                            list(
                                prepared_input.values()
                            )
                    }
                )


                st.dataframe(
                    display_input,
                    use_container_width=True,
                    hide_index=True
                )


        # ----------------------------------------------------
        # IMPORTANT NOTE
        # ----------------------------------------------------

        st.info(
            "This prediction is generated by the existing V2 "
            "machine-learning pipeline. It is an estimate for "
            "decision support and should be interpreted together "
            "with project-specific engineering and management "
            "information."
        )

    

    st.title("New Project Prediction")

    st.write(
        "Enter project parameters to generate a V2 "
        "cost, schedule and explainable risk prediction."
    )

    st.divider()

    # --------------------------------------------------------
    # PROJECT INFORMATION
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">PROJECT INFORMATION</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        original_cost = st.number_input(
            "Original Approved Cost (₹ Cr)",
            min_value=0.01,
            value=1000.0,
            step=10.0,
            format="%.2f"
        )

    with col2:

        project_category = st.selectbox(
            "Project Category",
            [
                "Substation_Grid_Equipment",
                "Transmission_System",
                "Transmission_Line",
                "Substation"
            ]
        )

    # --------------------------------------------------------
    # CURRENT STATUS
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">CURRENT PROJECT STATUS</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        cumulative_expenditure = st.number_input(
            "Cumulative Expenditure (₹ Cr)",
            min_value=0.0,
            value=600.0,
            step=10.0,
            format="%.2f"
        )

    with col2:

        physical_progress = st.number_input(
            "Physical Progress (%)",
            min_value=0.0,
            max_value=100.0,
            value=50.0,
            step=1.0,
            format="%.2f"
        )

    # --------------------------------------------------------
    # SCHEDULE
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">SCHEDULE INFORMATION</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        planned_duration = st.number_input(
            "Planned Duration (months)",
            min_value=1.0,
            value=36.0,
            step=1.0,
            format="%.1f"
        )

    with col2:

        elapsed_months = st.number_input(
            "Elapsed Duration (months)",
            min_value=0.0,
            value=20.0,
            step=1.0,
            format="%.1f"
        )

    # --------------------------------------------------------
    # TRAJECTORY
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">PROJECT TRAJECTORY</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        progress_velocity = st.number_input(
            "Progress Velocity (% / month)",
            value=2.0,
            step=0.1,
            format="%.2f"
        )

    with col2:

        expenditure_velocity = st.number_input(
            "Expenditure Velocity (₹ Cr / month)",
            value=20.0,
            step=1.0,
            format="%.2f"
        )

    st.divider()

    # --------------------------------------------------------
    # DERIVED FEATURES
    # --------------------------------------------------------

    expenditure_pct = (
        cumulative_expenditure
        / original_cost
        * 100.0
    )

    months_to_target = (
        planned_duration
        - elapsed_months
    )

    expenditure_progress_gap = (
        expenditure_pct
        - physical_progress
    )

    schedule_slippage = max(
        0.0,
        elapsed_months - planned_duration
    )

    # --------------------------------------------------------
    # INDICATORS
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">CALCULATED INDICATORS</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Expenditure",
            f"{expenditure_pct:.2f}%"
        )

    with c2:

        st.metric(
            "Physical Progress",
            f"{physical_progress:.1f}%"
        )

    with c3:

        st.metric(
            "Progress Gap",
            f"{expenditure_progress_gap:.2f}"
        )

    with c4:

        st.metric(
            "Schedule Slippage",
            f"{schedule_slippage:.1f} mo"
        )

    st.divider()

    # --------------------------------------------------------
    # RUN PREDICTION
    # --------------------------------------------------------

    if st.button(
        "Run V2 Prediction",
        type="primary",
        use_container_width=True
    ):

        project_data = {

            "original_cost_cr":
                float(original_cost),

            "cumulative_expenditure_cr":
                float(cumulative_expenditure),

            "physical_progress_pct":
                float(physical_progress),

            "planned_duration_months":
                float(planned_duration),

            "elapsed_months":
                float(elapsed_months),

            "project_category":
                str(project_category),

            "progress_velocity":
                float(progress_velocity),

            "expenditure_velocity":
                float(expenditure_velocity)
        }

        try:

            result = predict_new_project(
                project_data
            )

            prediction = result[
                "prediction"
            ]

            prepared_input = result[
                "input"
            ]

            st.success(
                "V2 prediction completed successfully."
            )

            # ------------------------------------------------
            # PREDICTION RESULTS
            # ------------------------------------------------

            render_markdown(
                '<div class="section-label">PREDICTION RESULT</div>',
                unsafe_allow_html=True
            )

            r1, r2, r3 = st.columns(3)

            with r1:

                st.metric(
                    "Predicted Final Cost Overrun",
                    f"{prediction['cost_prediction_pct']:.2f}%"
                )

            with r2:

                st.metric(
                    "Predicted Final Schedule Delay",
                    f"{prediction['schedule_prediction_months']:.2f} months"
                )

            with r3:

                st.metric(
                    "Explainable Risk Score",
                    str(
                        prediction[
                            "cost_risk_score"
                        ]
                    )
                )

            # ------------------------------------------------
            # RISK LEVEL
            # ------------------------------------------------

            risk_level = prediction[
                "cost_risk_level"
            ]

            if risk_level == "HIGH":

                st.error(
                    f"Risk Level: {risk_level}"
                )

            elif risk_level == "MEDIUM":

                st.warning(
                    f"Risk Level: {risk_level}"
                )

            else:

                st.success(
                    f"Risk Level: {risk_level}"
                )

            # ------------------------------------------------
            # RISK REASONS
            # ------------------------------------------------

            render_markdown(
                '<div class="section-label">RISK EXPLANATION</div>',
                unsafe_allow_html=True
            )

            for reason in prediction[
                "cost_risk_reasons"
            ]:

                st.warning(
                    reason
                )

            for warning in prediction[
                "cost_risk_warnings"
            ]:

                st.info(
                    warning
                )

            # ------------------------------------------------
            # SUPPORTING INDICATORS
            # ------------------------------------------------

            render_markdown(
                '<div class="section-label">SUPPORTING INDICATORS</div>',
                unsafe_allow_html=True
            )

            s1, s2, s3, s4 = st.columns(4)

            with s1:

                st.metric(
                    "Expenditure %",
                    f"{prediction['expenditure_pct']:.2f}%"
                )

            with s2:

                st.metric(
                    "Physical Progress",
                    f"{prediction['physical_progress_pct']:.2f}%"
                )

            with s3:

                st.metric(
                    "Expenditure / Progress Gap",
                    f"{prediction['expenditure_progress_gap']:.2f}"
                )

            with s4:

                st.metric(
                    "Schedule Pressure",
                    f"{prediction['schedule_pressure_ratio']:.2f}x"
                )

            # ------------------------------------------------
            # MODEL INPUT
            # ------------------------------------------------

            with st.expander(
                "Show V2 Model Input"
            ):

                model_table = pd.DataFrame(
                    {
                        "Feature":
                            list(
                                prepared_input.keys()
                            ),

                        "Value":
                            list(
                                prepared_input.values()
                            )
                    }
                )

                st.dataframe(
                    model_table,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:

            st.error(
                "Prediction failed."
            )

            st.exception(e)


elif page == "Project Intelligence":

    render_markdown(
        '<div class="section-label">PROJECT ANALYSIS</div>',
        unsafe_allow_html=True
    )

    st.title(
        "Project Intelligence"
    )

    st.write(
        "Select any validated POWERGRID project to view "
        "its V2 prediction, risk assessment and project health."
    )


    # --------------------------------------------------------
    # PROJECT SELECTOR
    # --------------------------------------------------------

    selected_project = st.selectbox(

        "Select Project",

        project_codes,

        key="project_intelligence_selector"
    )


    analysis = load_analysis(
        selected_project
    )

    snapshot = analysis[
        "snapshot"
    ]

    prediction = analysis[
        "prediction"
    ]


    # --------------------------------------------------------
    # PROJECT IDENTITY
    # --------------------------------------------------------

    render_markdown(
        f"""
        <div class="project-header">

            <div class="project-code">
                PROJECT {selected_project}
            </div>

            <div class="project-name">
                {snapshot["project_name"]}
            </div>

            <div class="project-category">
                {snapshot["project_category"]}
                &nbsp;&nbsp;•&nbsp;&nbsp;
                Latest snapshot:
                {snapshot["snapshot_date"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")


    # --------------------------------------------------------
    # HEALTH HEADER
    # --------------------------------------------------------

    risk_level = prediction[
        "cost_risk_level"
    ]

    risk_score = prediction[
        "cost_risk_score"
    ]


    if risk_level == "HIGH":

        panel_class = "risk-panel-high"
        score_color = "#c92a38"

    elif risk_level == "MEDIUM":

        panel_class = "risk-panel-medium"
        score_color = "#a66b00"

    else:

        panel_class = "risk-panel-low"
        score_color = "#16834a"


    r1, r2, r3 = st.columns(
        [1, 1, 1],
        gap="medium"
    )


    with r1:

        render_markdown(
            f"""
            <div class="risk-panel {panel_class}">

                <div class="risk-panel-label">
                    Explainable Risk
                </div>

                <div class="risk-panel-score"
                     style="color:{score_color};">
                    {risk_score}
                </div>

                <div class="risk-panel-level"
                     style="color:{score_color};">
                    {risk_level}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with r2:

        render_markdown(
            f"""
            <div class="dashboard-card">

                <div class="metric-label">
                    Predicted Final Cost Overrun
                </div>

                <div class="metric-value">
                    {prediction["cost_prediction_pct"]:.2f}%
                </div>

                <div class="metric-description">
                    V2 Random Forest prediction
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with r3:

        render_markdown(
            f"""
            <div class="dashboard-card">

                <div class="metric-label">
                    Predicted Final Schedule Delay
                </div>

                <div class="metric-value">
                    {prediction["schedule_prediction_months"]:.2f}
                </div>

                <div class="metric-description">
                    Months predicted by V2 Extra Trees
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    st.write("")


    # --------------------------------------------------------
    # BUDGET + PROGRESS
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">Project Health</div>',
        unsafe_allow_html=True
    )

    h1, h2 = st.columns(
        2,
        gap="large"
    )


    with h1:

        expenditure = float(
            snapshot[
                "cumulative_expenditure_cr"
            ]
        )

        original_cost = float(
            snapshot[
                "original_cost_cr"
            ]
        )

        expenditure_pct = float(
            prediction[
                "expenditure_pct"
            ]
        )

        render_markdown(
            f"""
            <div class="dashboard-card">

                <div class="metric-label">
                    Budget Consumption
                </div>

                <div style="
                    font-size:1.65rem;
                    font-weight:850;
                    color:#102a43;
                    margin-top:8px;
                ">
                    ₹{expenditure:,.2f} Cr
                </div>

                <div style="
                    color:#627d98;
                    margin-top:4px;
                    font-size:0.82rem;
                ">
                    Approved: ₹{original_cost:,.2f} Cr
                </div>

                <div style="
                    margin-top:15px;
                    height:11px;
                    background:#e9eef3;
                    border-radius:20px;
                    overflow:hidden;
                ">

                    <div style="
                        width:{min(expenditure_pct, 120) / 1.2}%;
                        height:100%;
                        background:#1683ff;
                        border-radius:20px;
                    "></div>

                </div>

                <div style="
                    margin-top:8px;
                    font-size:0.8rem;
                    color:#627d98;
                ">
                    {expenditure_pct:.2f}% of approved cost
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with h2:

        progress = float(
            prediction[
                "physical_progress_pct"
            ]
        )

        gap = float(
            prediction[
                "expenditure_progress_gap"
            ]
        )

        render_markdown(
            f"""
            <div class="dashboard-card">

                <div class="metric-label">
                    Physical Progress
                </div>

                <div style="
                    font-size:1.65rem;
                    font-weight:850;
                    color:#102a43;
                    margin-top:8px;
                ">
                    {progress:.1f}%
                </div>

                <div style="
                    margin-top:15px;
                    height:11px;
                    background:#e9eef3;
                    border-radius:20px;
                    overflow:hidden;
                ">

                    <div style="
                        width:{min(progress, 100)}%;
                        height:100%;
                        background:#25a36f;
                        border-radius:20px;
                    "></div>

                </div>

                <div style="
                    margin-top:10px;
                    color:#627d98;
                    font-size:0.8rem;
                ">
                    Expenditure-progress gap:
                    <b>{gap:.2f}%</b>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    st.write("")


    # --------------------------------------------------------
    # RISK REASONS
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">Why Is This Project At Risk?</div>',
        unsafe_allow_html=True
    )

    reasons = prediction[
        "cost_risk_reasons"
    ]

    warnings = prediction[
        "cost_risk_warnings"
    ]

    if reasons:

        for reason in reasons:

            render_markdown(
                f"""
                <div class="reason-card">

                    <div class="reason-title">
                        ⚠ Risk Indicator
                    </div>

                    <div class="reason-text">
                        {reason}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    if warnings:

        for warning in warnings:

            render_markdown(
                f"""
                <div class="reason-card"
                     style="border-left-color:#1683ff;">

                    <div class="reason-title">
                        ℹ Early Warning
                    </div>

                    <div class="reason-text">
                        {warning}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    # --------------------------------------------------------
    # SUPPORTING INDICATORS
    # --------------------------------------------------------

    st.write("")

    render_markdown(
        '<div class="section-label">Supporting Indicators</div>',
        unsafe_allow_html=True
    )

    i1, i2, i3, i4 = st.columns(
        4
    )

    indicators = [

        (
            i1,
            "Expenditure",
            f'{prediction["expenditure_pct"]:.2f}%'
        ),

        (
            i2,
            "Progress",
            f'{prediction["physical_progress_pct"]:.1f}%'
        ),

        (
            i3,
            "Schedule Slippage",
            f'{prediction["schedule_slippage_months"]:.1f} mo'
        ),

        (
            i4,
            "Schedule Pressure",
            f'{prediction["schedule_pressure_ratio"]:.2f}×'
        )
    ]


    for column, label, value in indicators:

        with column:

            render_markdown(
                f"""
                <div class="dashboard-card">

                    <div class="metric-label">
                        {label}
                    </div>

                    <div class="metric-value"
                         style="font-size:1.45rem;">
                        {value}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# ============================================================
# TRAJECTORY
# ============================================================
# ============================================================

elif page == "Trajectory":

    render_markdown(
        '<div class="section-label">PROJECT EVOLUTION</div>',
        unsafe_allow_html=True
    )

    st.title(
        "Project Trajectory"
    )

    st.write(
        "Explore the historical evolution of physical progress "
        "and expenditure for a real POWERGRID project."
    )


    selected_project = st.selectbox(

        "Select Project",

        project_codes,

        key="trajectory_project"
    )


    analysis = load_analysis(
        selected_project
    )

    snapshot = analysis[
        "snapshot"
    ]

    prediction = analysis[
        "prediction"
    ]


    # --------------------------------------------------------
    # LOAD HISTORICAL SNAPSHOTS
    # --------------------------------------------------------

    from src.project_service import (
        get_project_snapshots
    )

    history = get_project_snapshots(
        selected_project
    ).copy()


    history = history.sort_values(
        "snapshot_date"
    )


    # --------------------------------------------------------
    # TRAJECTORY CHART
    # --------------------------------------------------------

    chart = go.Figure()


    chart.add_trace(
        go.Scatter(

            x=history[
                "snapshot_date"
            ],

            y=history[
                "physical_progress_pct"
            ],

            mode="lines+markers",

            name="Physical Progress %",

            line=dict(
                width=3
            ),

            marker=dict(
                size=7
            )
        )
    )


    chart.add_trace(
        go.Scatter(

            x=history[
                "snapshot_date"
            ],

            y=history[
                "expenditure_pct_of_original_cost"
            ],

            mode="lines+markers",

            name="Expenditure %",

            line=dict(
                width=3
            ),

            marker=dict(
                size=7
            )
        )
    )


    chart.update_layout(

        height=500,

        hovermode="x unified",

        xaxis_title="Snapshot Date",

        yaxis_title="Percentage",

        plot_bgcolor="white",

        paper_bgcolor="white",

        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
    )


    st.plotly_chart(
        chart,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TRAJECTORY FEATURES
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">Trajectory Indicators</div>',
        unsafe_allow_html=True
    )


    model_input = analysis[
        "model_input"
    ]


    t1, t2, t3, t4 = st.columns(
        4
    )


    trajectory_values = [

        (
            t1,
            "Progress Velocity",
            model_input[
                "progress_velocity"
            ]
        ),

        (
            t2,
            "Expenditure Velocity",
            model_input[
                "expenditure_velocity"
            ]
        ),

        (
            t3,
            "Budget Consumption",
            model_input[
                "expenditure_pct_of_original_cost"
            ]
            / 100
        ),

        (
            t4,
            "Schedule Pressure",
            prediction[
                "schedule_pressure_ratio"
            ]
        )
    ]


    for column, label, value in trajectory_values:

        with column:

            st.metric(
                label,
                f"{float(value):.2f}"
            )


    st.info(
        "Trajectory features are derived from the observed "
        "POWERGRID project history. They are not synthetic future data."
    )


# ============================================================
# ============================================================
# SCENARIO LAB
# ============================================================
# ============================================================

elif page == "Scenario Lab":

    render_markdown(
        '<div class="section-label">DECISION SUPPORT</div>',
        unsafe_allow_html=True
    )

    st.title(
        "Scenario Lab"
    )

    st.write(
        "Explore how changes in project conditions affect "
        "predicted cost, schedule and risk."
    )


    selected_project = st.selectbox(

        "Select Project",

        project_codes,

        key="scenario_project"
    )


    analysis = load_analysis(
        selected_project
    )

    snapshot = analysis[
        "snapshot"
    ]

    model_input = analysis[
        "model_input"
    ]


    baseline_expenditure = float(
        snapshot[
            "cumulative_expenditure_cr"
        ]
    )

    baseline_progress = float(
        snapshot[
            "physical_progress_pct"
        ]
    )

    baseline_elapsed = float(
        snapshot[
            "elapsed_months"
        ]
    )


    st.write("")


    # --------------------------------------------------------
    # SCENARIO CONTROLS
    # --------------------------------------------------------

    left, right = st.columns(
        [1, 1.35],
        gap="large"
    )


    with left:

        render_markdown(
            '<div class="section-label">Scenario Controls</div>',
            unsafe_allow_html=True
        )


        new_expenditure = st.slider(

            "Cumulative Expenditure (₹ Crore)",

            min_value=0.0,

            max_value=max(
                baseline_expenditure * 1.5,
                100.0
            ),

            value=baseline_expenditure,

            step=10.0
        )


        new_progress = st.slider(

            "Physical Progress (%)",

            min_value=0.0,

            max_value=100.0,

            value=baseline_progress,

            step=1.0
        )


        additional_delay = st.slider(

            "Additional Delay (months)",

            min_value=0,

            max_value=60,

            value=0,

            step=1
        )


        st.write("")


        run = st.button(
            "▶ RUN SCENARIO",
            use_container_width=True
        )


    with right:

        render_markdown(
            '<div class="section-label">Scenario Impact</div>',
            unsafe_allow_html=True
        )


        changes = {

            "cumulative_expenditure_cr":
                new_expenditure,

            "physical_progress_pct":
                new_progress,

            "elapsed_months":
                baseline_elapsed
                + additional_delay
        }


        scenario_result = analyze_what_if(

            selected_project,

            changes
        )


        baseline = scenario_result[
            "baseline"
        ]["prediction"]

        scenario = scenario_result[
            "scenario"
        ]["prediction"]


        comparison = pd.DataFrame({

            "Metric":
                [
                    "Cost Prediction",
                    "Schedule Prediction",
                    "Risk Score",
                    "Risk Level"
                ],

            "Baseline":
                [
                    f'{baseline["cost_prediction_pct"]:.2f}%',
                    f'{baseline["schedule_prediction_months"]:.2f} mo',
                    str(
                        baseline[
                            "cost_risk_score"
                        ]
                    ),
                    baseline[
                        "cost_risk_level"
                    ]
                ],

            "Scenario":
                [
                    f'{scenario["cost_prediction_pct"]:.2f}%',
                    f'{scenario["schedule_prediction_months"]:.2f} mo',
                    str(
                        scenario[
                            "cost_risk_score"
                        ]
                    ),
                    scenario[
                        "cost_risk_level"
                    ]
                ]
        })


        st.dataframe(

            comparison,

            use_container_width=True,

            hide_index=True
        )


        # ----------------------------------------------------
        # SCENARIO MESSAGE
        # ----------------------------------------------------

        if scenario[
            "cost_risk_level"
        ] == "HIGH":

            st.error(
                "Scenario remains HIGH RISK."
            )

        elif scenario[
            "cost_risk_level"
        ] == "MEDIUM":

            st.warning(
                "Scenario is classified as MEDIUM RISK."
            )

        else:

            st.success(
                "Scenario is currently LOW RISK."
            )


        cost_change = (
            scenario[
                "cost_prediction_pct"
            ]
            -
            baseline[
                "cost_prediction_pct"
            ]
        )


        delay_change = (
            scenario[
                "schedule_prediction_months"
            ]
            -
            baseline[
                "schedule_prediction_months"
            ]
        )


        render_markdown(
            f"""
            <div class="info-strip">

            Scenario impact:
            cost prediction changed by
            <b>{cost_change:+.2f}%</b>,
            while schedule prediction changed by
            <b>{delay_change:+.2f} months</b>.

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# ============================================================
# COMPARE PROJECTS
# ============================================================
# ============================================================

elif page == "Compare Projects":

    render_markdown(
        '<div class="section-label">PORTFOLIO COMPARISON</div>',
        unsafe_allow_html=True
    )

    st.title(
        "Compare Projects"
    )

    st.write(
        "Compare multiple real POWERGRID projects using "
        "the same V2 prediction and risk indicators."
    )


    selected_projects = st.multiselect(

        "Select projects to compare",

        project_codes,

        default=project_codes[:3],

        max_selections=5
    )


    if selected_projects:

        comparison_rows = []


        for code in selected_projects:

            analysis = load_analysis(
                code
            )

            snapshot = analysis[
                "snapshot"
            ]

            prediction = analysis[
                "prediction"
            ]


            comparison_rows.append({

                "Project":
                    code,

                "Risk":
                    prediction[
                        "cost_risk_level"
                    ],

                "Risk Score":
                    prediction[
                        "cost_risk_score"
                    ],

                "Cost Prediction (%)":
                    prediction[
                        "cost_prediction_pct"
                    ],

                "Schedule Delay (months)":
                    prediction[
                        "schedule_prediction_months"
                    ],

                "Expenditure (%)":
                    prediction[
                        "expenditure_pct"
                    ],

                "Physical Progress (%)":
                    prediction[
                        "physical_progress_pct"
                    ],

                "Schedule Pressure":
                    prediction[
                        "schedule_pressure_ratio"
                    ]
            })


        comparison_df = pd.DataFrame(
            comparison_rows
        )


        st.dataframe(

            comparison_df,

            use_container_width=True,

            hide_index=True
        )


        st.write("")


        # ----------------------------------------------------
        # COMPARISON CHART
        # ----------------------------------------------------

        chart = go.Figure()


        chart.add_trace(

            go.Bar(

                x=comparison_df[
                    "Project"
                ],

                y=comparison_df[
                    "Cost Prediction (%)"
                ],

                name="Cost Prediction"
            )
        )


        chart.add_trace(

            go.Bar(

                x=comparison_df[
                    "Project"
                ],

                y=comparison_df[
                    "Schedule Delay (months)"
                ],

                name="Schedule Delay"
            )
        )


        chart.update_layout(

            height=420,

            barmode="group",

            plot_bgcolor="white",

            paper_bgcolor="white",

            xaxis_title="Project",

            yaxis_title="Value"
        )


        st.plotly_chart(

            chart,

            use_container_width=True
        )


    else:

        st.info(
            "Select at least one project."
        )


# ============================================================
# ============================================================
# MODEL & METHODOLOGY
# ============================================================
# ============================================================

elif page == "Model & Methodology":

    render_markdown(
        '<div class="section-label">SYSTEM TRANSPARENCY</div>',
        unsafe_allow_html=True
    )

    st.title(
        "Model & Methodology"
    )

    st.write(
        "Technical overview of the validated V2 prediction system."
    )


    # --------------------------------------------------------
    # MODEL CARDS
    # --------------------------------------------------------

    m1, m2 = st.columns(
        2,
        gap="large"
    )


    with m1:

        render_markdown(
            """
            <div class="dashboard-card">

                <div class="metric-label">
                    Cost Model
                </div>

                <div class="metric-value"
                     style="font-size:1.5rem;">
                    Random Forest
                </div>

                <div class="metric-description">
                    Predicts expected cost overrun percentage.
                </div>

                <hr>

                <b>Input:</b> 12 V2 features

            </div>
            """,
            unsafe_allow_html=True
        )


    with m2:

        render_markdown(
            """
            <div class="dashboard-card">

                <div class="metric-label">
                    Schedule Model
                </div>

                <div class="metric-value"
                     style="font-size:1.5rem;">
                    Extra Trees
                </div>

                <div class="metric-description">
                    Predicts expected schedule delay in months.
                </div>

                <hr>

                <b>Input:</b> 12 V2 features

            </div>
            """,
            unsafe_allow_html=True
        )


    st.write("")


    # --------------------------------------------------------
    # DATA VALIDATION
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">Data Validation</div>',
        unsafe_allow_html=True
    )


    validation = pd.DataFrame({

        "Validation":
            [
                "Validated projects",
                "Cost training projects",
                "Schedule training projects",
                "Unseen evaluation projects",
                "Project overlap",
                "Synthetic data",
                "PDF rows appended"
            ],

        "Status":
            [
                "92",
                "69",
                "68",
                "23",
                "0",
                "NO",
                "NO"
            ]
    })


    st.dataframe(

        validation,

        use_container_width=True,

        hide_index=True
    )


    st.write("")


    # --------------------------------------------------------
    # FEATURE GROUPS
    # --------------------------------------------------------

    render_markdown(
        '<div class="section-label">V2 Feature Groups</div>',
        unsafe_allow_html=True
    )


    feature_data = pd.DataFrame({

        "Group":
            [
                "Base Project",
                "Base Project",
                "Base Project",
                "Base Project",
                "Base Project",
                "Base Project",
                "Base Project",
                "Trajectory",
                "Trajectory",
                "Trajectory",
                "Trajectory",
                "Trajectory"
            ],

        "Feature":
            [
                "Original cost",
                "Cumulative expenditure",
                "Physical progress",
                "Planned duration",
                "Elapsed months",
                "Months to original target",
                "Expenditure % of original cost",
                "Progress velocity",
                "Expenditure velocity",
                "Expenditure-progress gap",
                "Schedule slippage",
                "Schedule pressure"
            ]
    })


    st.dataframe(

        feature_data,

        use_container_width=True,

        hide_index=True
    )


    st.info(
        "The system uses real POWERGRID project information. "
        "No synthetic project rows are used for training."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

render_markdown(
    """
    <div class="footer">

        POWERGRID Project Intelligence

        <br>

        AI-assisted cost prediction • schedule prediction •
        explainable project risk

    </div>
    """,
    unsafe_allow_html=True
)