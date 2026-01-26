import streamlit as st
from core.metrics import calculate_emergency_months
from core.scoring import calculate_moat_score

def render():
    # ============================================
    # ONBOARDING CHECK
    # ============================================
    
    if not st.session_state.get("onboarding_complete", False):
        st.warning(
            """
            **⚙️ Strategic Setup Required**
            
            Complete the 3-question setup to calibrate your Moat Score.
            
            Navigate to **Strategic Setup** in the sidebar.
            """
        )
        st.stop()
    
    # ============================================
    # STRATEGIC ALERT BLOCK (sempre visibile)
    # ============================================
    
    # Recupera archetype
    archetype = st.session_state.get("archetype", {})
    alert_sensitivity = archetype.get("alert_sensitivity", "medium")
    
    # Calcolo metriche preliminari
    emergency_months = calculate_emergency_months(12000, 2500)
    income_concentration = 60  # Da parametrizzare con dati reali
    
    score = calculate_moat_score({
        "emergency_months": emergency_months,
        "expense_growth": 8,
        "income_concentration": income_concentration
    })
    
    # 🔴 STRATEGIC RISK DETECTION
    # Logica: thresholds variano in base a alert_sensitivity
    
    if alert_sensitivity == "high":
        emergency_threshold = 6
        concentration_threshold = 60
        score_threshold = 75
    elif alert_sensitivity == "low":
        emergency_threshold = 4
        concentration_threshold = 75
        score_threshold = 65
    else:  # medium (default)
        emergency_threshold = 5
        concentration_threshold = 65
        score_threshold = 70
    
    show_alert = (
        emergency_months < emergency_threshold or 
        income_concentration > concentration_threshold or 
        score < score_threshold
    )
    
    if show_alert:
        st.warning(
            """
            **⚠️ Strategic Risk Detected**

            Your current income structure shows signs of concentration risk.
            If this exposure remains unchanged, your financial defensibility
            is likely to deteriorate over the next 6–12 months — even with stable revenue.
            """
        )
        
        # IF → THEN REASONING
        st.markdown(
            """
            **If nothing changes:**
            - Income concentration remains above 65%
            - Emergency coverage stays below 6 months
            - Moat Score drifts into the vulnerability zone

            Strategic operators intervene **before** metrics collapse.
            """
        )
        
        st.markdown("---")
    
    # ============================================
    # MOAT SCORE (posizione secondaria)
    # ============================================
    
    st.markdown(f"### Your Position: **{archetype.get('name', 'Operator')}**")
    st.caption(archetype.get('description', ''))
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Moat Score", 
            score,
            delta=None,
            help="Your current financial defensibility position"
        )
    
    with col2:
        st.metric(
            "Emergency Coverage",
            f"{emergency_months:.1f} mo",
            delta=None,
            help="Months of expenses covered by liquid reserves"
        )
    
    with col3:
        st.metric(
            "Income Concentration",
            f"{income_concentration}%",
            delta=None,
            help="% of income from primary source"
        )
    
    st.markdown("---")
    
    # ============================================
    # POSITIONING STATEMENT
    # ============================================
    
    st.markdown("### Your Strategic Position")
    
    if score >= 80:
        st.success(
            """
            **Strong defensive position.**  
            You have room to allocate capital toward growth without compromising stability.
            """
        )
    elif score >= 65:
        st.info(
            """
            **Adequate defense, limited optionality.**  
            You can withstand standard shocks, but lack leverage for strategic moves.
            """
        )
    else:
        st.error(
            """
            **Vulnerable position.**  
            Current structure exposes you to cascading risks if one variable shifts.
            """
        )
