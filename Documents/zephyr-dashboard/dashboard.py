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


# ── Helpers ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def fetch_projects() -> list[dict]:
    return ZephyrScaleClient().get_projects()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_folders(project_key: str) -> list[dict]:
    return ZephyrScaleClient().get_folders(project_key)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_test_cases(project_key: str) -> list[dict]:
    return ZephyrScaleClient().get_test_cases(project_key)


def _label_list(tc: dict) -> list[str]:
    raw = tc.get("labels") or []
    if raw and isinstance(raw[0], dict):
        return [l.get("name", "") for l in raw]
    return [str(l) for l in raw]


def _name(field) -> str:
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
            "Nombre": tc.get("name", ""),
            "Estado": _name(tc.get("status")),
            "Prioridad": _name(tc.get("priority")),
            "Carpeta": folder.get("name", "Sin carpeta"),
            "Folder ID": folder.get("id"),
            "Automatizado": AUTOMATION_LABEL in labels,
            "Labels": ", ".join(labels),
        })
    return pd.DataFrame(rows)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filtros")

    if st.button("🔄 Refrescar datos"):
        st.cache_data.clear()
        st.rerun()

    try:
        with st.spinner("Cargando proyectos..."):
            projects = fetch_projects()
    except Exception as e:
        st.error(f"Error conectando a Zephyr Scale: {e}")
        st.stop()

    project_options = {p["key"]: f"{p['key']} — {p.get('name', '')}" for p in projects}
    if not project_options:
        st.warning("No se encontraron proyectos.")
        st.stop()

    selected_project = st.selectbox(
        "Proyecto",
        options=list(project_options.keys()),
        format_func=lambda k: project_options[k],
    )

    with st.spinner("Cargando carpetas..."):
        folders = fetch_folders(selected_project)

    folder_options = {"__all__": "Todas las carpetas"}
    folder_options.update({str(f["id"]): f["name"] for f in folders})

    selected_folder_id = st.selectbox(
        "Carpeta",
        options=list(folder_options.keys()),
        format_func=lambda k: folder_options[k],
    )

    st.divider()
    st.caption(f"Label de automatización: `{AUTOMATION_LABEL}`")


# ── Data load ─────────────────────────────────────────────────────────────────

with st.spinner("Cargando test cases..."):
    raw = fetch_test_cases(selected_project)

df = build_dataframe(raw)

if selected_folder_id != "__all__":
    df = df[df["Folder ID"] == int(selected_folder_id)]

if df.empty:
    st.warning("No se encontraron test cases con los filtros seleccionados.")
    st.stop()


# ── KPIs ──────────────────────────────────────────────────────────────────────

total = len(df)
automated = df["Automatizado"].sum()
manual = total - automated
pct = (automated / total * 100) if total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Test Cases", total)
col2.metric("Automatizados", int(automated))
col3.metric("No automatizados", int(manual))
col4.metric("Cobertura", f"{pct:.1f}%")

st.divider()


# ── Charts ────────────────────────────────────────────────────────────────────

chart_col1, chart_col2 = st.columns([1, 2])

with chart_col1:
    st.subheader("Distribución general")
    donut = go.Figure(
        go.Pie(
            labels=["Automatizados", "No automatizados"],
            values=[int(automated), int(manual)],
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
    st.subheader("Cobertura por carpeta")
    by_folder = (
        df.groupby("Carpeta")["Automatizado"]
        .agg(Automatizados="sum", Total="count")
        .reset_index()
    )
    by_folder["No automatizados"] = by_folder["Total"] - by_folder["Automatizados"]
    by_folder["Cobertura %"] = (by_folder["Automatizados"] / by_folder["Total"] * 100).round(1)
    by_folder = by_folder.sort_values("Total", ascending=False)

    bar = px.bar(
        by_folder,
        x="Carpeta",
        y=["Automatizados", "No automatizados"],
        color_discrete_map={"Automatizados": "#2ecc71", "No automatizados": "#e74c3c"},
        barmode="stack",
        custom_data=["Cobertura %"],
    )
    bar.update_traces(
        hovertemplate="%{y} test cases<br>Cobertura: %{customdata[0]}%"
    )
    bar.update_layout(
        margin=dict(t=10, b=10),
        legend_title_text="",
        xaxis_title="",
        yaxis_title="Test Cases",
        height=300,
    )
    st.plotly_chart(bar, use_container_width=True)

st.divider()


# ── Coverage table by folder ──────────────────────────────────────────────────

st.subheader("Resumen por carpeta")
summary = by_folder[["Carpeta", "Total", "Automatizados", "No automatizados", "Cobertura %"]].copy()
summary["Cobertura %"] = summary["Cobertura %"].apply(lambda x: f"{x}%")
st.dataframe(summary, use_container_width=True, hide_index=True)

st.divider()


# ── Detail table ──────────────────────────────────────────────────────────────

st.subheader("Detalle de test cases")

auto_filter = st.radio(
    "Mostrar",
    ["Todos", "Solo automatizados", "Solo no automatizados"],
    horizontal=True,
)

display_df = df.copy()
if auto_filter == "Solo automatizados":
    display_df = display_df[display_df["Automatizado"]]
elif auto_filter == "Solo no automatizados":
    display_df = display_df[~display_df["Automatizado"]]

display_df["Automatizado"] = display_df["Automatizado"].map({True: "✅", False: "❌"})
st.dataframe(
    display_df[["Key", "Nombre", "Automatizado", "Carpeta", "Estado", "Prioridad", "Labels"]],
    use_container_width=True,
    hide_index=True,
)
