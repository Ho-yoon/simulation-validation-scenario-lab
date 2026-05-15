#!/usr/bin/env python3
"""Run a CARLA scenario from a YAML definition file."""
import argparse
import yaml
import time
import os
import sys
from pathlib import Path

try:
    import carla
    CARLA_AVAILABLE = True
except ImportError:
    CARLA_AVAILABLE = False
    print("[WARN] CARLA Python API not found. Running in dry-run mode.")


def load_scenario(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run_scenario(scenario: dict, host: str = "localhost", port: int = 2000,
                 output_dir: str = "results") -> dict:
    if not CARLA_AVAILABLE:
        print(f"[DRY-RUN] Would run scenario: {scenario.get('name')}")
        return {"success": False, "reason": "CARLA not available"}

    client = carla.Client(host, port)
    client.set_timeout(10.0)
    world = client.get_world()

    # Load map
    map_name = scenario.get("environment", {}).get("map", "Town04")
    if world.get_map().name.split("/")[-1] != map_name:
        client.load_world(map_name)
        world = client.get_world()
        time.sleep(2.0)

    # Set weather
    weather_name = scenario.get("environment", {}).get("weather", "ClearNoon")
    weather_preset = getattr(carla.WeatherParameters, weather_name, carla.WeatherParameters.ClearNoon)
    world.set_weather(weather_preset)

    blueprint_library = world.get_blueprint_library()
    spawn_points = world.get_map().get_spawn_points()
    actors = []

    try:
        # Spawn ego vehicle
        ego_cfg = scenario.get("ego", {})
        ego_bp = blueprint_library.find(ego_cfg.get("vehicle", "vehicle.tesla.model3"))
        spawn = ego_cfg.get("spawn", {})
        ego_transform = carla.Transform(
            carla.Location(x=spawn.get("x", 0), y=spawn.get("y", 0), z=spawn.get("z", 0.5)),
            carla.Rotation(yaw=spawn.get("yaw", 0))
        )
        ego = world.spawn_actor(ego_bp, ego_transform)
        actors.append(ego)
        print(f"[OK] Spawned ego: {ego_cfg.get('vehicle')}")

        # Record rosbag if enabled
        if scenario.get("record_bag"):
            os.makedirs(output_dir, exist_ok=True)
            bag_path = os.path.join(output_dir, f"{scenario['name']}.mcap")
            print(f"[INFO] Would record bag to: {bag_path}")

        # Simple timeout-based run
        duration = scenario.get("max_duration_s", 30)
        start = time.time()
        while time.time() - start < duration:
            world.tick()
            time.sleep(0.05)

        return {"success": True, "scenario": scenario.get("name")}

    finally:
        for actor in actors:
            actor.destroy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, help="Path to scenario YAML")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=2000)
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args()

    scenario = load_scenario(args.scenario)
    print(f"Running scenario: {scenario.get('name')}")
    result = run_scenario(scenario, args.host, args.port, args.output_dir)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
