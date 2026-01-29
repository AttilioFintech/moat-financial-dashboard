import streamlit as st
from src.utils.pro_gate import pro_gate
from core.scenarios import stress_test

def render():
    st.title("⚡ Stress Test")
    
    # ✅ PRO GATE
    pro_gate(
        "Stress Test Engine",
        "Test your financial structure against extreme scenarios. "
        "See if your defenses hold when variables collapse simultaneously."
    )
    
    # ⬇️ SOLO i PRO arrivano qui
    
    st.markdown("### Test Structural Resilience")
    
    st.markdown(
        """
        Stress tests reveal whether your financial position can absorb **cascading shocks**.
        
        This isn't pessimism — it's **preparation**.  
        Operators who stress test don't panic when reality hits.
        """
    )
    
    st.markdown("---")
    
    # ============================================
    # BASE METRICS INPUT
    # ============================================
    
    # Load user data for defaults
    financials = st.session_state.get("user_financials", {})
    
    default_income = financials.get("monthly_income", 8000)
    default_expenses = financials.get("monthly_expenses", 5000)
    default_emergency = financials.get("emergency_fund", 12000)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monthly_income = st.number_input(
            "Monthly Income ($)",
            min_value=0,
            value=int(default_income),
            step=500
        )
    
    with col2:
        monthly_expenses = st.number_input(
            "Monthly Expenses ($)",
            min_value=0,
            value=int(default_expenses),
            step=500
        )
    
    with col3:
        emergency_fund = st.number_input(
            "Emergency Fund ($)",
            min_value=0,
            value=int(default_emergency),
            step=1000
        )
    
    base_metrics = {
        "income": monthly_income,
        "expenses": monthly_expenses,
        "emergency_fund": emergency_fund,
        "monthly_surplus": monthly_income - monthly_expenses
    }
    
    st.markdown("---")
    
    # ============================================
    # STRESS SCENARIOS
    # ============================================
    
    st.markdown("### Stress Scenarios")
    
    stress_scenarios = [
        {
            "name": "Job Loss (6 months)",
            "income_delta": -100,
            "expense_delta": -20,  # Assume cost cutting
            "duration_months": 6
        },
        {
            "name": "Major Expense Shock",
            "income_delta": 0,
            "expense_delta": 50,
            "duration_months": 3
        },
        {
            "name": "Income Drop + Cost Increase",
            "income_delta": -50,
            "expense_delta": 25,
            "duration_months": 6
        },
        {
            "name": "Recession Scenario",
            "income_delta": -30,
            "expense_delta": 10,
            "duration_months": 12
        }
    ]
    
    results = stress_test(base_metrics, stress_scenarios)
    
    # ============================================
    # RESULTS DISPLAY
    # ============================================
    
    for result in results:
        with st.expander(f"**{result['name']}**", expanded=True):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Monthly Burn",
                    f"${result['monthly_burn']:,.0f}"
                )
            
            with col2:
                st.metric(
                    "Total Impact",
                    f"${result['total_burn']:,.0f}"
                )
            
            with col3:
                if result['survives']:
                    st.metric(
                        "Remaining Reserves",
                        f"${result['remaining_reserves']:,.0f}",
                        delta="✓ Survives"
                    )
                else:
                    st.metric(
                        "Status",
                        "DEPLETED",
                        delta="✗ Fails"
                    )
            
            # Assessment
            if result['survives']:
                if result['remaining_reserves'] > monthly_expenses * 3:
                    st.success(
                        f"""
                        **Position holds.** 
                        You survive this scenario with **${result['remaining_reserves']:,.0f}** remaining 
                        ({result['remaining_reserves'] / monthly_expenses:.1f} months coverage).
                        """
                    )
                else:
                    st.warning(
                        f"""
                        **Survives but depleted.** 
                        Reserves reduced to **${result['remaining_reserves']:,.0f}** 
                        ({result['remaining_reserves'] / monthly_expenses:.1f} months). 
                        Recovery would be prolonged.
                        """
                    )
            else:
                st.error(
                    f"""
                    **Structure fails.** 
                    Your emergency fund depletes **${abs(result['remaining_reserves']):,.0f}** 
                    before the scenario ends. This requires debt or forced liquidation.
                    """
                )
    
    st.markdown("---")
    
    # ============================================
    # OVERALL ASSESSMENT
    # ============================================
    
    st.markdown("### Overall Resilience")
    
    survived_count = sum(1 for r in results if r['survives'])
    total_scenarios = len(results)
    
    resilience_score = (survived_count / total_scenarios) * 100
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if resilience_score == 100:
            st.success(
                f"""
                **✅ Highly Resilient Position**
                
                Your structure survives **all {total_scenarios} stress scenarios**.
                
                This level of defense allows you to:
                - Take strategic risks without existential exposure
                - Maintain optionality during market dislocations
                - Absorb shocks without forced decisions
                """
            )
        elif resilience_score >= 50:
            st.warning(
                f"""
                **⚠️ Moderate Resilience**
                
                Your structure survives **{survived_count}/{total_scenarios} scenarios**.
                
                You can withstand single shocks but remain vulnerable to:
                - Prolonged income disruption
                - Multiple simultaneous stressors
                - Scenarios requiring 6+ months of defense
                """
            )
        else:
            st.error(
                f"""
                **🔴 Structurally Vulnerable**
                
                Your structure survives only **{survived_count}/{total_scenarios} scenarios**.
                
                Current reserves cannot absorb major shocks.
                Operators in your position prioritize:
                - Immediate expense reduction (20-30%)
                - Emergency fund acceleration to 9+ months
                - Income diversification within 90 days
                """
            )
    
    with col2:
        st.metric(
            "Resilience Score",
            f"{resilience_score:.0f}%",
            delta=f"{survived_count}/{total_scenarios} scenarios"
        )
    
    st.markdown("---")
    
    # ============================================
    # OPERATOR ACTIONS
    # ============================================
    
    with st.expander("🧠 What operators do with this information"):
        archetype = st.session_state.get("archetype", {}).get("name", "Operator")
        
        st.markdown(f"**For {archetype}s with {resilience_score:.0f}% resilience:**")
        
        if resilience_score == 100:
            st.markdown(
                """
                - Maintain current defense structure
                - Allocate surplus toward growth or optionality
                - Review stress tests quarterly to ensure resilience persists
                """
            )
        elif resilience_score >= 50:
            st.markdown(
                """
                - Identify which scenario caused failure
                - Address that specific vulnerability first
                - Increase emergency fund by 2-3 months before pursuing growth
                """
            )
        else:
            st.markdown(
                """
                - Treat this as structural emergency
                - Cut discretionary expenses immediately (20-30%)
                - Pause all non-essential allocations until 6+ months covered
                - Accelerate income diversification — single-source dependency is critical risk
                """
            )
