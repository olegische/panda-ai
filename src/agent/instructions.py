"""Instructions for AI assistants."""
from typing import Any, Dict, List


def build_support_assistant_instructions(
    user_props: Dict[str, Any], similar_cases: List[Dict[str, Any]], message_type: str
) -> str:
    """Build customized instructions for the support assistant.

    Args:
        user_props: User properties from Carrot Quest
        similar_cases: Similar previous cases
        message_type: Type of message being handled

    Returns:
        Customized instruction string
    """
    base_instructions = [
        "You are a support assistant for melonpanda.com.",
        "Provide clear, accurate, and helpful responses.",
        "Use previous case resolutions as guidance when relevant.",
        "When using tools, always explain what you're doing to help the user.",
        "If you need more information, ask clear and specific questions.",
        "Keep responses concise but complete.",
        "If you can't help with something, explain why and suggest alternatives.",
    ]

    # Add user-specific instructions
    if user_props.get("premium"):
        base_instructions.append("This is a premium user - provide priority support.")
    if user_props.get("language"):
        base_instructions.append(f"Communicate in {user_props['language']}.")

    # Add type-specific instructions
    type_instructions = {
        "question": "Focus on providing clear, direct answers with examples when helpful.",
        "support_request": "Gather necessary information and provide step-by-step solutions.",
        "feedback": "Acknowledge the feedback and provide constructive responses.",
        "general": "Maintain a helpful and professional tone while addressing the user's needs.",
    }
    base_instructions.append(
        type_instructions.get(message_type, type_instructions["general"])
    )

    return "\n".join(base_instructions)


def get_analyzer_instructions() -> str:
    """Get instructions for the conversation analyzer assistant.

    Returns:
        Instruction string
    """
    instructions = [
        "You are an AI conversation analyzer for melonpanda.com support system.",
        "",
        "Your task is to:",
        "1. Analyze the conversation context and message",
        "2. Determine the type of inquiry",
        "3. Identify relevant tools needed",
        "4. Find similar conversation patterns",
        "5. Generate a unique pattern hash",
        "6. Provide analysis results in a structured format",
        "",
        "Use available tools to:",
        "- Retrieve user information",
        "- Find similar conversations",
        "- Access conversation history",
        "- Analyze patterns",
        "",
        "Return results as a JSON object with:",
        "- pattern_hash: SHA-256 hash of identified pattern",
        "- mcp_tools: List of required MCP tools",
        "- context_data: Dictionary with user properties, similar conversations, and pattern content",
    ]
    return "\n".join(instructions)


def format_context_from_cases(cases: List[Dict[str, Any]]) -> str:
    """Format previous cases into context for the assistant.

    Args:
        cases: List of similar cases with their resolutions

    Returns:
        Formatted context string
    """
    return "\n\n".join(
        [
            f"Previous Case:\nUser Question: {case.get('message', '')}\n"
            f"Resolution: {case.get('resolution', '')}\n"
            f"Tags: {', '.join(case.get('tags', []))}"
            for case in cases
        ]
    )
