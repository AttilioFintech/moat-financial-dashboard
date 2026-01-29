import streamlit as st
from src.utils.pro_gate import pro_gate
from core.scenarios import apply_scenario
from core.scoring import calculate_moat_score

def render():
    st.title("🔮 What-If Engine")
    
    # ✅ PRO GATE
    pro_gate(
        "What-If Engine",
        "Test decisions **before committing time, capital, or reputation**. "
        "Strategic operators simulate consequences before acting."
    )
    
    # ⬇️ SOLO i PRO arrivano qui
    
    st.markdown("### Simulate Strategic Decisions")
    
    st.markdown(
        """
        Model how changes in your income or expense structure 
        affect your **Moat Score** and **financial defensibility**.
        
        This isn't forecasting — it's **decision testing**.
        """
    )
    
    st.markdown("---")
    
    # ============================================
    # SCENARIO CONTROLS
    # ============================================
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Income Adjustments")
        income_change = st.slider(
            "Income Change (%)",
            -50, 100, 0, 5,
            help="Model job loss (-30%), promotion (+20%), or side income (+50%)"
        )
        
        st.caption("**Examples:**")
        st.caption("• -30% = Job loss with severance")
        st.caption("• +20% = Promotion or raise")
        st.caption("• +50% = New revenue stream")
    
    with col2:
        st.markdown("#### Expense Adjustments")
        expense_change = st.slider(
            "Expense Change (%)",
            -50, 100, 0, 5,
            help="Model lifestyle changes, cost cuts, or new obligations"
        )
        
        st.caption("**Examples:**")
        st.caption("• -20% = Aggressive cost reduction")
        st.caption("• +15% = Lifestyle inflation")
        st.caption("• +30% = New dependent or obligation")
    
    st.markdown("---")
    
    # ============================================
    # SCENARIO CALCULATION
    # ============================================
    
    # Load user data
    financials = st.session_state.get("user_financials")
    
    if not financials:
        st.error("Financial data not found. Complete onboarding first.")
        st.stop()
    
    # Base metrics from real data
    base_metrics = {
        "income": financials["monthly_income"],
        "expenses": financials["monthly_expenses"],
        "emergency_months": financials["emergency_fund"] / financials["monthly_expenses"] if financials["monthly_expenses"] > 0 else 0,
        "expense_growth": 8,  # TODO: calculate from historical
        "income_concentration": financials["income_concentration"],
        "emergency_fund": financials["emergency_fund"]
    }
    
    # Applica scenario
    scenario_metrics = apply_scenario(base_metrics, income_change, expense_change)
    
    # Calcola Moat Scores
    base_score = calculate_moat_score(base_metrics)
    scenario_score = calculate_moat_score({
        "emergency_months": scenario_metrics["emergency_fund"] / scenario_metrics["expenses"] if scenario_metrics["expenses"] > 0 else 0,
        "expense_growth": base_metrics["expense_growth"],
        "income_concentration": base_metrics["income_concentration"]
    })
    
    score_delta = scenario_score - base_score
    
    # ============================================
    # IMPACT ANALYSIS
    # ============================================
    
    st.markdown("### Impact Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Current Monthly Surplus",
            f"${base_metrics['income'] - base_metrics['expenses']:,.0f}"
        )
    
    with col2:
        new_surplus = scenario_metrics['income'] - scenario_metrics['expenses']
        st.metric(
            "Scenario Monthly Surplus",
            f"${new_surplus:,.0f}",
            delta=f"{new_surplus - (base_metrics['income'] - base_metrics['expenses']):+,.0f}"
        )
    
    with col3:
        st.metric(
            "Annual Impact",
            f"${(new_surplus - (base_metrics['income'] - base_metrics['expenses'])) * 12:+,.0f}"
        )
    
    st.markdown("---")
    
    # ============================================
    # MOAT SCORE IMPACT
    # ============================================
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Current Moat Score", base_score)
    
    with col2:
        st.metric(
            "Scenario Moat Score",
            scenario_score,
            delta=f"{score_delta:+.0f}",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # ============================================
    # STRATEGIC ASSESSMENT
    # ============================================
    
    st.markdown("### Strategic Assessment")
    
    if scenario_score >= 75:
        st.success(
            f"""
            **✅ Strong Position**
            
            This scenario maintains or improves your defensive position.  
            Moat Score remains in the resilient zone ({scenario_score}).
            
            **Operators in your archetype** would consider this path viable.
            """
        )
    elif scenario_score >= 65:
        st.info(
            f"""
            **⚠️ Manageable Position**
            
            This scenario is viable but reduces strategic flexibility.  
            Moat Score: {scenario_score} (adequate but not optimal).
            
            Consider whether this tradeoff serves your time horizon.
            """
        )
    else:
        st.error(
            f"""
            **🔴 Vulnerable Position**
            
            This scenario significantly weakens your financial defensibility.  
            Moat Score drops to {scenario_score} — structural risk zone.
            
            **If you proceed:** Emergency reserves and expense reduction become critical priorities.
            """
        )
    
    st.markdown("---")
    
    # ============================================
    # OPERATOR INSIGHT (unique to PRO)
    # ============================================
    
    with st.expander("🧠 What operators like you typically do"):
        archetype = st.session_state.get("archetype", {}).get("name", "Operator")
        
        st.markdown(f"**For {archetype}s facing similar scenarios:**")
        
        if income_change < -20:
            st.markdown(
                """
                - Immediately cut discretionary expenses by 15-25%
                - Accelerate side income exploration
                - Extend emergency runway to 9+ months before considering new obligations
                """
            )
        elif income_change > 30:
            st.markdown(
                """
                - Resist immediate lifestyle inflation
                - Allocate 50%+ of new income to emergency fund until 12 months covered
                - Use remaining surplus to reduce income concentration risk
                """
            )
        elif expense_change > 20:
            st.markdown(
                """
                - Audit for cost creep in recurring subscriptions
                - Negotiate fixed costs (insurance, housing if possible)
                - Ensure expense growth doesn't exceed income growth rate
                """
            )
        else:
            st.markdown(
                """
                - Monitor monthly — small changes compound over 12 months
                - Maintain emergency fund coverage above 6 months
                - Review income diversification quarterly
                """
            )
