import streamlit as st

def determine_archetype(income_type, volatility, time_horizon):
    """
    Determina l'archetype iniziale basato sulle 3 risposte.
    Non è un quiz — è una dichiarazione di posizione.
    """
    
    # Mapping semplice ma efficace
    if income_type == "W2 / Salary" and volatility == "Low" and time_horizon in ["12 months", "36+ months"]:
        return {
            "name": "Stable Operator",
            "baseline_score": 75,
            "alert_sensitivity": "standard",
            "description": "Predictable income, building defensive position over time."
        }
    
    elif income_type == "Business / Freelance" and volatility == "High":
        return {
            "name": "Variable Operator",
            "baseline_score": 60,
            "alert_sensitivity": "high",
            "description": "Revenue volatility requires higher cash reserves and faster decision cycles."
        }
    
    elif income_type == "Mixed Sources":
        return {
            "name": "Portfolio Operator",
            "baseline_score": 70,
            "alert_sensitivity": "medium",
            "description": "Diversified income structure provides optionality but requires active monitoring."
        }
    
    else:
        # Default fallback
        return {
            "name": "Emerging Operator",
            "baseline_score": 65,
            "alert_sensitivity": "medium",
            "description": "Building strategic position across variable conditions."
        }


def render():
    st.title("⚙️ Strategic Setup")
    
    st.markdown(
        """
        ### Three questions to calibrate your position.
        
        This isn't data collection.  
        It's **context setting** — so Moat knows what matters to you.
        """
    )
    
    st.markdown("---")
    
    # ============================================
    # QUESTION 1: Primary Income Type
    # ============================================
    
    st.markdown("#### 1. Primary Income Structure")
    
    income_type = st.radio(
        "How do you earn?",
        [
            "W2 / Salary",
            "Business / Freelance",
            "Mixed Sources",
            "Investment / Passive"
        ],
        help="This determines your baseline volatility profile.",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # ============================================
    # QUESTION 2: Perceived Volatility
    # ============================================
    
    st.markdown("#### 2. Income Volatility")
    
    volatility = st.select_slider(
        "How stable is your income month-to-month?",
        options=["Low", "Medium", "High"],
        value="Medium",
        help="High volatility requires different defense structures.",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # ============================================
    # QUESTION 3: Time Horizon
    # ============================================
    
    st.markdown("#### 3. Strategic Time Horizon")
    
    time_horizon = st.radio(
        "What timeframe matters most to you?",
        [
            "6 months — immediate stability",
            "12 months — building optionality",
            "36+ months — compounding position"
        ],
        help="Shorter horizons prioritize liquidity. Longer horizons allow strategic allocation.",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # ============================================
    # SUBMIT & ARCHETYPE ASSIGNMENT
    # ============================================
    
    if st.button("Lock In Position", type="primary", use_container_width=True):
        
        # Determina archetype
        archetype = determine_archetype(income_type, volatility, time_horizon)
        
        # Salva in session state
        st.session_state["onboarding_complete"] = True
        st.session_state["archetype"] = archetype
        st.session_state["income_type"] = income_type
        st.session_state["volatility"] = volatility
        st.session_state["time_horizon"] = time_horizon
        
        # Feedback immediato
        st.success(
            f"""
            **Position Locked**
            
            Archetype: **{archetype['name']}**  
            {archetype['description']}
            
            Your Moat Score baseline: **{archetype['baseline_score']}**
            """
        )
        
        st.markdown("---")
        
        st.info("Navigate to **Dashboard** to see your strategic position.")
    
    # ============================================
    # OPTIONAL: Show Preview Before Submit
    # ============================================
    
    with st.expander("Why these questions?"):
        st.markdown(
            """
            **Income Type** → Determines your structural risk profile.  
            W2 income has different vulnerabilities than freelance revenue.
            
            **Volatility** → Calibrates alert sensitivity.  
            High volatility requires tighter thresholds.
            
            **Time Horizon** → Affects which metrics matter most.  
            6-month focus = liquidity priority.  
            36-month focus = optionality priority.
            """
        )
