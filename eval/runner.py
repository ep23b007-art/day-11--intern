import json
import pathlib
import os

from dotenv import load_dotenv
from groq import Groq

from app.chatbot import chatbot

# -------------------------------
# Load API key
# -------------------------------
load_dotenv()

print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# -------------------------------
# Load Golden Test Cases
# -------------------------------
golden_cases = json.loads(
    pathlib.Path("eval/golden_cases.json").read_text(encoding="utf-8")
)

# -------------------------------
# Load Rubric
# -------------------------------
rubric = pathlib.Path("eval/rubric.txt").read_text(encoding="utf-8")

results = []

# -------------------------------
# Evaluate Each Test Case
# -------------------------------
for case in golden_cases:

    query = case["query"]

    print(f"\nTesting: {query}")

    # Get chatbot response
    response = chatbot(query)

    # Create evaluation prompt
    prompt = f"""
{rubric}

User Query:
{query}

Assistant Response:
{response}
"""

    # Ask Groq to evaluate
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    text = completion.choices[0].message.content.strip()

    # Remove markdown if Groq returns JSON inside ```json
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    try:
        score = json.loads(text)
    except json.JSONDecodeError:
        print("Groq returned invalid JSON:")
        print(text)
        continue

    results.append({
        "query": query,
        "score": score["score"],
        "reason": score["reason"]
    })

# -------------------------------
# Calculate Average
# -------------------------------
if results:
    average = sum(r["score"] for r in results) / len(results)
    print("\nAverage Score:", average)
else:
    print("\nNo valid evaluation results.")

# -------------------------------
# Save Results
# -------------------------------
with open("eval/results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

print("Results saved to eval/results.json")