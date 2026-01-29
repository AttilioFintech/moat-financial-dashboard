import streamlit as st
import plotly.graph_objects as go
from src.utils.pro_gate import pro_gate
from core.trajectory import project_savings

def render():
    st.title("📈 12-Month Trajectory")
    
    # ✅ PRO GATE
    pro_gate(
        "Trajectory Projection",
        "See how your current structure compounds into future positioning. "
        "What others discover after 12 months, you see now."
    )
    
    # ⬇️ SOLO i PRO arrivano qui
    
    st.markdown("### Your Financial Path")
    
    st.markdown(
        """
        This projection shows where your **current habits** lead over 12 months.
        
        Not a forecast. Not a goal.  
        A **trajectory** based on your existing structure.
        """
    )
    
    st.markdown("---")
    
    # ============================================
    # TRAJECTORY CONTROLS
    # ============================================
    
    # Load user data for defaults
    financials = st.session_state.get("user_financials", {})
    
    default_savings = financials.get("emergency_fund", 10000)
    default_surplus = financials.get("monthly_income", 5000) - financials.get("monthly_expenses", 3000)
    default_expenses = financials.get("monthly_expenses", 2500)
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_savings = st.number_input(
            "Current Liquid Savings ($)",
            min_value=0,
            value=int(default_savings),
            step=1000,
            help="Cash + immediately accessible reserves"
        )
    
    with col2:
        monthly_surplus = st.number_input(
            "Average Monthly Surplus ($)",
            value=int(default_surplus),
            step=100,
            help="Typical income minus expenses (after all obligations)"
        )
    
    st.markdown("---")
    
    # ============================================
    # PROJECTION CALCULATION
    # ============================================
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    savings_projection = project_savings(current_savings, monthly_surplus, months=12)
    
    # Alternative scenarios
    conservative_projection = project_savings(current_savings, monthly_surplus * 0.7, months=12)
    aggressive_projection = project_savings(current_savings, monthly_surplus * 1.3, months=12)
    
    # ============================================
    # VISUALIZATION
    # ============================================
    
    fig = go.Figure()
    
    # Main trajectory
    fig.add_trace(go.Scatter(
        x=months,
        y=savings_projection,
        mode='lines+markers',
        name='Current Path',
        line=dict(color='#10b981', width=3),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    
    # Conservative scenario (if surplus drops)
    fig.add_trace(go.Scatter(
        x=months,
        y=conservative_projection,
        mode='lines',
        name='If Surplus Drops 30%',
        line=dict(color='#f59e0b', width=2, dash='dash'),
        opacity=0.6
    ))
    
    # Aggressive scenario (if surplus increases)
    fig.add_trace(go.Scatter(
        x=months,
        y=aggressive_projection,
        mode='lines',
        name='If Surplus Grows 30%',
        line=dict(color='#3b82f6', width=2, dash='dash'),
        opacity=0.6
    ))
    
    fig.update_layout(
        title="Savings Trajectory (12-Month Projection)",
        xaxis_title="Month",
        yaxis_title="Total Liquid Savings ($)",
        hovermode='x unified',
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ============================================
    # KEY INSIGHTS
    # ============================================
    
    st.markdown("#### Trajectory Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Starting Position",
            f"${current_savings:,.0f}"
        )
    
    with col2:
        st.metric(
            "12-Month Target (Current Path)",
            f"${savings_projection[-1]:,.0f}",
            delta=f"+${savings_projection[-1] - current_savings:,.0f}"
        )
    
    with col3:
        growth_rate = ((savings_projection[-1] / current_savings - 1) * 100) if current_savings > 0 else 0
        st.metric(
            "Growth Rate",
            f"+{growth_rate:.1f}%"
        )
    
    st.markdown("---")
    
    # ============================================
    # STRATEGIC CONTEXT
    # ============================================
    
    st.markdown("### Strategic Context")
    
    # Emergency coverage projection
    monthly_expenses = default_expenses
    final_emergency_months = savings_projection[-1] / monthly_expenses if monthly_expenses > 0 else 0
    
    if final_emergency_months >= 12:
        st.success(
            f"""
            **✅ Strong Defensive Position**
            
            By month 12, you'll have **{final_emergency_months:.1f} months** of emergency coverage.
            
            This provides optionality: you can allocate capital toward growth, 
            reduce income concentration risk, or maintain strategic reserves.
            """
        )
    elif final_emergency_months >= 6:
        st.info(
            f"""
            **⚠️ Adequate but Limited**
            
            By month 12, you'll have **{final_emergency_months:.1f} months** of coverage.
            
            This meets minimum defense requirements but limits strategic flexibility.
            Consider accelerating savings or reducing fixed expenses.
            """
        )
    else:
        st.error(
            f"""
            **🔴 Insufficient Defense**
            
            By month 12, you'll only have **{final_emergency_months:.1f} months** of coverage.
            
            Current trajectory leaves you structurally vulnerable.
            Operators in your position prioritize expense reduction and income diversification.
            """
        )
    
    st.markdown("---")
    
    # ============================================
    # ALTERNATIVE PATHS (unique to PRO)
    # ============================================
    
    with st.expander("🧠 What if you adjusted your structure?"):
        st.markdown("#### Alternative Scenarios")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Path A: Cost Reduction**")
            st.markdown(
                f"""
                If you cut expenses by 15%:
                - New monthly surplus: **${monthly_surplus * 1.15:,.0f}**
                - 12-month position: **${project_savings(current_savings, monthly_surplus * 1.15, 12)[-1]:,.0f}**
                - Emergency coverage: **{project_savings(current_savings, monthly_surplus * 1.15, 12)[-1] / monthly_expenses:.1f} months**
                """
            )
        
        with col2:
            st.markdown("**Path B: Income Growth**")
            st.markdown(
                f"""
                If you increase income by 20%:
                - New monthly surplus: **${monthly_surplus * 1.20:,.0f}**
                - 12-month position: **${project_savings(current_savings, monthly_surplus * 1.20, 12)[-1]:,.0f}**
                - Emergency coverage: **{project_savings(current_savings, monthly_surplus * 1.20, 12)[-1] / monthly_expenses:.1f} months**
                """
            )
        
        st.markdown("---")
        st.caption(
            "**Operators in your archetype** typically prioritize defense first, "
            "then pursue growth once emergency coverage exceeds 9 months."
        )
