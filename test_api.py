"""Quick test script to verify the API works"""
import asyncio
import json
from backend.app.services.llm_agent import run_agent_workflow

async def test():
    print("Testing news verification...")
    print("-" * 50)
    
    # Test with simple text
    result = await run_agent_workflow(
        "text", 
        {"text": "Breaking: Scientists discover cure for common cold"}
    )
    
    print("Result:")
    print(json.dumps(result, indent=2))
    print("-" * 50)
    print(f"Verdict: {result.get('verdict')}")
    print(f"Confidence: {result.get('confidence')}%")
    print(f"Summary: {result.get('summary')}")
    
if __name__ == "__main__":
    asyncio.run(test())
