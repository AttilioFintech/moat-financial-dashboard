import streamlit as st
from pages.dashboard import render as dashboard_page
from pages.trajectory import render as trajectory_page
from pages.whatif import render as whatif_page
from pages.vulnerabilities import render as vulnerabilities_page
from pages.archetypes import render as archetypes_page
from pages.about import render as about_page


# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Moat – Strategic Financial Resilience",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# SIDEBAR
# =============================
st.sidebar.title("🏰 MOAT")

st.sidebar.markdown(
    """
    **Strategic Financial Resilience Tool**

    Moat helps you decide **where to allocate**
    your time, energy, and capital —  
    not how much coffee to cut.
    """
)

PAGE_MAP = {
    "📊 Strategic Dashboard": "dashboard",
    "🔮 What-If Scenarios": "whatif",
    "📈 Trajectory": "trajectory",
    "🛡 Vulnerabilities": "vulnerabilities",
    "🧠 Archetypes": "archetypes",
    "ℹ️ About": "about"
}

page_label = st.sidebar.radio("Navigate", list(PAGE_MAP.keys()))
page = PAGE_MAP[page_label]

st.sidebar.divider()

st.sidebar.markdown(
    """
    🔒 **PRO ACCESS**
    
    Advanced simulations, projections  
    and strategic recommendations  
    are available via selective access.
    """
)

# =============================
# PAGE ROUTING
# =============================
if page == "dashboard":
    from pages.dashboard import render
    render()

elif page == "whatif":
    from pages.whatif import render
    render()

elif page == "trajectory":
    from pages.trajectory import render
    render()

elif page == "vulnerabilities":
    from pages.vulnerabilities import render
    render()

elif page == "archetypes":
    from pages.archetypes import render
    render()

elif page == "about":
    from pages.about import render
    render()

else:
    st.error("Page not found.")
