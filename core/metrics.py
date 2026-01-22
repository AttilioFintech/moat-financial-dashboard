def calculate_savings_rate(income, expenses):
    if income <= 0:
        return 0
    return (income - expenses) / income * 100


def calculate_emergency_months(emergency_fund, monthly_expenses):
    if monthly_expenses <= 0:
        return 0
    return emergency_fund / monthly_expenses
