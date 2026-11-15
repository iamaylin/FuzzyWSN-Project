
from src.fuzzy_system import triangular_membership


def evaluate_type1_rules(inputs, rules):
    results = []

    for rule in rules:
        strengths = []

        for variable, params in zip(
            ["energy", "delay", "trust"],
            rule["membership_functions"]
        ):
            upper = params["upper"]
            lower = params["lower"]

            # Type-1 reference: midpoint of IT2 membership bounds
            upper_mu = triangular_membership(
                inputs[variable], *upper
            )
            lower_mu = triangular_membership(
                inputs[variable], *lower
            )

            strengths.append(
                (upper_mu + lower_mu) / 2
            )

        results.append({
            "name": rule["name"],
            "strength": min(strengths),
            "output": rule["output"]
        })

    return results


def defuzzify_type1(results):
    numerator = sum(
        r["strength"] * r["output"]
        for r in results
    )

    denominator = sum(
        r["strength"]
        for r in results
    )

    if denominator <= 0:
        raise ValueError("No Type-1 rules were activated")

    return numerator / denominator