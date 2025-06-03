"""Support agent nodes for Dreamer PocketFlow architecture."""

from pocketflow import AsyncNode

from src.dreamer.pocketflow.utils_carrot import (
    get_similar_messages_by_tag,
    set_typing_status,
)
from src.llm.assistant_client import AssistantClient
from src.mcp_clients.carrot_quest.client import CarrotQuestClient


class SupportAgentNode(AsyncNode):
    """
    Support agent node: LLM (Assistant API) + CarrotQuest MCP.
    LLM возвращает action: 'reply', 'ask_more', 'assign_admin'.
    """

    def __init__(
        self, assistant_client: AssistantClient, cq_client: CarrotQuestClient, **kwargs
    ):
        super().__init__(**kwargs)
        self.assistant_client = assistant_client
        self.cq_client = cq_client

    async def prep_async(self, shared):
        # shared: message, conversation_id, user_id
        return {
            "message": shared["message"],
            "conversation_id": shared["conversation_id"],
            "user_id": shared.get("user_id"),
        }

    async def exec_async(self, prep_res):
        # 1. Поставить статус typing через MCP
        set_typing_status(self.cq_client, prep_res["conversation_id"])
        # 2. Получить похожие сообщения по тегу (пример)
        similar = get_similar_messages_by_tag(self.cq_client, prep_res["message"])
        # 3. Сформировать промпт для LLM
        prompt = (
            f"User message: {prep_res['message']}\n"
            f"Similar messages: {similar}\n"
            "Decide action: reply, ask_more, assign_admin. "
            'Return JSON: {"action": ..., "reply_text": ..., "question": ...}'
        )
        # 4. Вызвать LLM (Assistant API)
        llm_response = await self.assistant_client.acall(prompt)
        return llm_response

    async def post_async(self, shared, prep_res, exec_res):
        # Ожидается JSON: {"action": "...", ...}
        action = exec_res.get("action")
        shared["support_result"] = exec_res
        return action


class ReplyNode(AsyncNode):
    """Node для отправки ответа пользователю."""

    async def post_async(self, shared, prep_res, exec_res):
        reply = shared["support_result"].get("reply_text")
        # Здесь интеграция с CarrotQuest для отправки сообщения
        # self.cq_client.send_reply(...)
        shared["final_reply"] = reply
        return "done"


class AssignAdminNode(AsyncNode):
    """Node для эскалации в админку."""

    async def post_async(self, shared, prep_res, exec_res):
        # self.cq_client.assign_to_admin(...)
        shared["assigned"] = True
        return "done"


class AskMoreNode(AsyncNode):
    """Node для генерации дополнительного вопроса пользователю."""

    async def post_async(self, shared, prep_res, exec_res):
        question = shared["support_result"].get("question")
        # self.cq_client.send_reply(question)
        shared["followup_question"] = question
        return "done"
