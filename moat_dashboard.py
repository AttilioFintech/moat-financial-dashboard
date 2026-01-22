import streamlit as st
from src.dashboard import render as dashboard_page
from src.trajectory import render as trajectory_page
from src.whatif import render as whatif_page
from src.vulnerabilities import render as vulnerabilities_page
from src.archetypes import render as archetypes_page
from src.about import render as about_page

# -------------------------
# SESSION INIT – PRO FLAG
# -------------------------
if "is_pro" not in st.session_state:
    st.session_state.is_pro = False   # default
    # In futuro → login / invite / whitelist
    # st.session_state.is_pro = check_user_pro_status()

def project_savings(current_savings, monthly_delta, months=12):
    projections = []
    value = current_savings

    for _ in range(months):
        value += monthly_delta
        projections.append(value)

    return projections

st.set_page_config(
    page_title="Moat – Strategic Financial Resilience",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("🏰 MOAT")

st.sidebar.markdown(
    """
    **Strategic Financial Resilience Tool**
    
    Moat helps you decide **where to allocate**
    your time, energy, and capital.
    """
)

PAGE_MAP = {
    "📊 Strategic Dashboard": dashboard_page,
    "🔮 What-If Scenarios": whatif_page,
    "📈 Trajectory": trajectory_page,
    "🛡 Vulnerabilities": vulnerabilities_page,
    "🧠 Archetypes": archetypes_page,
    "ℹ️ About": about_page
}

page_label = st.sidebar.radio("Navigate", list(PAGE_MAP.keys()))

# -------------------------
# PRO BADGE (semplice, elegante)
# -------------------------
st.sidebar.divider()
if st.session_state.is_pro:
    st.sidebar.success("🔓 PRO Enabled")
else:
    st.sidebar.info("🔒 PRO Locked")

PAGE_MAP[page_label]()
