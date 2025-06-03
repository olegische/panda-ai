"""Dreamer: Main orchestrator for LLM-driven agentic task execution."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from src.dreamer.pocketflow.runtime import DreamerRuntime
from src.dreamer.reasoning_cache import ReasoningCache
from src.llm.assistant_client import AssistantClient
from src.mcp.client import MCPClient


class Dreamer:
    """Dreamer is the core orchestrator for LLM-driven, dynamic agentic flows.

    It receives user tasks, plans the agent graph, executes it, and returns results.
    """

    def __init__(
        self,
        llm_client: AssistantClient,
        flow_runtime: DreamerRuntime,
        cache: ReasoningCache,
        mcp: MCPClient,
    ):
        """Initialize Dreamer with all core subsystems.

        Args:
            llm_client: Client for interacting with the OpenAI Assistant API
            flow_runtime: Runtime for executing PocketFlow agent graphs
            cache: Cache for storing reasoning steps and results
            mcp: MCP client for accessing external tools and resources
        """
        self.llm_client = llm_client
        self.flow_runtime = flow_runtime
        self.cache = cache
        self.mcp = mcp
        self.user_threads = {}  # Map user_id to thread_id
        self.user_plans = {}  # Map user_id to plan
        self.user_contexts = {}  # Map user_id to conversation context
        self.logger = logging.getLogger(__name__)

    async def handle_message(
        self, user_id: str, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Entry point for handling a user message.

        This method determines the appropriate action based on the message content
        and user context, then orchestrates the response generation.

        Args:
            user_id: Unique identifier for the user
            message: User's message
            context: Optional context information

        Returns:
            Response to the user
        """
        # Initialize or retrieve user context
        user_context = self._get_or_create_user_context(user_id, context)

        # Update context with the new message
        user_context["messages"].append({"role": "user", "content": message})

        # Determine intent and appropriate action
        intent, confidence = await self._determine_intent(
            user_id, message, user_context
        )

        self.logger.info(f"Determined intent: {intent} with confidence: {confidence}")

        # Handle based on intent
        if intent == "greeting":
            return await self._handle_greeting(user_id, message, user_context)
        elif intent == "task":
            return await self.submit_task(user_id, message, context)
        elif intent == "question":
            return await self._handle_question(user_id, message, user_context)
        elif intent == "clarification":
            return await self._handle_clarification(user_id, message, user_context)
        else:
            # Default to task handling if intent is unclear
            return await self.submit_task(user_id, message, context)

    async def _determine_intent(
        self, user_id: str, message: str, user_context: Dict[str, Any]
    ) -> Tuple[str, float]:
        """Determine the intent of the user's message.

        Args:
            user_id: Unique identifier for the user
            message: User's message
            user_context: User's conversation context

        Returns:
            Tuple of (intent_type, confidence_score)
        """
        # Create a thread for this user if it doesn't exist
        if user_id not in self.user_threads:
            thread_id = self.llm_client.create_thread()
            self.user_threads[user_id] = thread_id

        thread_id = self.user_threads[user_id]

        # Prepare the intent detection prompt
        intent_prompt = self._create_intent_prompt(message, user_context)

        # Send the intent detection prompt to the LLM
        self.llm_client.send_user_message(thread_id, intent_prompt)

        # Start a run and wait for completion
        run_id = self.llm_client.start_run(thread_id)
        await asyncio.to_thread(self.llm_client.poll_run_status, thread_id, run_id)

        # Get the intent from the LLM response
        intent_response = self.llm_client.get_final_result(thread_id)

        # Parse the intent
        try:
            intent_data = json.loads(intent_response)
            intent = intent_data.get("intent", "unknown")
            confidence = float(intent_data.get("confidence", 0.5))
            return intent, confidence
        except (json.JSONDecodeError, ValueError):
            self.logger.warning(
                f"Failed to parse intent from response: {intent_response}"
            )
            # Default to task with low confidence if parsing fails
            return "task", 0.3

    async def _handle_greeting(
        self, user_id: str, message: str, user_context: Dict[str, Any]
    ) -> str:
        """Handle a greeting message from the user.

        Args:
            user_id: Unique identifier for the user
            message: User's greeting message
            user_context: User's conversation context

        Returns:
            Greeting response
        """
        thread_id = self.user_threads.get(user_id)
        if not thread_id:
            return "Hello! How can I assist you today?"

        # Prepare the greeting prompt
        greeting_prompt = self._create_greeting_prompt(message, user_context)

        # Send the greeting prompt to the LLM
        self.llm_client.send_user_message(thread_id, greeting_prompt)

        # Start a run and wait for completion
        run_id = self.llm_client.start_run(thread_id)
        await asyncio.to_thread(self.llm_client.poll_run_status, thread_id, run_id)

        # Get the greeting response
        greeting_response = self.llm_client.get_final_result(thread_id)

        # Update user context with the response
        user_context["messages"].append(
            {"role": "assistant", "content": greeting_response}
        )

        return greeting_response

    async def _handle_question(
        self, user_id: str, message: str, user_context: Dict[str, Any]
    ) -> str:
        """Handle a question from the user.

        Args:
            user_id: Unique identifier for the user
            message: User's question
            user_context: User's conversation context

        Returns:
            Answer to the question
        """
        # For simple questions, we can use a direct LLM call
        # For complex questions, we might want to use a RAG flow

        thread_id = self.user_threads.get(user_id)
        if not thread_id:
            thread_id = self.llm_client.create_thread()
            self.user_threads[user_id] = thread_id

        # Send the question directly to the LLM
        self.llm_client.send_user_message(thread_id, message)

        # Start a run and wait for completion
        run_id = self.llm_client.start_run(thread_id)
        await asyncio.to_thread(self.llm_client.poll_run_status, thread_id, run_id)

        # Get the answer
        answer = self.llm_client.get_final_result(thread_id)

        # Update user context with the response
        user_context["messages"].append({"role": "assistant", "content": answer})

        return answer

    async def _handle_clarification(
        self, user_id: str, message: str, user_context: Dict[str, Any]
    ) -> str:
        """Handle a clarification request from the user.

        Args:
            user_id: Unique identifier for the user
            message: User's clarification message
            user_context: User's conversation context

        Returns:
            Clarification response
        """
        thread_id = self.user_threads.get(user_id)
        if not thread_id:
            return "I'm not sure what you're asking for clarification about. Could you provide more details?"

        # Prepare the clarification prompt
        clarification_prompt = self._create_clarification_prompt(message, user_context)

        # Send the clarification prompt to the LLM
        self.llm_client.send_user_message(thread_id, clarification_prompt)

        # Start a run and wait for completion
        run_id = self.llm_client.start_run(thread_id)
        await asyncio.to_thread(self.llm_client.poll_run_status, thread_id, run_id)

        # Get the clarification response
        clarification_response = self.llm_client.get_final_result(thread_id)

        # Update user context with the response
        user_context["messages"].append(
            {"role": "assistant", "content": clarification_response}
        )

        return clarification_response

    async def submit_task(
        self, user_id: str, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process a task-oriented message from the user.

        Plans, executes, and returns the final result.

        Args:
            user_id: Unique identifier for the user
            message: User's task message
            context: Optional context information

        Returns:
            Final result of the task execution
        """
        # Get or create user context
        user_context = self._get_or_create_user_context(user_id, context)

        # Plan the agent graph
        plan = await self.plan(user_id, message, user_context)

        # Build the flow based on the plan
        await self.build_flow(plan)

        # Execute the flow
        results = await self.run_flow(user_id)

        # Aggregate results
        final_result = await self.aggregate(user_id, results)

        # Log the final result
        await self.log(user_id, {"type": "final_result", "result": final_result})

        # Update user context with the response
        user_context["messages"].append({"role": "assistant", "content": final_result})

        return final_result

    async def plan(
        self, user_id: str, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Uses the LLM to plan the agent graph (nodes, dependencies, subagents).

        Args:
            user_id: Unique identifier for the user
            message: User's task message
            context: Optional context information

        Returns:
            Plan specification with root agent information
        """
        # Create a thread for this user if it doesn't exist
        if user_id not in self.user_threads:
            thread_id = self.llm_client.create_thread()
            self.user_threads[user_id] = thread_id

        thread_id = self.user_threads[user_id]

        # Prepare the planning prompt
        planning_prompt = self._create_planning_prompt(message, context)

        # Send the planning prompt to the LLM
        self.llm_client.send_user_message(thread_id, planning_prompt)

        # Start a run and wait for completion
        run_id = self.llm_client.start_run(thread_id)
        await asyncio.to_thread(self.llm_client.poll_run_status, thread_id, run_id)

        # Get the plan from the LLM response
        plan_text = self.llm_client.get_final_result(thread_id)

        # Parse the plan
        plan = self._parse_plan(plan_text)

        # Store the plan for this user
        self.user_plans[user_id] = plan

        # Log the plan
        await self.log(user_id, {"type": "plan", "plan": plan})

        return plan

    async def build_flow(self, plan: Dict[str, Any]) -> None:
        """Constructs the PocketFlow agent graph based on the LLM plan.

        Args:
            plan: Plan specification with root agent information
        """
        # Build the agent graph using the flow runtime
        await self.flow_runtime.build_graph(plan)

    async def run_flow(self, user_id: str) -> Dict[str, Any]:
        """Executes the agent graph, possibly in parallel.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary with results from all agents
        """
        # Prepare shared state with user context
        shared = {
            "user_id": user_id,
            "thread_id": self.user_threads.get(user_id),
            "plan": self.user_plans.get(user_id),
            "context": self.user_contexts.get(user_id, {}),
        }

        # Execute the flow
        results = await self.flow_runtime.run(shared)

        # Log the raw results
        await self.log(user_id, {"type": "raw_results", "results": results})

        return results

    async def aggregate(self, user_id: str, results: Dict[str, Any]) -> str:
        """Aggregates results from all agents/subagents into a final output.

        Args:
            user_id: Unique identifier for the user
            results: Dictionary with results from all agents

        Returns:
            Aggregated final result
        """
        # Get the thread for this user
        thread_id = self.user_threads.get(user_id)

        if not thread_id:
            return "Error: No thread found for this user."

        # Prepare the aggregation prompt
        aggregation_prompt = self._create_aggregation_prompt(results)

        # Send the aggregation prompt to the LLM
        self.llm_client.send_user_message(thread_id, aggregation_prompt)

        # Start a run and wait for completion
        run_id = self.llm_client.start_run(thread_id)
        await asyncio.to_thread(self.llm_client.poll_run_status, thread_id, run_id)

        # Get the aggregated result
        final_result = self.llm_client.get_final_result(thread_id)

        return final_result

    async def recover(self, user_id: str) -> None:
        """Handles recovery and resumption using the reasoning cache.

        Args:
            user_id: Unique identifier for the user
        """
        # Get the cached reasoning steps
        log_key = f"user:{user_id}:log"
        reasoning_steps = await self.cache.get_steps(log_key)

        if not reasoning_steps:
            self.logger.warning(f"No reasoning steps found for user {user_id}")
            return

        # Find the last completed step
        last_completed_step = None
        for step in reversed(reasoning_steps):
            if step.get("status") == "completed":
                last_completed_step = step
                break

        if not last_completed_step:
            self.logger.warning(f"No completed steps found for user {user_id}")
            return

        # Restore the state from the last completed step
        if "plan" in last_completed_step:
            self.user_plans[user_id] = last_completed_step["plan"]

        # Rebuild the flow if needed
        if self.user_plans.get(user_id):
            await self.build_flow(self.user_plans[user_id])

        self.logger.info(
            f"Recovered state for user {user_id} from step {last_completed_step.get('step_id')}"
        )

    async def log(self, user_id: str, entry: Dict[str, Any]) -> None:
        """Logs reasoning steps and decisions to the cache.

        Args:
            user_id: Unique identifier for the user
            entry: Dictionary with log entry information
        """
        # Create a log key for this user
        log_key = f"user:{user_id}:log"

        # Add the entry to the log
        await self.cache.log_step(log_key, entry)

    def _get_or_create_user_context(
        self, user_id: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get or create the context for a user.

        Args:
            user_id: Unique identifier for the user
            context: Optional context information to initialize with

        Returns:
            User context dictionary
        """
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {
                "messages": [],
                "last_intent": None,
                "last_task": None,
                "metadata": context or {},
            }

        # Update with new context if provided
        if context:
            self.user_contexts[user_id]["metadata"].update(context)

        return self.user_contexts[user_id]

    def _create_intent_prompt(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a prompt for determining the user's intent.

        Args:
            message: User's message
            context: Optional context information

        Returns:
            Intent detection prompt for the LLM
        """
        prompt = f"""
        # Intent Detection Request

        ## User Message
        {message}

        ## Instructions
        Please analyze this message and determine the user's intent.

        Possible intents:
        - greeting: A simple hello or greeting without a specific task
        - task: A request to perform a specific task or action
        - question: A request for information or an answer to a question
        - clarification: A request for clarification about a previous response

        Your response should be a JSON object with the following structure:
        ```json
        {{
            "intent": "intent_type",
            "confidence": 0.0-1.0,
            "reasoning": "brief explanation of why you chose this intent"
        }}
        ```
        """

        if context and "messages" in context and len(context["messages"]) > 0:
            # Add conversation history for context
            prompt += "\n\n## Conversation History\n"
            for i, msg in enumerate(context["messages"][-5:]):  # Last 5 messages
                prompt += f"{msg['role'].capitalize()}: {msg['content']}\n\n"

        return prompt

    def _create_greeting_prompt(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a prompt for responding to a greeting.

        Args:
            message: User's greeting message
            context: Optional context information

        Returns:
            Greeting prompt for the LLM
        """
        prompt = f"""
        # Greeting Response Request

        ## User Greeting
        {message}

        ## Instructions
        Please respond to this greeting in a friendly and helpful manner.
        If this is a new conversation, introduce yourself briefly.
        If there's conversation history, acknowledge it appropriately.

        Your response should be conversational but concise, and should encourage the user to share what they need help with.
        """

        if context and "messages" in context and len(context["messages"]) > 0:
            # Add conversation history for context
            prompt += "\n\n## Conversation History\n"
            for i, msg in enumerate(context["messages"][-5:]):  # Last 5 messages
                prompt += f"{msg['role'].capitalize()}: {msg['content']}\n\n"

        return prompt

    def _create_clarification_prompt(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a prompt for responding to a clarification request.

        Args:
            message: User's clarification message
            context: Optional context information

        Returns:
            Clarification prompt for the LLM
        """
        prompt = f"""
        # Clarification Response Request

        ## User Message
        {message}

        ## Instructions
        The user is asking for clarification or has provided additional information.
        Please respond appropriately, addressing their specific points.
        If they're confused, explain more clearly.
        If they've provided more details, acknowledge them and adjust your response accordingly.
        """

        if context and "messages" in context and len(context["messages"]) > 0:
            # Add conversation history for context
            prompt += "\n\n## Conversation History\n"
            for i, msg in enumerate(context["messages"][-5:]):  # Last 5 messages
                prompt += f"{msg['role'].capitalize()}: {msg['content']}\n\n"

        return prompt

    def _create_planning_prompt(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a prompt for planning the agent graph.

        Args:
            message: User's task message
            context: Optional context information

        Returns:
            Planning prompt for the LLM
        """
        prompt = f"""
        # Task Planning Request

        ## User Task
        {message}

        ## Available Tools
        - MCP Servers: {self.mcp.list_servers()}

        ## Instructions
        Please analyze this task and create a plan for solving it using a graph of agents.

        Your response should be a JSON object with the following structure:
        ```json
        {{
            "root_agent_id": "unique_id_for_root_agent",
            "root_task": "description_of_root_agent_task",
            "description": "overall_plan_description"
        }}
        ```

        The root agent will be created first and can spawn additional agents as needed.
        """

        if context:
            # Add conversation history if available
            if "messages" in context and len(context["messages"]) > 0:
                prompt += "\n\n## Conversation History\n"
                for i, msg in enumerate(context["messages"][-5:]):  # Last 5 messages
                    prompt += f"{msg['role'].capitalize()}: {msg['content']}\n\n"

            # Add other context information
            if "metadata" in context and context["metadata"]:
                prompt += f"\n\n## Additional Context\n{json.dumps(context['metadata'], indent=2)}"

        return prompt

    def _create_aggregation_prompt(self, results: Dict[str, Any]) -> str:
        """Create a prompt for aggregating results from all agents.

        Args:
            results: Dictionary with results from all agents

        Returns:
            Aggregation prompt for the LLM
        """
        prompt = f"""
        # Result Aggregation Request

        ## Agent Results
        {json.dumps(results, indent=2)}

        ## Instructions
        Please aggregate these results into a coherent final response for the user.
        Focus on providing a clear, concise answer that addresses the original task.
        """

        return prompt

    def _parse_plan(self, plan_text: str) -> Dict[str, Any]:
        """Parse the plan from the LLM response.

        Args:
            plan_text: LLM response containing the plan

        Returns:
            Parsed plan as a dictionary
        """
        # Extract JSON from the response
        try:
            # Look for JSON block in markdown
            if "```json" in plan_text and "```" in plan_text.split("```json")[1]:
                json_str = plan_text.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)

            # Try to parse the entire response as JSON
            return json.loads(plan_text)
        except (json.JSONDecodeError, IndexError):
            # If parsing fails, create a simple plan with the text as the task
            return {
                "root_agent_id": "root",
                "root_task": plan_text,
                "description": "Simple plan with a single agent",
            }
