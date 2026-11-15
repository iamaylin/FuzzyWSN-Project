
import numpy as np


class WSNSimulation:
    def __init__(
        self,
        num_nodes=100,
        area_size=400,
        initial_energy=1.0,
        seed=42
    ):
        self.num_nodes = num_nodes
        self.area_size = area_size
        self.initial_energy = initial_energy
        self.rng = np.random.default_rng(seed)

        self.sink = np.array([
            area_size / 2,
            area_size / 2
        ])

        self.positions = self.rng.uniform(
            0, area_size, size=(num_nodes, 2)
        )

        self.energy = np.full(
            num_nodes, initial_energy, dtype=float
        )

        self.alive = np.ones(
            num_nodes, dtype=bool
        )

        self.trust = self.rng.uniform(
            0.5, 1.0, size=num_nodes
        )

        self.round_number = 0

    def distance_to_sink(self):
        return np.linalg.norm(
            self.positions - self.sink,
            axis=1
        )

    def get_node_features(self, node_id):
        distance = self.distance_to_sink()[node_id]

        energy_cost = 1.0 - (
            self.energy[node_id] / self.initial_energy
        )

        delay = min(
            distance / (self.area_size * np.sqrt(2)),
            1.0
        )

        return {
            "energy": float(np.clip(energy_cost, 0, 1)),
            "delay": float(delay),
            "trust": float(self.trust[node_id])
        }



    def transmit(self, node_id):
        if not self.alive[node_id]:
            return False

        distance = self.distance_to_sink()[node_id]

        tx_cost = (
            0.001 + 0.00000002 * distance ** 2
        )

        self.energy[node_id] -= tx_cost

        if self.energy[node_id] <= 0:
            self.energy[node_id] = 0
            self.alive[node_id] = False
            return False

        # Simplified trust-based delivery probability
        return bool(
            self.rng.random() < self.trust[node_id]
        )

   
    def step(self, selected_nodes=None):
        if selected_nodes is None:
            selected_nodes = np.where(self.alive)[0]

        successful = 0

        for node_id in selected_nodes:
            if self.transmit(int(node_id)):
                successful += 1

        self.round_number += 1

        return {
            "round": self.round_number,
            "alive_nodes": int(np.sum(self.alive)),
            "total_energy": float(np.sum(self.energy)),
            "successful_transmissions": successful
        }
