"""CarrotQuest utility functions for support agent flow."""

from src.mcp_clients.carrot_quest.client import CarrotQuestClient


def set_typing_status(cq_client: CarrotQuestClient, conversation_id: str) -> None:
    """Set typing status in CarrotQuest."""
    cq_client.set_typing(conversation_id)


def get_similar_messages_by_tag(cq_client: CarrotQuestClient, message: str):
    """Get similar messages by tag from CarrotQuest."""
    return cq_client.get_similar_by_tag(message)
