def emergency_fund_risk(months):
    if months < 3:
        return "Structural Risk Detected"
    if months < 6:
        return "Limited Buffer"
    return "Adequate Defense"


def expense_growth_risk(growth_rate):
    if growth_rate > 10:
        return "Cost Creep Risk"
    if growth_rate > 5:
        return "Monitoring Required"
