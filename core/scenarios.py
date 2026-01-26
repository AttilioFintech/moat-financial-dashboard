def apply_scenario(base_metrics, income_delta=0, expense_delta=0):
    """
    Applica modifiche percentuali a income ed expenses.
    Restituisce un nuovo dict con metriche aggiornate.
    """
    scenario = base_metrics.copy()

    # Applica delta percentuali
    scenario["income"] = base_metrics["income"] * (1 + income_delta / 100)
    scenario["expenses"] = base_metrics["expenses"] * (1 + expense_delta / 100)
    
    # Ricalcola metriche derivate
    scenario["monthly_surplus"] = scenario["income"] - scenario["expenses"]
    scenario["emergency_fund"] = base_metrics.get("emergency_fund", scenario["expenses"] * 4.8)
    
    return scenario


def compare_scenarios(base_metrics, scenarios):
    """
    Compara multiple scenari e restituisce ranking.
    
    Args:
        base_metrics: dict con metriche attuali
        scenarios: list of dicts, ciascuno con income_delta e expense_delta
    
    Returns:
        list of dicts con scenario + impact analysis
    """
    results = []
    
    for idx, scenario_params in enumerate(scenarios):
        scenario = apply_scenario(
            base_metrics,
            income_delta=scenario_params.get("income_delta", 0),
            expense_delta=scenario_params.get("expense_delta", 0)
        )
        
        # Calcola impact
        surplus_delta = scenario["monthly_surplus"] - base_metrics.get("monthly_surplus", 0)
        annual_impact = surplus_delta * 12
        
        results.append({
            "name": scenario_params.get("name", f"Scenario {idx+1}"),
            "metrics": scenario,
            "surplus_delta": surplus_delta,
            "annual_impact": annual_impact
        })
    
    # Ordina per annual_impact (descending)
    results.sort(key=lambda x: x["annual_impact"], reverse=True)
    
    return results


def stress_test(base_metrics, stress_scenarios=None):
    """
    Testa resilienza contro scenari estremi.
    
    Default stress scenarios:
    - Job loss (-100% income for 3 months, then 50% for 3 months)
    - Major expense shock (+50% expenses for 6 months)
    - Combination
    """
    if stress_scenarios is None:
        stress_scenarios = [
            {"name": "Job Loss", "income_delta": -100, "expense_delta": 0, "duration_months": 3},
            {"name": "Expense Shock", "income_delta": 0, "expense_delta": 50, "duration_months": 6},
            {"name": "Combined Shock", "income_delta": -50, "expense_delta": 25, "duration_months": 6}
        ]
    
    results = []
    
    for stress in stress_scenarios:
        scenario = apply_scenario(
            base_metrics,
            income_delta=stress["income_delta"],
            expense_delta=stress["expense_delta"]
        )
        
        monthly_burn = scenario["expenses"] - scenario["income"]
        total_burn = monthly_burn * stress.get("duration_months", 3)
        
        emergency_fund = base_metrics.get("emergency_fund", base_metrics["expenses"] * 4.8)
        survives = emergency_fund >= total_burn
        
        results.append({
            "name": stress["name"],
            "monthly_burn": monthly_burn,
            "total_burn": total_burn,
            "survives": survives,
            "remaining_reserves": emergency_fund - total_burn if survives else 0
        })
    
    return results
