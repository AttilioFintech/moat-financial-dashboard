from src.utils import pro_gate
import streamlit as st

def render():
    if not st.session_state.get("is_pro"):
        pro_gate("What-If Scenarios")
        return

    # ⬇️ SOLO QUI entra il vero engine
    st.slider("Income Change", -50, 100, 0)

