import streamlit as st
import plotly.graph_objects as go
from src.utils.pro_gate import pro_gate

def render():
    st.title("📈 12-Month Trajectory")
    
    ✅ PRO GATE
    pro_gate(
        "Trajectory Projection",
        "See how your current structure compounds into future positioning. "
        "What others discover after 12 months, you see now."
    )
    
    # ⬇️ SOLO i PRO arrivano qui
    st.markdown("### Your Financial Path")
    
    # Simulazione dati
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    current_savings = 10000
    monthly_surplus = 500
    
    savings_projection = [current_savings + (monthly_surplus * i) for i in range(1, 13)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=savings_projection,
        mode='lines+markers',
        name='Projected Savings',
        line=dict(color='#10b981', width=3),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    
    fig.update_layout(
        title="Savings Growth (Current Path)",
        xaxis_title="Month",
        yaxis_title="Total Savings ($)",
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### Key Insights")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Starting Position", f"${current_savings:,.0f}")
    col2.metric("12-Month Target", f"${savings_projection[-1]:,.0f}")
    col3.metric("Growth Rate", f"+{((savings_projection[-1]/current_savings - 1) * 100):.1f}%")

