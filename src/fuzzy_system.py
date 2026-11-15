
import numpy as np


def gaussian_membership(x, center, sigma):
    """
    Gaussian membership function.

    Parameters
    ----------
    x : float or array
        Input value.
    center : float
        Center of the membership function.
    sigma : float
        Standard deviation (must be positive).

    Returns
    -------
    float or array
        Membership degree between 0 and 1.
    """
    if sigma <= 0:
        raise ValueError("sigma must be positive")

    x = np.asarray(x, dtype=float)

    return np.exp(
        -0.5 * ((x - center) / sigma) ** 2
    )


def interval_type2_membership(
    x,
    center,
    sigma_lower,
    sigma_upper
):
    """
    Interval Type-2 Gaussian membership function.

    Returns lower and upper membership degrees.
    """
    if sigma_lower <= 0 or sigma_upper <= 0:
        raise ValueError("Sigma values must be positive")

    if sigma_lower > sigma_upper:
        raise ValueError(
            "sigma_lower must not exceed sigma_upper"
        )

    lower = gaussian_membership(
        x, center, sigma_lower
    )

    upper = gaussian_membership(
        x, center, sigma_upper
    )

    return lower, upper


def triangular_membership(x, a, b, c):
    if not a < b < c:
        raise ValueError("Expected a < b < c")

    if x <= a or x >= c:
        return 0.0

    if x == b:
        return 1.0

    if x < b:
        return (x - a) / (b - a)

    return (c - x) / (c - b)


def interval_type2_triangular(x, upper, lower):
    upper_value = triangular_membership(x, *upper)
    lower_value = triangular_membership(x, *lower)

    if lower_value > upper_value:
        raise ValueError(
            "Lower membership exceeds upper membership"
        )

    return lower_value, upper_value


def fuzzy_rule_strength(
    energy,
    delay,
    trust,
    membership_functions
):
    """
    Calculate interval-valued rule firing strength.
    """

    lower_values = []
    upper_values = []

    for value, params in zip(
        [energy, delay, trust],
        membership_functions
    ):
        lower, upper = interval_type2_triangular(
            value,
            params["upper"],
            params["lower"]
        )

        lower_values.append(lower)
        upper_values.append(upper)

    return min(lower_values), min(upper_values)


def evaluate_fuzzy_rules(inputs, rules):
    """
    Evaluate fuzzy rules using minimum t-norm.
    """

    results = []

    for rule in rules:
        lower, upper = fuzzy_rule_strength(
            inputs["energy"],
            inputs["delay"],
            inputs["trust"],
            rule["membership_functions"]
        )

        results.append({
            "name": rule["name"],
            "lower_strength": lower,
            "upper_strength": upper,
            "output": rule["output"]
        })

    return results



def karnik_mendel(rules, tolerance=1e-8, max_iterations=100):
    import numpy as np

    active = [
        r for r in rules
        if r["upper_strength"] > 0
    ]

    if not active:
        raise ValueError("No fuzzy rules were activated")

    outputs = np.array(
        [r["output"] for r in active], dtype=float
    )
    lower = np.array(
        [r["lower_strength"] for r in active], dtype=float
    )
    upper = np.array(
        [r["upper_strength"] for r in active], dtype=float
    )

    if (
        np.any(lower < 0)
        or np.any(upper > 1)
        or np.any(lower > upper)
    ):
        raise ValueError("Invalid firing strength interval")

    order = np.argsort(outputs)
    outputs = outputs[order]
    lower = lower[order]
    upper = upper[order]

    def endpoint(left):
        weights = (lower + upper) / 2

        for _ in range(max_iterations):
            denominator = np.sum(weights)

            if denominator <= 0:
                raise ValueError("Zero total firing strength")

            y = np.sum(outputs * weights) / denominator

            if left:
                new_weights = np.where(
                    outputs <= y, upper, lower
                )
            else:
                new_weights = np.where(
                    outputs <= y, lower, upper
                )

            new_denominator = np.sum(new_weights)

            if new_denominator <= 0:
                raise ValueError("Zero total firing strength")

            new_y = (
                np.sum(outputs * new_weights)
                / new_denominator
            )

            if abs(new_y - y) < tolerance:
                return float(new_y)

            weights = new_weights

        raise RuntimeError(
            "Karnik-Mendel algorithm did not converge"
        )

    y_left = endpoint(left=True)
    y_right = endpoint(left=False)

    return y_left, y_right



def defuzzify_interval_type2(rules):
    """
    Return the crisp output of the IT2 fuzzy system.
    """
    y_left, y_right = karnik_mendel(rules)
    return (y_left + y_right) / 2