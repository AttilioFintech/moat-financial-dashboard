from core.metrics import calculate_emergency_months
from core.scoring import calculate_moat_score

def render():
    emergency_months = calculate_emergency_months(12000, 2500)

    score = calculate_moat_score({
        "emergency_months": emergency_months,
        "expense_growth": 8,
        "income_concentration": 60
    })

    st.metric("Moat Score", score)

