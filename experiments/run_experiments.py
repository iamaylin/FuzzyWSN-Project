
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.wsn_simulation import WSNSimulation
from src.routing import select_best_node

FAST_MODE = True
RESULTS_DIR = "results/fast" if FAST_MODE else "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

METHODS = ["random", "type1", "type2"]
NODE_COUNTS = [30]
SEEDS = [42, 43, 44]
ROUNDS = 100


def run_simulation(method, num_nodes, seed):
    wsn = WSNSimulation(
        num_nodes=num_nodes,
        area_size=400,
        initial_energy=0.02,
        seed=seed,
    )

    rng = np.random.default_rng(seed + 1000)

    history = []
    successful = 0
    attempted = 0

    fnd = None
    hnd = None
    lnd = None

    for round_number in range(1, ROUNDS + 1):
        alive = np.where(wsn.alive)[0]

        if len(alive) == 0:
            break

        if method == "random":
            selected = int(rng.choice(alive))
        else:
            selected = select_best_node(wsn, method)

        if selected is None:
            break

        result = wsn.step([selected])

        alive_count = result["alive_nodes"]

        if fnd is None and alive_count < num_nodes:
            fnd = round_number

        if hnd is None and alive_count <= num_nodes / 2:
            hnd = round_number

        if lnd is None and alive_count == 0:
            lnd = round_number

        attempted += 1
        successful += result["successful_transmissions"]

        history.append({
            "round": round_number,
            "alive_nodes": result["alive_nodes"],
            "total_energy": result["total_energy"],
            "pdr": successful / attempted,
        })

    return history


def main():
    rows = []
    histories = {}

    for num_nodes in NODE_COUNTS:
        for seed in SEEDS:
            for method in METHODS:
                print(
                    f"Running: {method}, "
                    f"nodes={num_nodes}, seed={seed}",
                    flush=True,
                )

                history = run_simulation(
                    method, num_nodes, seed
                )

                histories[(method, num_nodes, seed)] = history

                if not history:
                    continue

                final = history[-1]

                rows.append({
                    "method": method,
                    "nodes": num_nodes,
                    "seed": seed,
                    "rounds": final["round"],
                    "alive_nodes": final["alive_nodes"],
                    "total_energy": final["total_energy"],
                    "pdr": final["pdr"],

"fnd": next(
    (h["round"] for h in history
     if h["alive_nodes"] < num_nodes),
    None
),
"hnd": next(
    (h["round"] for h in history
     if h["alive_nodes"] <= num_nodes / 2),
    None
),
"lnd": next(
    (h["round"] for h in history
     if h["alive_nodes"] == 0),
    None
),

                })

    csv_path = os.path.join(
        RESULTS_DIR, "experiment_results.csv"
    )

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=[
                "method", "nodes", "seed",
                "rounds", "alive_nodes",
                "total_energy", "pdr", "fnd", "hnd", "lnd",
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    for metric, ylabel in [
        ("alive_nodes", "Alive Nodes"),
        ("total_energy", "Remaining Energy (J)"),
        ("pdr", "Successful / Attempted"),
    ]:
        plt.figure(figsize=(9, 5))

        for method in METHODS:
            values = []

            for nodes in NODE_COUNTS:
                subset = [
                    row[metric] for row in rows
                    if row["method"] == method
                    and row["nodes"] == nodes
                ]
                values.append(
                    np.mean(subset) if subset else np.nan
                )

            plt.plot(
                NODE_COUNTS, values,
                marker="o", label=method
            )

        plt.xlabel("Number of Nodes")
        plt.ylabel(ylabel)
        plt.title(f"Comparison: {metric}")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()

        plt.savefig(
            os.path.join(
                RESULTS_DIR, f"{metric}_comparison.png"
            ),
            dpi=200,
        )
        plt.close()

    print("\nExperiments completed.")
    print("Results saved in:", RESULTS_DIR)


if __name__ == "__main__":
    main()