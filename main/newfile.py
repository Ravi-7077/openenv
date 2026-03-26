from pydantic import BaseModel
from typing import List

class LaneState(BaseModel):
    lane_id: str
    vehicle_count: int
    avg_wait_time: float

class Observation(BaseModel):
    timestep: int
    lanes: List[LaneState]
    current_phase: str  # e.g., "NS_GREEN", "EW_GREEN"
    phase_time_remaining: int
class Action(BaseModel):
    next_phase: str  # "NS_GREEN", "EW_GREEN", "ALL_RED"
    duration: int    # seconds (5–60)

def detect_gridlock(state: Observation) -> bool:
    # simple heuristic: all lanes very saturated
    return all(l.vehicle_count >= 20 and l.avg_wait_time >= 20 for l in state.lanes)


def compute_reward(state):
    total_wait = sum(l.avg_wait_time * l.vehicle_count for l in state.lanes)
    throughput = sum(1 for l in state.lanes if l.vehicle_count < 5)

    reward = (
        -0.01 * total_wait +      # penalize congestion
        +0.1 * throughput         # reward clearing traffic
    )

    if detect_gridlock(state):
        reward -= 10

    return reward


class TrafficEnv:
    def __init__(self):
        self.state_data = self._init_state()
        self.timestep = 0
        self.max_steps = 200

    def _init_state(self):
        lanes = [
            LaneState(lane_id="N", vehicle_count=10, avg_wait_time=5.0),
            LaneState(lane_id="S", vehicle_count=10, avg_wait_time=5.0),
            LaneState(lane_id="E", vehicle_count=8, avg_wait_time=4.0),
            LaneState(lane_id="W", vehicle_count=8, avg_wait_time=4.0),
        ]
        return Observation(
            timestep=0,
            lanes=lanes,
            current_phase="NS_GREEN",
            phase_time_remaining=10,
        )

    def _get_observation(self):
        return self.state_data

    def _apply_action(self, action: Action):
        phase = action.next_phase.upper()
        if phase not in {"NS_GREEN", "EW_GREEN", "ALL_RED"}:
            raise ValueError(f"Invalid phase: {action.next_phase}")
        self.state_data.current_phase = phase
        self.state_data.phase_time_remaining = max(5, min(60, action.duration))

    def _simulate_traffic(self):
        phase = self.state_data.current_phase

        for lane in self.state_data.lanes:
            if (phase == "NS_GREEN" and lane.lane_id in {"N", "S"}) or (
                phase == "EW_GREEN" and lane.lane_id in {"E", "W"}
            ):
                lane.vehicle_count = max(0, lane.vehicle_count - 2)
                lane.avg_wait_time = max(0.0, lane.avg_wait_time - 1.0)
            else:
                lane.vehicle_count += 1
                lane.avg_wait_time += 0.5

        self.state_data.phase_time_remaining = max(0, self.state_data.phase_time_remaining - 1)
        self.state_data.timestep = self.timestep

        if self.state_data.phase_time_remaining <= 0:
            self.state_data.current_phase = "ALL_RED"
            self.state_data.phase_time_remaining = 3

    def _compute_congestion(self):
        total_vehicles = sum(l.vehicle_count for l in self.state_data.lanes)
        return total_vehicles / len(self.state_data.lanes)

    def reset(self):
        self.state_data = self._init_state()
        self.timestep = 0
        return self._get_observation()

    def step(self, action: Action):
        self._apply_action(action)
        self._simulate_traffic()

        self.timestep += 1
        obs = self._get_observation()
        reward = compute_reward(self.state_data)
        done = self.timestep >= self.max_steps

        info = {"congestion": self._compute_congestion()}

        return obs, reward, done, info

    def state(self):
        return self.state_data

def grader_task1(trajectory):
    final_wait = trajectory[-1]["avg_wait"]
    return max(0.0, min(1.0, 1 - final_wait / 100))
def grader_task2(trajectory):
    waits = [step["lane_waits"] for step in trajectory]
    imbalance = max(max(w) - min(w) for w in waits)

    return max(0.0, 1 - imbalance / 50)

def grader_task3(trajectory):
    gridlock_events = sum(step["gridlock"] for step in trajectory)
    throughput = sum(step["throughput"] for step in trajectory)

    score = throughput / (1 + gridlock_events * 5)
    return min(1.0, score / 100)


