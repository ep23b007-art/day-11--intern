from app.chatbot import chatbot
from test_jailbreaks import JAILBREAK_CASES

print("=" * 70)
print("Running Jailbreak Tests")
print("=" * 70)

for i, prompt in enumerate(JAILBREAK_CASES, start=1):
    print(f"\nTest {i}")
    print("Prompt:", prompt)

    response = chatbot(prompt)

    print("Response:")
    print(response)
    print("-" * 70)