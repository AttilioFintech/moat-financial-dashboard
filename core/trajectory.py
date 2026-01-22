def project_savings(current_savings, monthly_delta, months=12):
    projections = []
    value = current_savings

    for _ in range(months):
        value += monthly_delta
        projections.append(value)
