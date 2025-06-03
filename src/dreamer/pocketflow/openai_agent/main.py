"""Entrypoint for running the OpenAI MCP agentic flow (PocketFlow, MCP-style)."""

import sys

from src.dreamer.pocketflow.openai_agent.flow import create_openai_mcp_agent_flow

if __name__ == "__main__":
    # Default question
    default_question = "What is the best way to use OpenAI Assistant API via MCP?"

    # Get question from command line if provided with --
    question = default_question
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            question = arg[2:]
            break

    print(f"🤔 Processing question: {question}")

    # Create and run flow
    flow = create_openai_mcp_agent_flow()
    shared = {"question": question}
    flow.run(shared)

    # Print final result
    print("\n=== Final shared state ===")
    for k, v in shared.items():
        print(f"{k}: {v}")
