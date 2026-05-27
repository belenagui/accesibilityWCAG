import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from zephyr_client import ZephyrScaleClient

AUTOMATION_LABEL = "Automation Status"

st.set_page_config(
    page_title="Zephyr - Automation Coverage",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 Zephyr Scale — Automation Coverage Dashboard")


# ── Data fetching ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def fetch_projects() -> list[dict]:
    return ZephyrScaleClient().get_projects()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_folders(project_key: str) -> list[dict]:
    return ZephyrScaleClient().get_folders(project_key)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_test_cases(project_key: str) -> list[dict]:
    return ZephyrScaleClient().get_test_cases(project_key)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _label_list(tc: dict) -> list[str]:
    raw = tc.get("labels") or []
    if raw and isinstance(raw[0], dict):
        return [l.get("name", "") for l in raw]
    return [str(l) for l in raw]


def _field_name(field) -> str:
    if isinstance(field, dict):
        return field.get("name", "")
    return str(field) if field else ""


def build_dataframe(test_cases: list[dict]) -> pd.DataFrame:
    rows = []
    for tc in test_cases:
        labels = _label_list(tc)
        folder = tc.get("folder") or {}
        rows.append({
            "Key": tc.get("key", ""),
            "Name": tc.get("name", ""),
            "Status": _field_name(tc.get("status")),
            "Priority": _field_name(tc.get("priority")),
            "Folder": folder.get("name", "No folder"),
            "Folder ID": folder.get("id"),
            "Automated": AUTOMATION_LABEL in labels,
            "Labels": ", ".join(labels),
        })
    return pd.DataFrame(rows)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filters")

    if st.button("🔄 Refresh data"):
        st.cache_data.clear()
        st.rerun()

    try:
        with st.spinner("Loading projects..."):
            projects = fetch_projects()
    except Exception as e:
        st.error(f"Error connecting to Zephyr Scale: {e}")
        st.stop()

    if not projects:
        st.warning("No projects found.")
        st.stop()

    project_options = {p["key"]: f"{p['key']} — {p.get('name', '')}" for p in projects}
    selected_project = st.selectbox(
        "Project",
        options=list(project_options.keys()),
        format_func=lambda k: project_options[k],
    )

    with st.spinner("Loading folders..."):
        folders = fetch_folders(selected_project)

    folder_options = {"__all__": "All folders"}
    folder_options.update({str(f["id"]): f["name"] for f in folders})

    selected_folder_id = st.selectbox(
        "Folder",
        options=list(folder_options.keys()),
        format_func=lambda k: folder_options[k],
    )

    st.divider()
    st.caption(f"Automation label: `{AUTOMATION_LABEL}`")


# ── Load & filter data ────────────────────────────────────────────────────────

with st.spinner("Loading test cases..."):
    raw = fetch_test_cases(selected_project)

df = build_dataframe(raw)

if selected_folder_id != "__all__":
    df = df[df["Folder ID"] == int(selected_folder_id)]

if df.empty:
    st.warning("No test cases found for the selected filters.")
    st.stop()


# ── KPIs ──────────────────────────────────────────────────────────────────────

total = len(df)
automated = int(df["Automated"].sum())
manual = total - automated
coverage_pct = (automated / total * 100) if total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Test Cases", total)
col2.metric("Automated", automated)
col3.metric("Not Automated", manual)
col4.metric("Coverage", f"{coverage_pct:.1f}%")

st.divider()


# ── Charts ────────────────────────────────────────────────────────────────────

chart_col1, chart_col2 = st.columns([1, 2])

with chart_col1:
    st.subheader("Overall distribution")
    donut = go.Figure(
        go.Pie(
            labels=["Automated", "Not automated"],
            values=[automated, manual],
            hole=0.55,
            marker_colors=["#2ecc71", "#e74c3c"],
        )
    )
    donut.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", y=-0.1),
        height=300,
    )
    st.plotly_chart(donut, use_container_width=True)

with chart_col2:
    st.subheader("Coverage by folder")
    by_folder = (
        df.groupby("Folder")["Automated"]
        .agg(Automated="sum", Total="count")
        .reset_index()
    )
    by_folder["Not automated"] = by_folder["Total"] - by_folder["Automated"]
    by_folder["Coverage %"] = (by_folder["Automated"] / by_folder["Total"] * 100).round(1)
    by_folder = by_folder.sort_values("Total", ascending=False)

    bar = px.bar(
        by_folder,
        x="Folder",
        y=["Automated", "Not automated"],
        color_discrete_map={"Automated": "#2ecc71", "Not automated": "#e74c3c"},
        barmode="stack",
        custom_data=["Coverage %"],
    )
    bar.update_traces(hovertemplate="%{y} test cases<br>Coverage: %{customdata[0]}%")
    bar.update_layout(
        margin=dict(t=10, b=10),
        legend_title_text="",
        xaxis_title="",
        yaxis_title="Test Cases",
        height=300,
    )
    st.plotly_chart(bar, use_container_width=True)

st.divider()


# ── Summary table by folder ───────────────────────────────────────────────────

st.subheader("Summary by folder")
summary = by_folder[["Folder", "Total", "Automated", "Not automated", "Coverage %"]].copy()
summary["Coverage %"] = summary["Coverage %"].apply(lambda x: f"{x}%")
st.dataframe(summary, use_container_width=True, hide_index=True)

st.divider()


# ── Detail table ──────────────────────────────────────────────────────────────

st.subheader("Test case detail")

view_filter = st.radio(
    "Show",
    ["All", "Automated only", "Not automated only"],
    horizontal=True,
)

display_df = df.copy()
if view_filter == "Automated only":
    display_df = display_df[display_df["Automated"]]
elif view_filter == "Not automated only":
    display_df = display_df[~display_df["Automated"]]

display_df["Automated"] = display_df["Automated"].map({True: "✅", False: "❌"})
st.dataframe(
    display_df[["Key", "Name", "Automated", "Folder", "Status", "Priority", "Labels"]],
    use_container_width=True,
    hide_index=True,
)
