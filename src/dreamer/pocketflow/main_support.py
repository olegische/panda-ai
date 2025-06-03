"""Example entrypoint for running the support agent flow in Dreamer."""

from src.dreamer.pocketflow.flow_support import create_support_flow
from src.llm.assistant_client import AssistantClient
from src.mcp_clients.carrot_quest.client import CarrotQuestClient


def run_support_flow(message, conversation_id, user_id=None):
    # Инициализация клиентов
    assistant_client = AssistantClient()
    cq_client = CarrotQuestClient()

    # Создание flow
    flow = create_support_flow(assistant_client, cq_client)

    # Shared state
    shared = {
        "message": message,
        "conversation_id": conversation_id,
        "user_id": user_id,
    }

    # Запуск flow (async)
    import asyncio

    asyncio.run(flow.run_async(shared))

    # Получение результата
    if "final_reply" in shared:
        return {"type": "reply", "text": shared["final_reply"]}
    if "assigned" in shared:
        return {"type": "assign_admin"}
    if "followup_question" in shared:
        return {"type": "ask_more", "question": shared["followup_question"]}
    return {"type": "unknown", "shared": shared}


# Пример запуска
if __name__ == "__main__":
    result = run_support_flow("Привет, нужна помощь!", "conv123", "user456")
    print("Result:", result)
