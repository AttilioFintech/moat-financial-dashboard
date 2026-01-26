import streamlit as st
from src import dashboard, onboarding, archetypes, whatif, trajectory, vulnerabilities, stress_test, about

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Moat — Strategic Finance",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if "onboarding_complete" not in st.session_state:
    st.session_state["onboarding_complete"] = False

if "is_pro" not in st.session_state:
    st.session_state["is_pro"] = False

# ============================================
# SIDEBAR NAVIGATION
# ============================================

with st.sidebar:
    st.title("🏰 Moat")
    st.caption("Strategic Finance for Operators")
    
    st.markdown("---")
    
    # Se onboarding non completo, limita navigazione
    if not st.session_state.get("onboarding_complete", False):
        st.warning("Complete Strategic Setup to unlock full navigation")
        
        page = st.radio(
            "Navigate",
            ["Strategic Setup", "About"],
            label_visibility="collapsed"
        )
    else:
        page = st.radio(
            "Navigate",
            [
                "Dashboard",
                "Vulnerabilities",
                "What-If",
                "Trajectory",
                "Stress Test",
                "Archetypes",
                "About"
            ],
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    # PRO Status indicator
    if st.session_state.get("is_pro", False):
        st.success("✓ Strategic Access Active")
    else:
        st.info("📊 Free Tier")
    
    # Debug toggle (dev only)
    with st.expander("⚙️ Dev Controls"):
        if st.checkbox("Enable PRO (dev mode)"):
            st.session_state["is_pro"] = True
        
        if st.button("Reset Onboarding"):
            st.session_state["onboarding_complete"] = False
            st.session_state["archetype"] = None
            st.rerun()

# ============================================
# PAGE ROUTING
# ============================================

if page == "Strategic Setup":
    onboarding.render()
elif page == "Dashboard":
    dashboard.render()
elif page == "Vulnerabilities":
    vulnerabilities.render()
elif page == "What-If":
    whatif.render()
elif page == "Trajectory":
    trajectory.render()
elif page == "Stress Test":
    stress_test.render()
elif page == "Archetypes":
    archetypes.render()
elif page == "About":
    about.render()
