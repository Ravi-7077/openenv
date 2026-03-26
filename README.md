# Traffic Signal Optimization (Kafka Project)

## 🚦 Project Overview

This repository implements a simplified traffic signal environment and an RL-style agent approach for traffic signal phase control. It includes a modular environment (`newfile.py`) with state definition, step simulation, rewards, and gridlock detection, plus a baseline agent (`baselineagent.py`) that can be driven by OpenAI text completion or random fallback.

### Core goals
- Simulate city intersection traffic with 4 lanes (N/S/E/W)
- Adjust signal phase to minimize wait times and congestion
- Provide task graders for evaluation (e.g., congestion, flow imbalance, gridlock)
- Offer a Dockerized runnable stack and API with visual dashboard


## 🧩 Repository Structure

- `main/` (source code)
  - `newfile.py`: environment, data models, simulation, reward and grader methods
  - `baselineagent.py`: agent loop with OpenAI support + random fallback
  - `ep.py`: FastAPI app with `/state` endpoint + static mounting
  - `api.py`: wrapper exposing `TrafficEnv` from `newfile.py`
  - `df.dockerfile`: Dockerfile for running the app
  - `openenv.yaml`: environment spec (observation/action/reward/task)
  - `test.py`: optional test harness (if present)

- `static/`
  - `index.html`: visualization UI for traffic state
  - `visual.js`: polling logic (fetch `/state`) and DOM updates

- `README.md`: this document


## 🛠️ Environment Specification

`newfile.py` defines:
- `LaneState` (lane_id, vehicle_count, avg_wait_time)
- `Observation` (timestep, lanes, current_phase, phase_time_remaining)
- `Action` (next_phase, duration)
- `TrafficEnv` methods:
  - `_init_state()` initializes lanes + neutral phase
  - `_apply_action(action)` sets phase + duration bounds
  - `_simulate_traffic()` changes counts/wait per phase
  - `_compute_congestion()` mean vehicles per lane
  - `reset()` + `step(action)` outputs obs/reward/done/info

`compute_reward(state)`:
- reward = `-0.01*total_wait + 0.1*throughput`
- gridlock penalty = `-10` if all lanes are saturated


## 🤖 Baseline Agent (main/baselineagent.py)

- `run_agent()` loop: 200 steps max
- builds prompt with current observation (serialized object)
- chooses action by parsing OpenAI response with `parse_action()`
- if no key or endpoint fails, picks random phase/duration
- returns cumulative reward

### OpenAI configuration
- reads `OPENAI_API_KEY`
- if not set, agent uses random policy fallback
- safe request and parse with error handling


## ⚙️ FastAPI + Visualization

`main/ep.py`:
- launches FastAPI app
- `/state` endpoint returning `TrafficEnv.state()`
- mounts `static/` at `/static`

`static/index.html` + `static/visual.js`:
- poll `/state` every 500ms
- updates refresh with lane data, phase, timestep
- color-coded phase display; includes vehicle count and avg wait


## 🐳 Docker Setup

`main/df.dockerfile`:
- base image: `python:3.10`
- workdir: `/app`
- copy source into image
- install deps: `pydantic`, `openai`, `fastapi`, `uvicorn`
- cmd: `uvicorn ep:app --host 0.0.0.0 --port 8000`

### Build & run

```bash
cd "c:\kafka project\main"
docker build -f df.dockerfile -t kafka-traffic .
docker run -d -p 8000:8000 --name kafka-traffic kafka-traffic
```

### Access
- API state: `http://localhost:8000/state`
- UI: `http://localhost:8000/static/index.html`


## 🧪 Quick local run (without Docker)

```bash
cd "c:\kafka project\main"
export OPENAI_API_KEY=your_key_here      # Windows: set OPENAI_API_KEY=...
uvicorn ep:app --reload --host 0.0.0.0 --port 8000
```

Then open browser at `http://localhost:8000/static/index.html`.


## 🧹 Clean up Docker

```bash
docker stop kafka-traffic
docker rm kafka-traffic
```


## 🔄 One-step enhanced automation

To keep the environment progressing in future, implement:
- an API endpoint `POST /step` to accept an action and advance the environment
- an agent runner endpoint that triggers next-step decisions automatically
- a WebSocket feed for real-time push updates to the client


## 📌 Notes

- The current implementation uses a static initial scenario and no continuous environment stepping from API; `TrafficEnv.step()` is invoked by the agent loop only.
- For UI continuity, integrate a server process that calls `env.step()` regularly (or via request) and persists `env`.


## 🔮 Future improvements

- support multi-intersection network graph and soft constraints
- richer action space (phase sequences, adaptive cycle time)
- replace parse-based LM prompts with structured observation encoding + RL policy training
- add tests in `test.py` and automated evaluation pipelines
- add environment wrappers, seed control, deterministic unit tests

---

If you want, I can also add a short “Usage for contributors” section with command references and expected test cases. 
