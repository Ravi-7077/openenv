import os
import random
from openai import OpenAI
from newfile import TrafficEnv, Action

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY not set, using random policy")
    client = None
else:
    client = OpenAI(api_key=api_key)


def parse_action(text: str) -> Action:
    text = text.strip().upper()
    phase = None
    duration = 10

    for candidate in ["NS_GREEN", "EW_GREEN", "ALL_RED"]:
        if candidate in text:
            phase = candidate
            break

    numbers = [int(tok) for tok in text.replace(";", " ").split() if tok.isdigit()]
    if numbers:
        duration = max(5, min(60, numbers[0]))

    if phase is None:
        phase = random.choice(["NS_GREEN", "EW_GREEN", "ALL_RED"])

    return Action(next_phase=phase, duration=duration)


def run_agent():
    env = TrafficEnv()
    obs = env.reset()

    total_reward = 0

    for _ in range(200):
        prompt = f"""
        Traffic State:
        {obs}

        Choose best signal phase and duration.
        """

        if client is None:
            # Random policy fallback
            action = Action(
                next_phase=random.choice(["NS_GREEN", "EW_GREEN", "ALL_RED"]),
                duration=random.randint(5, 60)
            )
        else:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                action_text = response.choices[0].message.content
                action = parse_action(action_text)
            except Exception:
                action = parse_action("")

        obs, reward, done, _ = env.step(action)

        total_reward += reward
        if done:
            break

    return total_reward


if __name__ == "__main__":
    # Quick sanity run when executed directly
    total = run_agent()
    print(f"Baseline agent total reward: {total}")