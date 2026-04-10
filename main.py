from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

Position3D = Tuple[int, int, int]


@dataclass
class SimulationConfig:
    grid_shape: Tuple[int, int, int] = (30, 30, 30)
    resource_ratio: float = 0.08
    resource_regen_ratio: float = 0.001
    resource_energy_min: int = 1
    resource_energy_max: int = 6
    n_agents: int = 75
    initial_energy: float = 120.0
    sensing_range: int = 4
    move_cost: float = 1.5
    energy_efficiency: float = 1.25
    generations: int = 500
    seed: int = 42


class Grid:
    def __init__(
        self,
        shape: Tuple[int, int, int],
        resource_ratio: float = 0.10,
        resource_energy_min: int = 1,
        resource_energy_max: int = 6,
        seed: Optional[int] = None,
    ) -> None:
        if len(shape) != 3:
            raise ValueError("shape must be a 3D tuple")
        if not (0.0 <= resource_ratio <= 1.0):
            raise ValueError("resource_ratio must be within [0.0, 1.0]")
        if resource_energy_min < 1 or resource_energy_max < resource_energy_min:
            raise ValueError("resource energy bounds are invalid")

        self.shape = shape
        self.resource_ratio = resource_ratio
        self.resource_energy_min = resource_energy_min
        self.resource_energy_max = resource_energy_max
        self.rng = np.random.default_rng(seed)
        self.cells = np.zeros(shape, dtype=np.uint8)
        self._place_resources_exact_ratio()

    def _sample_resource_values(self, n: int) -> np.ndarray:
        return self.rng.integers(
            self.resource_energy_min,
            self.resource_energy_max + 1,
            size=n,
            dtype=np.uint8,
        )

    def _place_resources_exact_ratio(self) -> None:
        total_cells = int(np.prod(self.shape))
        resource_cells = int(round(total_cells * self.resource_ratio))

        if resource_cells == 0:
            return

        chosen_indices = self.rng.choice(total_cells, size=resource_cells, replace=False)
        flat = self.cells.reshape(-1)
        flat[chosen_indices] = self._sample_resource_values(resource_cells)

    def in_bounds(self, pos: Position3D) -> bool:
        x, y, z = pos
        sx, sy, sz = self.shape
        return 0 <= x < sx and 0 <= y < sy and 0 <= z < sz

    def get_cell(self, pos: Position3D) -> int:
        if not self.in_bounds(pos):
            raise IndexError("position out of bounds")
        x, y, z = pos
        return int(self.cells[x, y, z])

    def set_cell(self, pos: Position3D, value: int) -> None:
        if not self.in_bounds(pos):
            raise IndexError("position out of bounds")
        x, y, z = pos
        self.cells[x, y, z] = np.uint8(value)

    def has_resource(self, pos: Position3D) -> bool:
        return self.get_cell(pos) > 0

    def consume_resource(self, pos: Position3D) -> int:
        if self.has_resource(pos):
            energy = self.get_cell(pos)
            self.set_cell(pos, 0)
            return energy
        return 0

    def resource_count(self) -> int:
        return int(np.count_nonzero(self.cells))

    def spawn_resources(self, ratio: float) -> int:
        if not (0.0 <= ratio <= 1.0):
            raise ValueError("ratio must be within [0.0, 1.0]")

        total_cells = int(np.prod(self.shape))
        target_new = int(round(total_cells * ratio))
        if target_new <= 0:
            return 0

        flat = self.cells.reshape(-1)
        empty_indices = np.where(flat == 0)[0]
        if empty_indices.size == 0:
            return 0

        spawn_n = min(target_new, int(empty_indices.size))
        chosen_empty = self.rng.choice(empty_indices, size=spawn_n, replace=False)
        flat[chosen_empty] = self._sample_resource_values(spawn_n)
        return int(spawn_n)


@dataclass

class Agent:
    position: Position3D
    energy: float
    protocol: str
    sensing_range: int = 3
    energy_efficiency: float = 1.0
    age: int = 0
    alive: bool = True
    parent_id: Optional[int] = None
    id: Optional[int] = None

    def _distance(self, a: Position3D, b: Position3D) -> float:
        ax, ay, az = a
        bx, by, bz = b
        return float(np.sqrt((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2))

    def sense(self, grid: Grid) -> List[Tuple[float, Position3D]]:
        x, y, z = self.position
        r = self.sensing_range
        sx, sy, sz = grid.shape

        x0, x1 = max(0, x - r), min(sx - 1, x + r)
        y0, y1 = max(0, y - r), min(sy - 1, y + r)
        z0, z1 = max(0, z - r), min(sz - 1, z + r)

        local = grid.cells[x0 : x1 + 1, y0 : y1 + 1, z0 : z1 + 1]
        resource_offsets = np.argwhere(local > 0)

        found: List[Tuple[float, Position3D]] = []
        for ox, oy, oz in resource_offsets:
            pos = (x0 + int(ox), y0 + int(oy), z0 + int(oz))
            dist = self._distance(self.position, pos)
            if dist <= float(r):
                found.append((dist, pos))

        found.sort(key=lambda item: item[0])
        return found

    def grow(
        self,
        grid: Grid,
        sensed: Optional[List[Tuple[float, Position3D]]] = None,
        move_cost: float = 1.0,
    ) -> None:
        if not self.alive:
            return

        move_energy_cost = move_cost * self.energy_efficiency
        targets = sensed if sensed is not None else self.sense(grid)
        if not targets:
            self.energy -= move_energy_cost
            return

        _, target = targets[0]
        cx, cy, cz = self.position
        tx, ty, tz = target

        # Move exactly one step per axis toward the nearest resource.
        nx = cx + int(np.sign(tx - cx))
        ny = cy + int(np.sign(ty - cy))
        nz = cz + int(np.sign(tz - cz))

        nx = max(0, min(grid.shape[0] - 1, nx))
        ny = max(0, min(grid.shape[1] - 1, ny))
        nz = max(0, min(grid.shape[2] - 1, nz))

        self.position = (nx, ny, nz)
        self.energy -= move_energy_cost

        resource_energy = grid.consume_resource(self.position)
        if resource_energy > 0:
            self.energy += float(resource_energy)

    def replicate(self, rng: np.random.Generator, next_id: int, trait_bounds: dict, mutation_rate: float = 0.1) -> "Agent":
        # Mutate traits with small Gaussian noise, clamp to bounds
        sr_min, sr_max = trait_bounds["sensing_range"]
        ee_min, ee_max = trait_bounds["energy_efficiency"]
        new_sensing_range = np.clip(
            self.sensing_range + rng.normal(0, mutation_rate), sr_min, sr_max
        )
        new_energy_efficiency = np.clip(
            self.energy_efficiency + rng.normal(0, mutation_rate * 0.1), ee_min, ee_max
        )
        # Log mutation event if traits changed
        mutated = (
            abs(new_sensing_range - self.sensing_range) > 1e-6 or
            abs(new_energy_efficiency - self.energy_efficiency) > 1e-6
        )
        child = Agent(
            position=self.position,
            energy=self.energy,
            protocol=self.protocol,
            sensing_range=int(round(new_sensing_range)),
            energy_efficiency=float(new_energy_efficiency),
            age=0,
            alive=True,
            parent_id=self.id,
            id=next_id,
        )
        return child, mutated

    def step(self, grid: Grid) -> None:
        if not self.alive:
            return

        sensed = self.sense(grid)
        self.grow(grid, sensed=sensed)
        self.age += 1

        if self.energy < 50.0 or self.age > 1000:
            self.alive = False


class Simulation:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.grid = Grid(
            shape=config.grid_shape,
            resource_ratio=config.resource_ratio,
            resource_energy_min=config.resource_energy_min,
            resource_energy_max=config.resource_energy_max,
            seed=config.seed,
        )
        self.next_agent_id = 0
        self.agents = self._init_agents()
        self.metrics: List[dict] = []
        self.births: List[dict] = []
        self.deaths: List[dict] = []
        self.mutations: List[dict] = []
        self.trait_bounds = {
            "sensing_range": (1, 10),
            "energy_efficiency": (0.5, 2.0),
        }

    def _init_agents(self) -> List[Agent]:
        sx, sy, sz = self.config.grid_shape
        agents: List[Agent] = []
        for idx in range(self.config.n_agents):
            x = int(self.rng.integers(0, sx))
            y = int(self.rng.integers(0, sy))
            z = int(self.rng.integers(0, sz))
            agent = Agent(
                position=(x, y, z),
                energy=self.config.initial_energy,
                protocol=f"p{idx % 3}",
                sensing_range=self.config.sensing_range,
                energy_efficiency=self.config.energy_efficiency,
                id=self.next_agent_id,
            )
            self.next_agent_id += 1
            agents.append(agent)
        return agents

    def step(self, generation: int) -> None:
        # Phase 2: Replication, mutation, lineage, logging
        survivors = []
        new_births = []
        new_mutations = []
        deaths = []
        for agent in self.agents:
            agent.grow(
                self.grid,
                move_cost=self.config.move_cost,
            )
            agent.age += 1
            if agent.energy < 50.0 or agent.age > 1000:
                agent.alive = False
                deaths.append({
                    "id": agent.id,
                    "parent_id": agent.parent_id,
                    "age": agent.age,
                    "energy": agent.energy,
                    "generation": generation,
                })
            else:
                survivors.append(agent)

        # Replication: Each survivor can produce a child with some probability (or if energy is high)
        children = []
        for agent in survivors:
            if agent.energy > 150.0:  # Arbitrary threshold for reproduction
                child, mutated = agent.replicate(
                    self.rng, self.next_agent_id, self.trait_bounds, mutation_rate=0.5
                )
                self.next_agent_id += 1
                children.append(child)
                new_births.append({
                    "id": child.id,
                    "parent_id": agent.id,
                    "generation": generation,
                    "sensing_range": child.sensing_range,
                    "energy_efficiency": child.energy_efficiency,
                })
                if mutated:
                    new_mutations.append({
                        "child_id": child.id,
                        "parent_id": agent.id,
                        "generation": generation,
                        "old_sensing_range": agent.sensing_range,
                        "new_sensing_range": child.sensing_range,
                        "old_energy_efficiency": agent.energy_efficiency,
                        "new_energy_efficiency": child.energy_efficiency,
                    })
                # Reproduction cost
                agent.energy -= 40.0

        self.agents = survivors + children
        spawned = self.grid.spawn_resources(self.config.resource_regen_ratio)
        self.births.extend(new_births)
        self.deaths.extend(deaths)
        self.mutations.extend(new_mutations)
        self._log_metrics(generation=generation, spawned_resources=spawned)

    def _log_metrics(self, generation: int, spawned_resources: int) -> None:
        alive = len(self.agents)
        avg_energy = float(np.mean([agent.energy for agent in self.agents])) if alive else 0.0
        total_energy = float(np.sum([agent.energy for agent in self.agents])) if alive else 0.0
        sensing_ranges = [agent.sensing_range for agent in self.agents]
        energy_effs = [agent.energy_efficiency for agent in self.agents]
        mean_sr = float(np.mean(sensing_ranges)) if sensing_ranges else 0.0
        var_sr = float(np.var(sensing_ranges)) if sensing_ranges else 0.0
        mean_ee = float(np.mean(energy_effs)) if energy_effs else 0.0
        var_ee = float(np.var(energy_effs)) if energy_effs else 0.0

        self.metrics.append(
            {
                "generation": generation,
                "alive_agents": alive,
                "avg_energy": round(avg_energy, 4),
                "total_energy": round(total_energy, 4),
                "resource_cells": self.grid.resource_count(),
                "spawned_resources": spawned_resources,
                "mean_sensing_range": round(mean_sr, 4),
                "var_sensing_range": round(var_sr, 4),
                "mean_energy_efficiency": round(mean_ee, 4),
                "var_energy_efficiency": round(var_ee, 4),
            }
        )

    def run(self, generations: int) -> None:
        for generation in range(1, generations + 1):
            if not self.agents:
                self._log_metrics(generation=generation, spawned_resources=0)
                break
            self.step(generation=generation)

    def save_metrics(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(self.metrics, indent=2), encoding="utf-8")

    def save_logs(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "births.json").write_text(json.dumps(self.births, indent=2), encoding="utf-8")
        (output_dir / "deaths.json").write_text(json.dumps(self.deaths, indent=2), encoding="utf-8")
        (output_dir / "mutations.json").write_text(json.dumps(self.mutations, indent=2), encoding="utf-8")

    def save_checkpoint(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = {
            "config": {
                "grid_shape": list(self.config.grid_shape),
                "resource_ratio": self.config.resource_ratio,
                "resource_regen_ratio": self.config.resource_regen_ratio,
                "resource_energy_min": self.config.resource_energy_min,
                "resource_energy_max": self.config.resource_energy_max,
                "n_agents": self.config.n_agents,
                "initial_energy": self.config.initial_energy,
                "sensing_range": self.config.sensing_range,
                "move_cost": self.config.move_cost,
                "energy_efficiency": self.config.energy_efficiency,
                "generations": self.config.generations,
                "seed": self.config.seed,
            },
            "final_state": {
                "alive_agents": len(self.agents),
                "resource_cells": self.grid.resource_count(),
                "last_generation": self.metrics[-1]["generation"] if self.metrics else 0,
                "agents": [
                    {
                        "position": list(agent.position),
                        "energy": round(agent.energy, 4),
                        "age": agent.age,
                        "protocol": agent.protocol,
                    }
                    for agent in self.agents
                ],
            },
        }
        output_path.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")


# ----------------------
# Acceptance checks
# ----------------------

def _check_grid_spawns_with_10_percent_resources() -> None:
    grid = Grid(shape=(10, 10, 10), resource_ratio=0.10, seed=7)
    expected = int(round(10 * 10 * 10 * 0.10))
    actual = grid.resource_count()
    assert actual == expected, f"Expected {expected} resources, got {actual}"


def _check_agent_senses_resources_correctly() -> None:
    grid = Grid(shape=(5, 5, 5), resource_ratio=0.0, seed=1)
    grid.set_cell((2, 2, 2), 4)
    grid.set_cell((4, 4, 4), 2)

    agent = Agent(position=(1, 1, 1), energy=100.0, protocol="phase1", sensing_range=3)
    sensed = agent.sense(grid)
    sensed_positions = [pos for _, pos in sensed]

    assert (2, 2, 2) in sensed_positions, "Agent failed to sense near resource"
    assert (4, 4, 4) not in sensed_positions, "Agent sensed resource outside sensing range"


def _check_agent_moves_and_energy_decreases() -> None:
    grid = Grid(shape=(5, 5, 5), resource_ratio=0.0, seed=1)
    grid.set_cell((2, 2, 2), 1)

    agent = Agent(position=(1, 1, 1), energy=100.0, protocol="phase1", sensing_range=3)
    before_pos = agent.position
    before_energy = agent.energy

    agent.grow(grid, move_cost=2.0)

    assert agent.position != before_pos, "Agent did not move"
    assert agent.energy < before_energy, "Agent energy did not decrease"


def _check_resource_disappears_after_pickup() -> None:
    grid = Grid(shape=(5, 5, 5), resource_ratio=0.0, seed=1)
    grid.set_cell((2, 2, 2), 6)
    agent = Agent(position=(1, 1, 1), energy=100.0, protocol="phase1", sensing_range=3)

    before = grid.get_cell((2, 2, 2))
    agent.grow(grid, move_cost=1.0)
    after = grid.get_cell((2, 2, 2))

    assert before > 0, "Resource was not initialized"
    assert after == 0, "Resource was not consumed from the grid"


def run_phase1_acceptance_checks() -> None:
    _check_grid_spawns_with_10_percent_resources()
    _check_agent_senses_resources_correctly()
    _check_agent_moves_and_energy_decreases()
    _check_resource_disappears_after_pickup()
    print("Phase 1 acceptance checks passed")


def _check_simulation_runs_500_without_crash_and_population_stays_alive() -> None:
    cfg = SimulationConfig(generations=500, seed=7)
    simulation = Simulation(cfg)
    simulation.run(cfg.generations)

    assert simulation.metrics, "Simulation produced no metrics"
    assert simulation.metrics[-1]["generation"] == 500, "Simulation did not reach 500 generations"
    assert len(simulation.agents) > 0, "Population collapsed before generation 500"


def _check_metrics_log_is_written_json() -> None:
    cfg = SimulationConfig(generations=50, seed=11)
    simulation = Simulation(cfg)
    simulation.run(cfg.generations)

    out_path = Path("outputs") / "test_metrics.json"
    simulation.save_metrics(out_path)

    raw = out_path.read_text(encoding="utf-8")
    parsed = json.loads(raw)
    assert isinstance(parsed, list), "Metrics file is not a JSON list"
    assert parsed, "Metrics log is empty"


def run_full_acceptance_checks() -> None:
    run_phase1_acceptance_checks()
    _check_simulation_runs_500_without_crash_and_population_stays_alive()
    _check_metrics_log_is_written_json()
    print("Full acceptance checks passed")


def run_main() -> None:
    parser = argparse.ArgumentParser(description="mycelium-ML Day 1 mechanics run")
    parser.add_argument("--generations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resource-ratio", type=float, default=0.10)
    parser.add_argument("--resource-regen-ratio", type=float, default=0.002)
    parser.add_argument("--resource-energy-min", type=int, default=1)
    parser.add_argument("--resource-energy-max", type=int, default=6)
    parser.add_argument("--n-agents", type=int, default=75)
    parser.add_argument("--move-cost", type=float, default=1.5)
    parser.add_argument("--energy-efficiency", type=float, default=1.25)
    parser.add_argument("--output-dir", type=str, default="outputs")
    parser.add_argument("--acceptance-only", action="store_true")
    args = parser.parse_args()

    if args.acceptance_only:
        run_full_acceptance_checks()
        return

    config = SimulationConfig(
        generations=args.generations,
        seed=args.seed,
        resource_ratio=args.resource_ratio,
        resource_regen_ratio=args.resource_regen_ratio,
        resource_energy_min=args.resource_energy_min,
        resource_energy_max=args.resource_energy_max,
        n_agents=args.n_agents,
        move_cost=args.move_cost,
        energy_efficiency=args.energy_efficiency,
    )
    simulation = Simulation(config)
    simulation.run(config.generations)

    output_dir = Path(args.output_dir)
    metrics_path = output_dir / "metrics.json"
    checkpoint_path = output_dir / "checkpoint.json"

    simulation.save_metrics(metrics_path)
    simulation.save_checkpoint(checkpoint_path)
    simulation.save_logs(output_dir)

    print(
        f"Run complete: generations={config.generations}, "
        f"alive_agents={len(simulation.agents)}, "
        f"metrics={metrics_path}, checkpoint={checkpoint_path}, logs={output_dir}"
    )


if __name__ == "__main__":
    run_main()
