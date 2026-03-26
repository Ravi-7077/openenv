import pytest
from newfile import TrafficEnv, Action, grader_task1

def test_reset():
    env = TrafficEnv()
    obs = env.reset()
    assert obs is not None

def test_step():
    env = TrafficEnv()
    env.reset()

    action = Action(next_phase="NS_GREEN", duration=20)
    obs, reward, done, _ = env.step(action)

    assert isinstance(reward, float)
    assert isinstance(done, bool)

def test_episode_end():
    env = TrafficEnv()
    env.reset()

    for _ in range(env.max_steps):
        obs, reward, done, _ = env.step(
            Action(next_phase="NS_GREEN", duration=10)
        )

    assert done is True
def test_task1_grader():
    trajectory = [
        {"avg_wait": 80},
        {"avg_wait": 50},
        {"avg_wait": 20},
    ]

    score = grader_task1(trajectory)

    assert 0 <= score <= 1
    assert score > 0.5  # should improve