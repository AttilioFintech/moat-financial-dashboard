import streamlit as st
from core.persistence import save_user_financials, save_onboarding

def determine_archetype(income_type, volatility, time_horizon):
    """
    Determina l'archetype iniziale basato sulle 3 risposte.
    Non è un quiz — è una dichiarazione di posizione.
    """
    
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
        return {
            "name": "Emerging Operator",
            "baseline_score": 65,
            "alert_sensitivity": "medium",
            "description": "Building strategic position across variable conditions."
        }


def calculate_income_concentration(income_sources):
    """
    Calcola concentrazione reddito da lista di sources.
    """
    if not income_sources or len(income_sources) == 0:
        return 100
    
    amounts = [s["amount"] for s in income_sources if s["amount"] > 0]
    
    if not amounts:
        return 100
    
    total = sum(amounts)
    if total == 0:
        return 100
    
    max_source = max(amounts)
    concentration = (max_source / total) * 100
    
    return round(concentration, 1)


def render():
    st.title("⚙️ Strategic Setup")
    
    st.markdown(
        """
        ### Setup your financial position.
        
        This calibrates Moat to your structure — so alerts and simulations reflect your reality.
        """
    )
    
    st.markdown("---")
    
    # ============================================
    # SECTION 1: STRATEGIC CONTEXT (3 domande originali)
    # ============================================
    
    st.markdown("## Part 1: Strategic Context")
    
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
    
    st.markdown("#### 2. Income Volatility")
    
    volatility = st.select_slider(
        "How stable is your income month-to-month?",
        options=["Low", "Medium", "High"],
        value="Medium",
        help="High volatility requires different defense structures.",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
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
    st.markdown("---")
    
    # ============================================
    # SECTION 2: FINANCIAL METRICS (dati reali)
    # ============================================
    
    st.markdown("## Part 2: Current Position")
    st.caption("These numbers drive all calculations. Be accurate.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_income = st.number_input(
            "Total Monthly Income ($)",
            min_value=0,
            value=5000,
            step=500,
            help="All sources combined (after tax)"
        )
    
    with col2:
        monthly_expenses = st.number_input(
            "Total Monthly Expenses ($)",
            min_value=0,
            value=3000,
            step=500,
            help="All recurring + discretionary spending"
        )
    
    st.markdown("---")
    
    emergency_fund = st.number_input(
        "Emergency Fund / Liquid Savings ($)",
        min_value=0,
        value=10000,
        step=1000,
        help="Cash immediately accessible (checking, savings, not investments)"
    )
    
    st.markdown("---")
    
    # ============================================
    # SECTION 3: INCOME SOURCES (concentration)
    # ============================================
    
    st.markdown("### Income Sources")
    st.caption("This calculates your concentration risk.")
    
    num_sources = st.number_input(
        "How many income sources?",
        min_value=1,
        max_value=5,
        value=1,
        step=1
    )
    
    income_sources = []
    
    for i in range(num_sources):
        st.markdown(f"**Source {i+1}**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            source_name = st.text_input(
                f"Name (e.g., W2 Salary, Freelance)",
                value=f"Source {i+1}",
                key=f"source_name_{i}"
            )
        
        with col2:
            source_amount = st.number_input(
                f"Monthly Amount ($)",
                min_value=0,
                value=monthly_income if i == 0 else 0,
                step=500,
                key=f"source_amount_{i}"
            )
        
        income_sources.append({
            "name": source_name,
            "amount": source_amount
        })
    
    # Verifica che somma sources = total income
    total_sources = sum(s["amount"] for s in income_sources)
    
    if total_sources != monthly_income:
        st.warning(
            f"""
            ⚠️ Income mismatch:  
            Total sources: ${total_sources:,}  
            Stated income: ${monthly_income:,}
            
            Adjust source amounts to match total income.
            """
        )
    
    st.markdown("---")
    
    # ============================================
    # SUBMIT & SAVE
    # ============================================
    
    if st.button("Lock In Position", type="primary", use_container_width=True):
        
        # Validate
        if total_sources != monthly_income:
            st.error("Fix income mismatch before submitting.")
            st.stop()
        
        # Calculate concentration
        concentration = calculate_income_concentration(income_sources)
        
        # Determine archetype
        archetype = determine_archetype(income_type, volatility, time_horizon)
        
        # Save to session state
        st.session_state["onboarding_complete"] = True
        st.session_state["archetype"] = archetype
        st.session_state["income_type"] = income_type
        st.session_state["volatility"] = volatility
        st.session_state["time_horizon"] = time_horizon
        
        # CRITICAL: Save financial data
        st.session_state["user_financials"] = {
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "emergency_fund": emergency_fund,
            "income_sources": income_sources,
            "income_concentration": concentration
        }
        
        # PERSIST TO DATABASE
        save_onboarding(income_type, volatility, time_horizon, archetype)
        save_user_financials(st.session_state["user_financials"])
        
        # Feedback
        st.success(
            f"""
            **Position Locked**
            
            Archetype: **{archetype['name']}**  
            {archetype['description']}
            
            Your baseline Moat Score: **{archetype['baseline_score']}**  
            Income concentration: **{concentration}%**
            """
        )
        
        st.markdown("---")
        
        st.info("Navigate to **Dashboard** to see your strategic position.")
    
    # ============================================
    # OPTIONAL: Why these questions?
    # ============================================
    
    with st.expander("Why these questions?"):
        st.markdown(
            """
            **Strategic Context** determines archetype and alert sensitivity.
            
            **Financial Metrics** are used in ALL calculations:
            - Moat Score
            - Emergency coverage
            - Stress tests
            - What-If scenarios
            
            **Income Sources** calculate concentration risk — a core vulnerability metric.
            
            All values are saved and used throughout the app.
            """
        )
