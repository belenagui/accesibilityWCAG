import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from zephyr_client import ZephyrScaleClient

# Labels that mark a test case as "in scope for automation tracking"
# Test cases without any of these labels are purely manual → excluded from dashboard
AUTOMATION_STATUSES = {
    "ToAutomate": {"color": "rgba(61, 107, 158, 0.80)",  "border": "rgba(90, 142, 196, 1.0)",  "order": 1},
    "InProgress": {"color": "rgba(158, 122, 61, 0.80)",  "border": "rgba(196, 155, 80, 1.0)",  "order": 2},
    "Automated":  {"color": "rgba(61, 158, 114, 0.80)",  "border": "rgba(80, 196, 144, 1.0)",  "order": 3},
}

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


def get_automation_status(labels: list[str]) -> str | None:
    """Return the automation status label if present, else None (purely manual)."""
    for label in labels:
        if label in AUTOMATION_STATUSES:
            return label
    return None


def build_dataframe(test_cases: list[dict]) -> pd.DataFrame:
    rows = []
    for tc in test_cases:
        labels = _label_list(tc)
        status = get_automation_status(labels)
        if status is None:
            continue  # skip purely manual test cases
        folder = tc.get("folder") or {}
        rows.append({
            "Key": tc.get("key", ""),
            "Name": tc.get("name", ""),
            "Automation Status": status,
            "TC Status": _field_name(tc.get("status")),
            "Priority": _field_name(tc.get("priority")),
            "Folder": folder.get("name", "No folder"),
            "Folder ID": folder.get("id"),
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
    st.caption("Tracked labels:")
    for label, meta in AUTOMATION_STATUSES.items():
        st.markdown(
            f"<span style='color:{meta['color']}'>●</span> `{label}`",
            unsafe_allow_html=True,
        )


# ── Load & filter data ────────────────────────────────────────────────────────

with st.spinner("Loading test cases..."):
    try:
        raw = fetch_test_cases(selected_project)
    except Exception as e:
        st.error(f"Could not load test cases for project **{selected_project}**: {e}")
        st.info("This may be a permissions issue. Try selecting a different project.")
        st.stop()

df = build_dataframe(raw)

if selected_folder_id != "__all__":
    df = df[df["Folder ID"] == int(selected_folder_id)]

if df.empty:
    st.warning("No test cases with automation labels found. Make sure test cases have labels: ToAutomate, In Progress, or Automated.")
    st.stop()

STATUS_ORDER   = list(AUTOMATION_STATUSES.keys())
STATUS_COLORS  = {k: v["color"]  for k, v in AUTOMATION_STATUSES.items()}
STATUS_BORDERS = {k: v["border"] for k, v in AUTOMATION_STATUSES.items()}


# ── KPIs ──────────────────────────────────────────────────────────────────────

counts = df["Automation Status"].value_counts()
total       = len(df)
n_candidate = int(counts.get("ToAutomate",  0))
n_progress  = int(counts.get("InProgress",  0))
n_automated = int(counts.get("Automated",   0))
coverage_pct = (n_automated / total * 100) if total else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total in scope",  total)
col2.metric("🔵 To Automate",  n_candidate)
col3.metric("🟡 In Progress",  n_progress)
col4.metric("🟢 Automated",    n_automated)
col5.metric("✅ Coverage",     f"{coverage_pct:.1f}%")

st.divider()


# ── Charts ────────────────────────────────────────────────────────────────────

chart_col1, chart_col2 = st.columns([1, 2])

with chart_col1:
    st.subheader("Overall distribution")
    donut_labels = [s for s in STATUS_ORDER if counts.get(s, 0) > 0]
    donut_values = [counts.get(s, 0) for s in donut_labels]
    donut_colors  = [STATUS_COLORS[s]  for s in donut_labels]
    donut_borders = [STATUS_BORDERS[s] for s in donut_labels]

    donut = go.Figure(
        go.Pie(
            labels=donut_labels,
            values=donut_values,
            hole=0.55,
            sort=False,
            marker=dict(
                colors=donut_colors,
                line=dict(color=donut_borders, width=2),
            ),
            textfont=dict(size=13),
        )
    )
    donut.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", y=-0.15),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(donut, use_container_width=True)

with chart_col2:
    st.subheader("Breakdown by folder")

    by_folder = (
        df.groupby(["Folder", "Automation Status"])
        .size()
        .reset_index(name="Count")
    )
    by_folder["Automation Status"] = pd.Categorical(
        by_folder["Automation Status"], categories=STATUS_ORDER, ordered=True
    )
    by_folder = by_folder.sort_values(["Folder", "Automation Status"])

    bar = px.bar(
        by_folder,
        x="Folder",
        y="Count",
        color="Automation Status",
        color_discrete_map=STATUS_COLORS,
        barmode="stack",
        category_orders={"Automation Status": STATUS_ORDER},
    )
    # Apply crystal effect: lighter border per status
    for status in STATUS_ORDER:
        bar.update_traces(
            marker_line_color=STATUS_BORDERS[status],
            marker_line_width=1.5,
            selector=dict(name=status),
        )
    bar.update_layout(
        margin=dict(t=10, b=10),
        legend_title_text="",
        xaxis_title="",
        yaxis_title="Test Cases",
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(bar, use_container_width=True)

st.divider()


# ── Summary table by folder ───────────────────────────────────────────────────

st.subheader("Summary by folder")

pivot = (
    df.groupby(["Folder", "Automation Status"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
for col in STATUS_ORDER:
    if col not in pivot.columns:
        pivot[col] = 0

pivot["Total"]      = pivot[STATUS_ORDER].sum(axis=1)
pivot["Coverage %"] = (pivot["Automated"] / pivot["Total"] * 100).round(1).apply(lambda x: f"{x}%")
pivot = pivot[["Folder"] + STATUS_ORDER + ["Total", "Coverage %"]]

st.dataframe(pivot, use_container_width=True, hide_index=True)

st.divider()


# ── Detail table ──────────────────────────────────────────────────────────────

st.subheader("Test case detail")

status_filter = st.radio(
    "Filter by status",
    ["All"] + STATUS_ORDER,
    horizontal=True,
)

display_df = df.copy()
if status_filter != "All":
    display_df = display_df[display_df["Automation Status"] == status_filter]

STATUS_ICONS = {"ToAutomate": "🔵", "InProgress": "🟡", "Automated": "🟢"}
display_df["Automation Status"] = display_df["Automation Status"].map(
    lambda s: f"{STATUS_ICONS.get(s, '')} {s}"
)

st.dataframe(
    display_df[["Key", "Name", "Automation Status", "Folder", "TC Status", "Priority"]],
    use_container_width=True,
    hide_index=True,
)
