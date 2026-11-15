
import numpy as np

from src.fuzzy_system import (
    evaluate_fuzzy_rules,
    defuzzify_interval_type2,
)
from src.type1_fuzzy import (
    evaluate_type1_rules,
    defuzzify_type1,
)


def membership(label):
    shapes = {
        "low": {
            "upper": (-0.5, 0.0, 0.5),
            "lower": (-0.4, 0.0, 0.4),
        },
        "medium": {
            "upper": (0.0, 0.5, 1.0),
            "lower": (0.1, 0.5, 0.9),
        },
        "high": {
            "upper": (0.5, 1.0, 1.5),
            "lower": (0.6, 1.0, 1.4),
        },
    }
    return shapes[label]


def build_rules():
    rules = []

    labels = ["low", "medium", "high"]

    for energy in labels:
        for delay in labels:
            for trust in labels:

                energy_score = {
                    "low": 1.0,
                    "medium": 0.5,
                    "high": 0.0,
                }[energy]

                delay_score = {
                    "low": 1.0,
                    "medium": 0.5,
                    "high": 0.0,
                }[delay]

                trust_score = {
                    "low": 0.0,
                    "medium": 0.5,
                    "high": 1.0,
                }[trust]

                output = (
                    0.35 * energy_score
                    + 0.25 * delay_score
                    + 0.40 * trust_score
                )

                rules.append({
                    "name": f"{energy}_{delay}_{trust}",
                    "membership_functions": [
                        membership(energy),
                        membership(delay),
                        membership(trust),
                    ],
                    "output": output,
                })

    return rules


RULES = build_rules()


def calculate_node_score(features, method="type2"):
    if method == "type1":
        results = evaluate_type1_rules(
            features, RULES
        )
        return defuzzify_type1(results)

    if method == "type2":
        results = evaluate_fuzzy_rules(
            features, RULES
        )
        return defuzzify_interval_type2(results)

    raise ValueError("Unknown routing method")


def select_best_node(wsn, method="type2"):
    alive_nodes = np.where(wsn.alive)[0]

    if len(alive_nodes) == 0:
        return None

    best_node = None
    best_score = -float("inf")

    for node_id in alive_nodes:
        features = wsn.get_node_features(
            int(node_id)
        )

        score = calculate_node_score(
            features, method
        )

        if score > best_score:
            best_score = score
            best_node = int(node_id)

    return best_node