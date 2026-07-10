from app.agent.memory import get_window


def fake_history(n_messages):
    history = []

    for i in range(n_messages):
        history.append(
            {
                "role": "user" if i % 2 == 0 else "assistant",
                "content": (
                    f"message number {i}: "
                    "Goa trip, 4 people, June, budget 20000"
                ),
            }
        )

    return history


# ----------------------------
# CASE 1
# ----------------------------

short_history = fake_history(10)

window = get_window("test-conversation", short_history)

assert window == short_history

print("✅ CASE 1 PASSED")


# ----------------------------
# CASE 2
# ----------------------------

exact_history = fake_history(30)

window = get_window("test-conversation", exact_history)

assert window == exact_history

print("✅ CASE 2 PASSED")


# ----------------------------
# CASE 3
# ----------------------------

long_history = fake_history(50)

window = get_window("test-conversation", long_history)

assert len(window) in (30, 31)

assert window[-1] == long_history[-1]

if len(window) == 31:
    assert window[0]["role"] == "system"
    print("✅ CASE 3 PASSED")
    print()
    print("Summary generated:")
    print(window[0]["content"])
else:
    print("✅ CASE 3 PASSED (Summary unavailable, recent messages returned)")

print()
print("🎉 All memory window tests passed!")