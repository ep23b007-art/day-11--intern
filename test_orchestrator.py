import asyncio
from app.agent.orchestrator import AgentOrchestrator

async def main():
    orch = AgentOrchestrator()
    result = await orch.handle_message(
        session_id="test-123",
        user_message="I want a 5 day trip to Bali",
        history=[],
    )
    print(result)

if __name__ == "__main__":          # ← add this check
    asyncio.run(main())