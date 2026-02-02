"""
PRO-exclusive: Operator comparison insights
Mostra cosa fanno operatori simili in condizioni simili
"""

def get_archetype_benchmarks(archetype_name):
    """
    Restituisce benchmark per archetype.
    MVP: dati simulati. Production: dati aggregati (anonimizzati).
    """
    
    benchmarks = {
        "Stable Operator": {
            "avg_emergency_months": 8.2,
            "avg_savings_rate": 22,
            "typical_income_concentration": 85,
            "common_actions": [
                "Maintain 9-12 months emergency coverage",
                "Allocate 15-20% of surplus to growth investments",
                "Review income diversification annually"
            ]
        },
        "Variable Operator": {
            "avg_emergency_months": 11.5,
            "avg_savings_rate": 18,
            "typical_income_concentration": 55,
            "common_actions": [
                "Keep 12+ months liquid reserves due to volatility",
                "Aggressively reduce fixed costs",
                "Diversify income within 6 months of hitting 12-month coverage"
            ]
        },
        "Portfolio Operator": {
            "avg_emergency_months": 9.8,
            "avg_savings_rate": 25,
            "typical_income_concentration": 45,
            "common_actions": [
                "Monitor concentration risk quarterly",
                "Ensure no single source exceeds 50%",
                "Build optionality through multiple income streams"
            ]
        },
        "Emerging Operator": {
            "avg_emergency_months": 6.5,
            "avg_savings_rate": 15,
            "typical_income_concentration": 75,
            "common_actions": [
                "Prioritize emergency fund to 6 months minimum",
                "Identify and reduce largest expense category by 10-15%",
                "Explore side income within 90 days"
            ]
        }
    }
    
    return benchmarks.get(archetype_name, benchmarks["Emerging Operator"])


def compare_to_archetype(user_metrics, archetype_name):
    """
    Compara metriche utente con benchmark archetype.
    Restituisce gaps e positioning.
    """
    
    benchmarks = get_archetype_benchmarks(archetype_name)
    
    comparison = {
        "emergency_months": {
            "user": user_metrics.get("emergency_months", 0),
            "benchmark": benchmarks["avg_emergency_months"],
            "gap": user_metrics.get("emergency_months", 0) - benchmarks["avg_emergency_months"]
        },
        "savings_rate": {
            "user": user_metrics.get("savings_rate", 0),
            "benchmark": benchmarks["avg_savings_rate"],
            "gap": user_metrics.get("savings_rate", 0) - benchmarks["avg_savings_rate"]
        },
        "income_concentration": {
            "user": user_metrics.get("income_concentration", 100),
            "benchmark": benchmarks["typical_income_concentration"],
            "gap": user_metrics.get("income_concentration", 100) - benchmarks["typical_income_concentration"]
        }
    }
    
    return {
        "comparison": comparison,
        "common_actions": benchmarks["common_actions"]
    }


def get_scenario_recommendations(archetype_name, scenario_type):
    """
    Restituisce cosa fanno operators simili in scenario specifico.
    
    ⚠️ PRO ONLY - Questa funzione richiede Strategic Access
    
    Args:
        archetype_name: str
        scenario_type: "income_loss" | "income_gain" | "expense_increase"
    
    Returns:
        list of str: recommendations
    """
    # This function should only be called after PRO gate check
    # It's the caller's responsibility to verify PRO status
    
    recommendations = {
        "Stable Operator": {
            "income_loss": [
                "Immediately cut discretionary expenses by 15-20%",
                "Extend emergency runway before considering new income sources",
                "Avoid panic moves — stability recovers given time"
            ],
            "income_gain": [
                "Resist lifestyle inflation for first 6 months",
                "Allocate 50% of increase to emergency fund until 12 months covered",
                "Use remainder to reduce debt or increase investment allocation"
            ],
            "expense_increase": [
                "Audit recurring subscriptions quarterly",
                "Negotiate fixed costs (insurance, utilities)",
                "Ensure expense growth doesn't exceed 50% of income growth"
            ]
        },
        "Variable Operator": {
            "income_loss": [
                "Cut fixed costs aggressively (target 25-30% reduction)",
                "Activate backup income streams within 30 days",
                "Preserve 12+ months emergency coverage at all costs"
            ],
            "income_gain": [
                "Bank 70% of upside — volatility works both ways",
                "Don't increase fixed obligations during good months",
                "Use surplus to build 18+ month runway"
            ],
            "expense_increase": [
                "Review every recurring cost — variable income can't support bloat",
                "Keep fixed expenses below 40% of average monthly income",
                "Build expense buffer to handle income troughs"
            ]
        },
        "Portfolio Operator": {
            "income_loss": [
                "Identify which stream dropped — diversify that vulnerability",
                "Ensure no single income loss threatens total position",
                "Maintain minimum 9 months coverage even during downturns"
            ],
            "income_gain": [
                "Allocate gains to strengthen weakest income stream",
                "Avoid over-allocating to highest-performing source",
                "Build optionality across multiple channels"
            ],
            "expense_increase": [
                "Monitor expense-to-income ratio per stream",
                "Ensure total expenses stay below 60% of total income",
                "Cut expenses if any single stream shows sustained decline"
            ]
        }
    }
    
    archetype_recs = recommendations.get(archetype_name, recommendations["Stable Operator"])
    return archetype_recs.get(scenario_type, [])