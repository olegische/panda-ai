"""Utility functions for OpenAI MCP agent."""

import openai


def call_llm(prompt: str) -> str:
    """Call OpenAI LLM (o4) with a prompt and return the response.

    Args:
        prompt: Prompt string for the LLM.

    Returns:
        LLM response as a string.
    """
    # Example using openai SDK (replace with MCP tool call if needed)
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.2,
    )
    return response["choices"][0]["message"]["content"]
