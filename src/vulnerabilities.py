import streamlit as st
from core.vulnerabilities import emergency_fund_risk, expense_growth_risk

def identify_top_risk(metrics):
    """
    Identifica IL rischio dominante.
    Non restituisce liste — restituisce UNA vulnerabilità strutturale.
    """
    
    risks = []
    
    # Emergency Fund Risk
    if metrics["emergency_months"] < 3:
        risks.append({
            "severity": 10,
            "type": "structural",
            "title": "Critical Liquidity Exposure",
            "description": "Your emergency position cannot absorb a single major disruption."
        })
    elif metrics["emergency_months"] < 6:
        risks.append({
            "severity": 7,
            "type": "defensive",
            "title": "Limited Shock Absorption",
            "description": "Current reserves provide minimal buffer against income loss."
        })
    
    # Income Concentration Risk
    if metrics["income_concentration"] > 80:
        risks.append({
            "severity": 9,
            "type": "structural",
            "title": "Single-Source Income Dependency",
            "description": "Your financial structure collapses if one income stream fails."
        })
    elif metrics["income_concentration"] > 65:
        risks.append({
            "severity": 6,
            "type": "strategic",
            "title": "Concentration Risk",
            "description": "Over-reliance on primary income reduces strategic flexibility."
        })
    
    # Expense Growth Risk
    if metrics["expense_growth"] > 10:
        risks.append({
            "severity": 8,
            "type": "operational",
            "title": "Cost Structure Inflation",
            "description": "Expense growth is outpacing income capacity to absorb it."
        })
    
    # Ordina per severity e restituisci SOLO il primo
    if risks:
        top_risk = sorted(risks, key=lambda x: x["severity"], reverse=True)[0]
        return top_risk
    
    return None


def render():
    st.title("🛡️ Strategic Vulnerabilities")
    
    # Simulazione metriche (da sostituire con dati reali)
    metrics = {
        "emergency_months": 4.8,
        "income_concentration": 75,
        "expense_growth": 8
    }
    
    # Identifica IL rischio dominante
    top_risk = identify_top_risk(metrics)
    
    if top_risk:
        st.markdown("### Your Top Strategic Risk")
        
        # Colore basato su tipo
        if top_risk["type"] == "structural":
            alert_type = st.error
        elif top_risk["type"] == "strategic":
            alert_type = st.warning
        else:
            alert_type = st.info
        
        alert_type(
            f"""
            **{top_risk["title"]}**
            
            {top_risk["description"]}
            """
        )
        
        st.markdown("---")
        
        # If nothing changes block
        st.markdown("#### If This Persists")
        
        st.markdown(
            """
            - Your Moat Score will continue declining
            - Strategic optionality decreases
            - Recovery time from shocks increases exponentially
            
            Operators with strong moats act **before** the market forces them to.
            """
        )
    else:
        st.success(
            """
            **No critical vulnerabilities detected.**
            
            Your current position shows adequate defensive structure.
            Focus remains on maintaining optionality.
            """
        )
    
    st.markdown("---")
    
    # Dettaglio metriche (secondario)
    with st.expander("📊 Metric Breakdown"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Emergency Fund Status**")
            st.write(emergency_fund_risk(metrics["emergency_months"]))
        
        with col2:
            st.markdown("**Expense Growth Status**")
            st.write(expense_growth_risk(metrics["expense_growth"]))
