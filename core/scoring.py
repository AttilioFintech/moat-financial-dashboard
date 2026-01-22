def calculate_moat_score(metrics):
    score = 100

    if metrics["emergency_months"] < 3:
        score -= 25
    if metrics["expense_growth"] > 10:
        score -= 15
    if metrics["income_concentration"] > 70:
        score -= 20

    return max(score, 0)
