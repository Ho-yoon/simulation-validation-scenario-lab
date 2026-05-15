# Simulation & Validation Scenario Lab

## 1. One-line Summary
Scenario-based AV validation with CARLA and Gazebo — covering collision, lane invasion, comfort, and closed-loop evaluation.

## 2. What This Proves
- CARLA simulator integration with ROS2
- Scenario design using YAML and SCENIC 3
- Closed-loop evaluation in simulation
- ODD (Operational Design Domain) definition
- Regression testing with rosbag replay
- Safety validation metrics (TTC, collision rate, route completion)
- Multi-weather and multi-lighting scenario generation

## 3. Validation Scenarios

| Scenario          | ODD Condition  | Key Risk           |
|-------------------|----------------|--------------------|
| cut_in            | Highway, dry   | Side collision     |
| pedestrian_cross  | Urban, dry     | Pedestrian contact |
| left_turn_unprotected | Intersection | Cross traffic   |
| occluded_vehicle  | Urban          | Hidden object      |
| rain_low_visibility | Rain, night  | Perception failure |

## 4. Metrics

| Metric                | Unit    | Description                         |
|-----------------------|---------|-------------------------------------|
| collision_rate        | %       | Fraction of runs with any collision |
| near_miss             | count   | TTC < 1.0 s events                  |
| time_to_collision     | s       | Min TTC during run                  |
| route_completion      | %       | Distance covered / planned          |
| lane_invasion         | count   | Lane boundary crossings             |
| jerk_rms              | m/s³    | Comfort metric                      |
| planning_latency_p95  | ms      | 95th percentile planning time       |

## 5. How to Run

```bash
# Start CARLA server (Docker)
docker run -p 2000-2002:2000-2002 carlasim/carla:0.9.15

# Run scenario
python3 carla/scripts/run_scenario.py \
  --scenario carla/scenarios/cut_in.yaml \
  --host localhost \
  --output-dir results/

# Generate scenario report
python3 reports/scenario_report_template.md

# Regression test (rosbag replay)
python3 tests/test_regression_replay.py --bag data/cutIn_2025-01-01.mcap
```

## 6. Design Decisions
- YAML scenario files for reproducibility and parametric variation
- All runs recorded to rosbag for offline analysis
- Metrics computed post-hoc from rosbag (not real-time) for reproducibility
- SCENIC scenarios used for probabilistic scenario sampling

## 7. Failure Cases
- CARLA physics inconsistency at >70 km/h on rough terrain
- Pedestrian AI gets stuck in narrow passages
- Rain particle system does not affect camera exposure in CARLA 0.9.x

## 8. Limitations
- Sim-to-real gap: CARLA physics not validated against real vehicle dynamics
- No HD map integration (uses CARLA built-in maps)
- Isaac Sim integration is notes-only (not implemented in this branch)
