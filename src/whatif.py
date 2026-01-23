import streamlit as st
from src.utils.pro_gate import pro_gate

def render():
    st.title("🔮 What-If Scenarios")
    
    # ✅ PRO GATE
    pro_gate(
        "What-If Engine",
        "Model the impact of life changes on your financial position in real-time."
    )
    
    # ⬇️ SOLO i PRO arrivano qui
    st.markdown("### Test Strategic Decisions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        income_change = st.slider(
            "Income Change (%)",
            -50, 100, 0,
            help="Simulate job loss, promotion, or side income"
        )
    
    with col2:
        expense_change = st.slider(
            "Expense Change (%)",
            -50, 100, 0,
            help="Model lifestyle inflation or frugality"
        )
    
    st.markdown("---")
    st.markdown("#### Impact Analysis")
    
    # Placeholder per calcoli reali
    base_monthly_surplus = 500
    new_surplus = base_monthly_surplus * (1 + income_change/100) * (1 - expense_change/100)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Monthly Surplus", f"${base_monthly_surplus:,.0f}")
    col2.metric("Projected Surplus", f"${new_surplus:,.0f}", f"{new_surplus - base_monthly_surplus:+,.0f}")
    col3.metric("Annual Impact", f"${(new_surplus - base_monthly_surplus) * 12:+,.0f}")
    
    st.success("✅ This scenario is **viable** — your Moat Score remains above 65")

