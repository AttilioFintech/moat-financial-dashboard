import streamlit as st
from src.dashboard import render as dashboard_page
from src.trajectory import render as trajectory_page
from src.whatif import render as whatif_page
from src.vulnerabilities import render as vulnerabilities_page
from src.archetypes import render as archetypes_page
from src.about import render as about_page

# -------------------------
# SESSION INIT
# -------------------------
if "is_pro" not in st.session_state:
    st.session_state.is_pro = False

st.set_page_config(
    page_title="Moat – Strategic Financial Resilience",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("🏰 MOAT")

st.sidebar.markdown(
    """
    **Strategic Financial Resilience**
    
    Moat helps you decide **where to allocate**
    time, energy, and capital.
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
# PRO STATUS
# -------------------------
st.sidebar.divider()

if st.session_state.is_pro:
    st.sidebar.success("🔓 **Strategic Access Enabled**")
else:
    st.sidebar.markdown("### 🔐 Strategic Access")
    
    st.sidebar.markdown(
        """
        Moat PRO is reserved for individuals who
        actively manage **capital, leverage, and risk**.
        
        Access is reviewed manually.
        """
    )
    
    if st.sidebar.button("Request Strategic Access", use_container_width=True):
        st.sidebar.success("✅ Request received. Priority queue assigned.")
        # TODO: Collect email + send to Airtable/Notion

# -------------------------
# RENDER PAGE
# -------------------------
PAGE_MAP[page_label]()


