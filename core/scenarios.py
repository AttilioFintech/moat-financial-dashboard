def apply_scenario(base_metrics, income_delta=0, expense_delta=0):
    scenario = base_metrics.copy()

    scenario["income"] *= (1 + income_delta / 100)
    scenario["expenses"] *= (1 + expense_delta / 100)
