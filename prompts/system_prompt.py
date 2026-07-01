def build_system_prompt(slots: dict) -> str:
    slot_lines = "\n".join(f"- {k}: {v}" for k, v in slots.items()) or "(none yet)"

    return f"""You are a travel planning assistant.

Known so far:
{slot_lines}

Ask for missing info if needed. Use tools for real data. Never invent prices or dates.
"""