import streamlit as st

def render():
    st.title("🧠 Strategic Archetypes")
    
    st.markdown(
        """
        ### Your archetype is not a label.
        ### It's a strategic baseline.
        
        Moat uses archetypes to calibrate:
        - Alert thresholds
        - Scoring weights
        - Risk sensitivity
        
        ---
        """
    )
    
    # Mostra archetype corrente se esiste
    if st.session_state.get("onboarding_complete", False):
        archetype = st.session_state.get("archetype", {})
        
        st.markdown(f"### Your Current Archetype: **{archetype['name']}**")
        
        st.info(
            f"""
            {archetype['description']}
            
            **Baseline Moat Score:** {archetype['baseline_score']}  
            **Alert Sensitivity:** {archetype['alert_sensitivity'].title()}
            """
        )
        
        st.markdown("---")
    
    # ============================================
    # ARCHETYPE LIBRARY
    # ============================================
    
    st.markdown("### All Archetypes")
    
    archetypes = {
        "Stable Operator": {
            "profile": "W2 income, low volatility, long time horizon",
            "strengths": "Predictable cash flow, ability to plan long-term allocations",
            "vulnerabilities": "Single income source, limited upside optionality",
            "focus": "Building emergency reserves, then optimizing for growth"
        },
        "Variable Operator": {
            "profile": "Freelance/business income, high volatility, shorter horizon",
            "strengths": "High income ceiling, multiple revenue streams possible",
            "vulnerabilities": "Revenue unpredictability, expense management critical",
            "focus": "Maintaining 6+ months reserves, reducing fixed costs"
        },
        "Portfolio Operator": {
            "profile": "Mixed income sources, medium volatility",
            "strengths": "Diversification reduces single-point failure risk",
            "vulnerabilities": "Complexity in tracking, potential attention fragmentation",
            "focus": "Monitoring concentration risk, ensuring no single source dominates"
        },
        "Emerging Operator": {
            "profile": "Building position, variable conditions",
            "strengths": "Flexibility to adapt strategy as conditions change",
            "vulnerabilities": "Undefined baseline, unclear risk tolerances",
            "focus": "Establishing defense first, then pursuing optionality"
        }
    }
    
    for name, details in archetypes.items():
        with st.expander(f"**{name}**"):
            st.markdown(f"**Profile:** {details['profile']}")
            st.markdown(f"**Strengths:** {details['strengths']}")
            st.markdown(f"**Vulnerabilities:** {details['vulnerabilities']}")
            st.markdown(f"**Strategic Focus:** {details['focus']}")
    
    st.markdown("---")
    
    st.markdown(
        """
        ### Archetypes evolve.
        
        As your income structure or risk tolerance changes, so does your archetype.
        
        Moat adapts with you.
        """
    )
