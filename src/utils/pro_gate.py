import streamlit as st

def pro_gate(feature_name: str, description: str = None):
    """
    Blocco elegante per feature PRO.
    Non è un paywall aggressivo — è un segnale di valore.
    """
    if not st.session_state.get("is_pro", False):
        st.markdown(
            f"""
            ### 🔒 {feature_name} — Strategic Access Required
            
            This capability allows you to **simulate decisions before making them**.
            
            {description if description else "Access is limited to PRO members."}
            """
        )
        
        st.info(
            "💡 **What you're missing**: Interactive tools that let you test financial strategies "
            "without real-world consequences."
        )
        
        st.stop()
