import streamlit as st
from src.dashboard import render as dashboard_page
from src.trajectory import render as trajectory_page
from src.whatif import render as whatif_page
from src.vulnerabilities import render as vulnerabilities_page
from src.archetypes import render as archetypes_page
from src.about import render as about_page

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

st.sidebar.divider()
st.sidebar.markdown("🔒 **PRO ACCESS**")

PAGE_MAP[page_label]()
