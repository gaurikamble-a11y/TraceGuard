
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

LOG_FILE = Path(__file__).with_name("traffic.jsonl")

st.set_page_config(
    page_title="TraceGuard | Security Operations",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== DESIGN ====================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #070B14;
    --panel: #111C2D;
    --border: rgba(111,148,190,.23);
    --cyan: #42E8F5;
    --muted: #B5C5D9;
    --white: #F2F6FF;
}

/* Main background */
.stApp {
    background:
        radial-gradient(ellipse at 75% 0%, rgba(58,91,170,.15), transparent 35%),
        radial-gradient(ellipse at 5% 45%, rgba(27,188,207,.07), transparent 35%),
        var(--bg);
    color: var(--white);
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1600px;
    padding: 2rem 3rem 4rem;
}

header[data-testid="stHeader"] {
    background: rgba(7,11,20,.85);
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--white) !important;
}

/* IMPORTANT: Do not apply fonts globally to span/div.
   Streamlit uses spans for its Material icons. */

.stApp p,
.stApp label,
.stApp li,
.stApp small {
    font-family: 'DM Sans', sans-serif;
    color: #D0DCEB;
}

.stApp [data-testid="stWidgetLabel"] p {
    color: #D0DCEB !important;
}

.stApp [data-testid="stCaptionContainer"] p {
    color: #B5C5D9 !important;
}

/* Preserve Streamlit icon fonts */
.stApp span.material-icons,
.stApp span.material-symbols-rounded,
.stApp span[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    font-weight: normal !important;
    font-style: normal !important;
    letter-spacing: normal !important;
    white-space: nowrap !important;
    direction: ltr !important;
    line-height: 1 !important;
    text-transform: none !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0D1524,#090F1B);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
}

[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 9px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255,255,255,.025);
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 11px 13px;
    transition: .2s;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(66,232,245,.08);
    border-color: rgba(66,232,245,.25);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(100deg,rgba(66,232,245,.16),rgba(100,139,255,.10));
    border-color: rgba(66,232,245,.35);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    color: #E8F0FC !important;
    font-weight: 600;
}

/* Brand */
.tg-logo {
    font-family: 'Space Grotesk',sans-serif;
    font-size: 29px;
    font-weight: 700;
    letter-spacing: -1.5px;
    color: #F2F6FF;
}

.tg-logo span {
    color: var(--cyan);
}

.tg-tagline {
    color: #B5C5D9;
    font-size: 10px;
    letter-spacing: 3px;
    margin-top: 5px;
    text-transform: uppercase;
}

/* Eyebrows */
.tg-eyebrow {
    color: var(--cyan);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* Hero */
.tg-hero {
    position: relative;
    overflow: hidden;
    padding: 34px 36px;
    border: 1px solid rgba(88,177,224,.24);
    border-radius: 20px;
    background:
        radial-gradient(circle at 90% 20%,rgba(94,119,255,.20),transparent 32%),
        linear-gradient(115deg,#14243A,#101827 70%);
    margin: 14px 0 25px;
    box-shadow: 0 15px 55px rgba(0,0,0,.18);
}

.tg-hero h1 {
    font-size: 31px;
    letter-spacing: -1px;
    margin: 10px 0 7px;
}

.tg-hero p {
    color: #C4D1E2 !important;
    font-size: 14px;
}

.tg-hero-icon {
    position: absolute;
    right: 50px;
    top: 23px;
    font-size: 90px;
    opacity: .15;
}

/* Metric cards */
.tg-card {
    position: relative;
    overflow: hidden;
    background: linear-gradient(145deg,#151F31,#101827);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 19px;
    min-height: 135px;
    box-shadow: 0 8px 25px rgba(0,0,0,.12);
    transition: transform .2s,border-color .2s;
}

.tg-card:hover {
    transform: translateY(-3px);
    border-color: rgba(66,232,245,.42);
}

.tg-card:after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 45%;
    height: 2px;
    background: linear-gradient(90deg,var(--cyan),transparent);
}

.tg-card-label {
    color: #B6C5D9;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.3px;
}

.tg-card-value {
    font-family: 'Space Grotesk',sans-serif;
    color: #F4F7FF;
    font-size: 34px;
    font-weight: 700;
    margin-top: 13px;
}

.tg-card-note {
    color: var(--cyan);
    font-size: 11px;
    margin-top: 5px;
}

/* Sections */
.tg-section {
    font-family: 'Space Grotesk',sans-serif;
    color: #EDF3FF;
    font-size: 20px;
    font-weight: 700;
    margin: 30px 0 4px;
}

.tg-muted {
    color: #B5C5D9;
    font-size: 12px;
    margin-bottom: 14px;
}

/* Severity cards */
.tg-severity {
    background: #111C2D;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 17px;
    min-height: 108px;
}

.tg-severity-number {
    font-family: 'Space Grotesk',sans-serif;
    font-size: 32px;
    font-weight: 700;
    margin-top: 8px;
}

.tg-severity-label {
    font-size: 10px;
    color: #B5C5D9;
    letter-spacing: 1.2px;
    font-weight: 700;
}

.tg-high { color: #FF7185; }
.tg-medium { color: #FFBD69; }
.tg-low { color: #65C9FF; }
.tg-critical { color: #D58BFF; }

/* Input controls */
.stApp input,
.stApp textarea {
    color: #F2F6FF !important;
    background-color: #152237 !important;
    border-color: #40536D !important;
}

.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #B5C5DA !important;
    opacity: 1 !important;
}

.stApp [data-baseweb="select"] > div {
    background-color: #152237 !important;
    border-color: #40536D !important;
}

.stApp [data-baseweb="select"] * {
    color: #E8F0FC !important;
}

/* Buttons */
.stButton button,
.stDownloadButton button {
    background: linear-gradient(110deg,#15364A,#1A3152);
    color: #75E8F2;
    border: 1px solid rgba(66,232,245,.35);
    border-radius: 9px;
    font-weight: 700;
    transition: .2s;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background: linear-gradient(110deg,#1B5367,#284577);
    color: white;
    border-color: var(--cyan);
}

/* Dataframes and metrics */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

div[data-testid="stMetric"] {
    background: #121D2D;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 13px;
}

div[data-testid="stMetricLabel"] {
    color: #B6C5D9 !important;
}

div[data-testid="stMetricValue"] {
    color: #F4F7FF !important;
}

/* EXPANDER FIX */
div[data-testid="stExpander"] {
    background: linear-gradient(145deg,#111C2D,#0D1725);
    border: 1px solid rgba(111,148,190,.23);
    border-radius: 12px;
    margin: 10px 0;
    overflow: hidden;
}

div[data-testid="stExpander"] summary {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    padding: 15px 18px !important;
    min-height: 58px;
    color: #E8F0FC !important;
}

div[data-testid="stExpander"] summary p {
    color: #E8F0FC !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    line-height: 1.5 !important;
    margin: 0 !important;
    overflow-wrap: anywhere;
}

div[data-testid="stExpander"] summary:hover {
    background: rgba(66,232,245,.06);
}

div[data-testid="stExpander"] details {
    border: none !important;
}

div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    padding: 12px 18px 18px !important;
    border-top: 1px solid var(--border);
}

div[data-testid="stExpander"] [data-testid="stExpanderDetails"] p {
    color: #C5D2E2 !important;
    line-height: 1.65;
}

/* Progress */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg,#42E8F5,#648BFF);
}

hr {
    border-color: var(--border);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)


# ==================== LOAD DATA ====================

def load_events():
    if not LOG_FILE.exists():
        return []

    records = []
    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    records.append(item)
            except json.JSONDecodeError:
                continue
    return records


events = load_events()
df = pd.DataFrame(events)
all_findings = []

if not df.empty:

    if "findings" not in df.columns:
        df["findings"] = [[] for _ in range(len(df))]

    df["findings"] = df["findings"].apply(
        lambda x: x if isinstance(x, list) else []
    )

    df["finding_count"] = df["findings"].apply(len)

    defaults = {
        "host": "Unknown",
        "method": "Unknown",
        "url": "",
        "status_code": None,
        "response_time_ms": None,
        "timestamp": "",
    }

    for key, value in defaults.items():
        if key not in df.columns:
            df[key] = value

    for event in events:
        for finding in event.get("findings", []):
            all_findings.append({
                "Host": event.get("host", "Unknown"),
                "URL": event.get("url", ""),
                "Rule ID": finding.get("rule_id", "Legacy"),
                "Rule": finding.get("rule", "Unspecified"),
                "Severity": str(finding.get("severity", "Info")).title(),
                "Evidence": finding.get("evidence", ""),
                "Recommendation": finding.get("recommendation", ""),
            })

findings_df = pd.DataFrame(all_findings)

if findings_df.empty:
    findings_df = pd.DataFrame(columns=[
        "Host", "URL", "Rule ID", "Rule", "Severity",
        "Evidence", "Recommendation"
    ])

total = len(df)
flagged = int((df["finding_count"] > 0).sum()) if total else 0
domains = int(df["host"].nunique()) if total else 0

avg_time = (
    pd.to_numeric(df["response_time_ms"], errors="coerce").mean()
    if total else None
)

weights = {"Critical": 30, "High": 20, "Medium": 10, "Low": 5}
unique_rules = {}

for item in all_findings:
    key = (item["Host"], item["Rule"])
    unique_rules[key] = max(
        unique_rules.get(key, 0),
        weights.get(item["Severity"], 0),
    )

score = max(0, 100 - sum(unique_rules.values()))


# ==================== HELPERS ====================

def section(title, subtitle=""):
    st.markdown(
        f'<div class="tg-section">{title}</div>'
        f'<div class="tg-muted">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def metric_card(label, value, note):
    st.markdown(
        f'<div class="tg-card">'
        f'<div class="tg-card-label">{label}</div>'
        f'<div class="tg-card-value">{value}</div>'
        f'<div class="tg-card-note">{note}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def severity_card(label, value, css_class):
    st.markdown(
        f'<div class="tg-severity">'
        f'<div class="tg-severity-label">{label.upper()} SEVERITY</div>'
        f'<div class="tg-severity-number {css_class}">{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def empty_state():
    st.markdown("""
    <div class="tg-hero">
        <div class="tg-eyebrow">SYSTEM STANDBY</div>
        <h1>Waiting for network activity</h1>
        <p>Start the proxy and send a request to begin monitoring traffic.</p>
    </div>
    """, unsafe_allow_html=True)


def chart_layout(fig, height=300):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#C2D0E1"),
        margin=dict(l=10, r=10, t=20, b=10),
        height=height,
    )
    return fig


# ==================== SIDEBAR ====================

with st.sidebar:

    st.markdown(
        '<div class="tg-logo">🛡️ Trace<span>Guard</span></div>'
        '<div class="tg-tagline">Network security intelligence</div>',
        unsafe_allow_html=True,
    )

    st.write("")
    st.divider()

    st.markdown(
        '<div class="tg-eyebrow">COMMAND CENTRE</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        ["Overview", "Traffic Monitor", "Security Findings", "Reports"],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown(
        '<div class="tg-eyebrow">SYSTEM STATUS</div>',
        unsafe_allow_html=True,
    )

    if events:
        st.markdown(
            '<div class="tg-status"><span class="tg-dot"></span> SYSTEM ACTIVE</div>',
            unsafe_allow_html=True,
        )
    else:
        st.caption("Waiting for captured traffic")

    st.write("")
    st.caption("LOCAL ANALYSIS ENVIRONMENT")
    st.caption("TraceGuard · MWS Project")
    st.caption("Version 1.0")


# ==================== OVERVIEW ====================

if page == "Overview":

    st.markdown("""
    <div class="tg-eyebrow">SECURITY OPERATIONS / OVERVIEW</div>
    <div class="tg-hero">
        <div class="tg-hero-icon">◈</div>
        <div class="tg-eyebrow">NETWORK INTELLIGENCE PLATFORM</div>
        <h1>See your traffic. Understand your risks.</h1>
        <p>Monitor network activity, detect security weaknesses and inspect traffic through one unified console.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↻ Refresh live data"):
        st.rerun()

    if not events:
        empty_state()

    else:
        cards = st.columns(4)

        with cards[0]:
            metric_card("REQUESTS CAPTURED", total, "Total recorded responses")

        with cards[1]:
            metric_card("FLAGGED REQUESTS", flagged, "Requests with findings")

        with cards[2]:
            metric_card("DOMAINS OBSERVED", domains, "Unique hostnames")

        with cards[3]:
            metric_card(
                "AVG RESPONSE TIME",
                f"{avg_time:.1f} ms" if pd.notna(avg_time) else "N/A",
                "Average response latency",
            )

        section(
            "Security intelligence",
            "A breakdown of security indicators identified by TraceGuard"
        )

        counts = (
            findings_df["Severity"].value_counts()
            if not findings_df.empty else {}
        )

        severity_columns = st.columns(4)

        severity_items = [
            ("High", "high"),
            ("Medium", "medium"),
            ("Low", "low"),
            ("Critical", "critical"),
        ]

        for col, (name, css) in zip(severity_columns, severity_items):
            with col:
                severity_card(name, int(counts.get(name, 0)), css)

        left, right = st.columns([1.15, 1])

        with left:
            section("Threat distribution", "Findings grouped by severity")

            if not findings_df.empty:

                chart_data = (
                    findings_df["Severity"]
                    .value_counts()
                    .rename_axis("Severity")
                    .reset_index(name="Findings")
                )

                fig = px.bar(
                    chart_data,
                    x="Severity",
                    y="Findings",
                    color="Severity",
                    color_discrete_map={
                        "Critical": "#C084FC",
                        "High": "#FF7185",
                        "Medium": "#FFBD69",
                        "Low": "#65C9FF",
                        "Info": "#94A3B8",
                    },
                    text="Findings",
                )

                fig.update_traces(
                    marker_line_width=0,
                    textposition="outside",
                )
                fig.update_layout(showlegend=False)

                st.plotly_chart(
                    chart_layout(fig),
                    use_container_width=True,
                )
            else:
                st.info("No security findings available.")

        with right:
            section("Security posture", "Illustrative rule-based score")

            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                number={
                    "suffix": "/100",
                    "font": {"size": 42, "color": "#F2F6FF"},
                },
                title={
                    "text": "CONFIGURATION SCORE",
                    "font": {"size": 12, "color": "#C0CDDE"},
                },
                gauge={
                    "axis": {
                        "range": [0, 100],
                        "tickcolor": "#AFC0D5",
                    },
                    "bar": {"color": "#42E8F5"},
                    "bgcolor": "#172438",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 40], "color": "#492536"},
                        {"range": [40, 70], "color": "#514126"},
                        {"range": [70, 100], "color": "#17444A"},
                    ],
                },
            ))

            gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font={"color": "#F2F6FF"},
                height=260,
                margin=dict(l=20, r=20, t=35, b=5),
            )

            st.plotly_chart(gauge, use_container_width=True)

            st.caption(
                "Illustrative score based on distinct host/rule pairs. "
                "It is not a security certification."
            )

        left, right = st.columns(2)

        with left:
            section("HTTP response analytics", "Captured response status codes")

            status = (
                df["status_code"].fillna("Unknown").astype(str)
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Requests")
            )

            fig = px.pie(
                status,
                names="Status",
                values="Requests",
                hole=.65,
                color_discrete_sequence=["#42E8F5", "#648BFF", "#A78BFA"],
            )

            st.plotly_chart(
                chart_layout(fig, 280),
                use_container_width=True,
            )

        with right:
            section("Recent network activity", "Latest captured requests")

            preview = df.tail(5).iloc[::-1]

            columns = [
                c for c in [
                    "host", "method", "status_code",
                    "response_time_ms", "finding_count"
                ] if c in preview.columns
            ]

            st.dataframe(
                preview[columns],
                use_container_width=True,
                hide_index=True,
            )


# ==================== TRAFFIC MONITOR ====================

elif page == "Traffic Monitor":

    st.markdown(
        '<div class="tg-eyebrow">INSPECTION / NETWORK ACTIVITY</div>',
        unsafe_allow_html=True,
    )

    st.title("Traffic Monitor")
    st.caption("Inspect recorded HTTP requests and response metadata.")

    if not events:
        empty_state()

    else:
        section("Traffic filters", "Narrow down captured network activity")

        c1, c2 = st.columns(2)

        hosts = sorted(df["host"].dropna().unique().tolist())
        methods = sorted(df["method"].dropna().unique().tolist())

        selected_hosts = c1.multiselect("Filter by host", hosts)
        selected_methods = c2.multiselect("Filter by method", methods)

        filtered = df.copy()

        if selected_hosts:
            filtered = filtered[filtered["host"].isin(selected_hosts)]

        if selected_methods:
            filtered = filtered[filtered["method"].isin(selected_methods)]

        a, b, c = st.columns(3)

        a.metric("Displayed requests", len(filtered))
        b.metric(
            "Flagged requests",
            int((filtered["finding_count"] > 0).sum()),
        )
        c.metric("Unique hosts", filtered["host"].nunique())

        section("Captured requests", "Recorded network responses")

        columns = [
            c for c in [
                "timestamp", "host", "method", "url",
                "status_code", "response_time_ms", "finding_count"
            ] if c in filtered.columns
        ]

        st.dataframe(
            filtered[columns],
            use_container_width=True,
            hide_index=True,
        )

        st.caption(f"Showing {len(filtered)} of {total} captured responses.")


# ==================== SECURITY FINDINGS ====================

elif page == "Security Findings":

    st.markdown(
        '<div class="tg-eyebrow">DETECTION / SECURITY INTELLIGENCE</div>',
        unsafe_allow_html=True,
    )

    st.title("Security Findings")
    st.caption(
        "Detected security indicators, supporting evidence and recommendations."
    )

    if findings_df.empty:
        st.success("No configured security rules have triggered.")

    else:
        c1, c2 = st.columns(2)

        available = [
            x for x in ["Critical", "High", "Medium", "Low", "Info"]
            if x in findings_df["Severity"].unique()
        ]

        severity_filter = c1.multiselect(
            "Severity",
            available,
            default=available,
        )

        hosts = sorted(findings_df["Host"].dropna().unique().tolist())
        host_filter = c2.multiselect("Host", hosts)

        visible = findings_df[
            findings_df["Severity"].isin(severity_filter)
        ]

        if host_filter:
            visible = visible[visible["Host"].isin(host_filter)]

        a, b, c, d = st.columns(4)

        a.metric("Total visible", len(visible))

        severity_totals = visible["Severity"].value_counts()

        b.metric("High", int(severity_totals.get("High", 0)))
        c.metric("Medium", int(severity_totals.get("Medium", 0)))
        d.metric("Low", int(severity_totals.get("Low", 0)))

        section(
            "Detected issues",
            "Expand a finding to inspect its evidence and recommendation",
        )

        for _, finding in visible.iterrows():

            title = (
                f"{finding['Severity']}  |  "
                f"{finding['Rule']}  |  {finding['Host']}"
            )

            with st.expander(title, expanded=False):

                st.write("**Rule ID:**", finding["Rule ID"])
                st.write("**URL:**", finding["URL"])

                st.markdown("**Evidence**")
                st.write(finding["Evidence"])

                st.markdown("**Recommendation**")
                st.write(finding["Recommendation"])

        st.caption(
            "A missing security header or cookie attribute is an indicator "
            "for review, not proof of an exploitable vulnerability."
        )


# ==================== REPORTS ====================

elif page == "Reports":

    st.markdown(
        '<div class="tg-eyebrow">OUTPUT / SECURITY REPORTING</div>',
        unsafe_allow_html=True,
    )

    st.title("Reports")
    st.caption("Export captured traffic and security analysis results.")

    if df.empty:
        empty_state()

    else:
        section(
            "Report overview",
            "Summary of recorded monitoring activity",
        )

        a, b, c = st.columns(3)

        a.metric("Captured requests", total)
        b.metric("Security findings", len(findings_df))
        c.metric("Flagged requests", flagged)

        st.markdown('<div class="tg-panel">', unsafe_allow_html=True)
        st.markdown("### Network traffic report")

        traffic_columns = [
            c for c in [
                "timestamp", "host", "method", "url",
                "status_code", "response_time_ms", "finding_count"
            ] if c in df.columns
        ]

        st.download_button(
            "⬇ Download traffic CSV",
            df[traffic_columns].to_csv(index=False).encode("utf-8"),
            "traceguard_traffic.csv",
            "text/csv",
            use_container_width=True,
        )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="tg-panel">', unsafe_allow_html=True)
        st.markdown("### Security findings report")

        st.download_button(
            "⬇ Download findings CSV",
            findings_df.to_csv(index=False).encode("utf-8"),
            "traceguard_findings.csv",
            "text/csv",
            use_container_width=True,
        )

        st.markdown('</div>', unsafe_allow_html=True)

        if not findings_df.empty:

            summary = (
                findings_df["Severity"]
                .value_counts()
                .rename_axis("Severity")
                .reset_index(name="Findings")
            )

            st.markdown('<div class="tg-panel">', unsafe_allow_html=True)
            st.markdown("### Severity summary")

            st.dataframe(
                summary,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "⬇ Download severity summary CSV",
                summary.to_csv(index=False).encode("utf-8"),
                "traceguard_severity_summary.csv",
                "text/csv",
                use_container_width=True,
            )

            st.markdown('</div>', unsafe_allow_html=True)

        st.caption(
            "Reports contain captured metadata and configured rule findings. "
            "They are not a complete security audit."
        )
