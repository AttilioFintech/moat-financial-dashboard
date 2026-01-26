import streamlit as st

def pro_gate(feature_name: str, description: str = None):
    """
    Blocco per feature PRO.
    Non è un paywall — è un segnale di decision power.
    """
    if not st.session_state.get("is_pro", False):
        st.markdown(
            f"""
            ### 🔒 {feature_name}
            
            **This projection is locked.**
            
            {description if description else "Strategic access allows you to test decisions before committing resources."}
            """
        )
        
        st.info(
            """
            **What you're missing:**  
            The ability to see consequences before they happen.
            
            Most people react to financial changes.  
            Strategic operators **simulate** them first.
            """
        )
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(
                """
                **Strategic Access includes:**
                - What-If scenarios across income/expense shifts
                - 12-month trajectory modeling
                - Alternative path comparison
                """
            )
        
        with col2:
            if st.button("Request Access", type="primary"):
                st.session_state["access_requested"] = True
        
        if st.session_state.get("access_requested", False):
            st.success("Access request noted. This is not an automated upgrade.")
        
        st.stop()
