"""Compute collision rate and related safety metrics from scenario run results."""
import json
from dataclasses import dataclass
from pathlib import Path
import numpy as np


@dataclass
class ScenarioResult:
    name: str
    collision: bool
    collision_severity: float   # m/s delta-v at collision, 0 if none
    near_miss_count: int        # TTC < 1.0 s events
    min_ttc: float              # minimum time-to-collision [s]
    route_completion: float     # [0, 1]
    duration_s: float


def compute_ttc(ego_pos: np.ndarray, ego_vel: np.ndarray,
                obs_pos: np.ndarray, obs_vel: np.ndarray) -> float:
    """Time-to-collision for 2D pursuit model."""
    rel_pos = obs_pos - ego_pos
    rel_vel = ego_vel - obs_vel
    rel_speed = np.dot(rel_vel, rel_pos / (np.linalg.norm(rel_pos) + 1e-9))
    if rel_speed <= 0:
        return float('inf')
    return np.linalg.norm(rel_pos) / rel_speed


def collision_rate(results: list[ScenarioResult]) -> float:
    if not results:
        return 0.0
    return sum(1 for r in results if r.collision) / len(results)


def near_miss_rate(results: list[ScenarioResult]) -> float:
    if not results:
        return 0.0
    return sum(r.near_miss_count for r in results) / len(results)


def mean_route_completion(results: list[ScenarioResult]) -> float:
    if not results:
        return 0.0
    return np.mean([r.route_completion for r in results])


def generate_safety_report(results: list[ScenarioResult]) -> dict:
    report = {
        "n_runs": len(results),
        "collision_rate": collision_rate(results),
        "near_miss_per_run": near_miss_rate(results),
        "mean_route_completion": mean_route_completion(results),
        "min_ttc_across_runs": min(r.min_ttc for r in results) if results else float('inf'),
        "scenarios_with_collision": [r.name for r in results if r.collision],
    }
    return report


def load_results_from_json(path: str) -> list[ScenarioResult]:
    with open(path) as f:
        data = json.load(f)
    return [ScenarioResult(**entry) for entry in data]
