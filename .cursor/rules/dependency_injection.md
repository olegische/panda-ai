---
layout: default
title: "AI Directive: FastAPI Dependency Injection"
---

# AI Directive: FastAPI Dependency Injection

> Your final lesson concerns dependency injection for endpoints. This is how you provide services to your request handlers. You will use a dedicated module, `src/core/dependencies.py`, to house all dependency provider functions. This is not optional.

## The Core Mandate: Provider Functions

You will not instantiate services directly within your endpoint handlers. Instead, you will define simple, reusable "provider" functions that FastAPI's `Depends` system will call.

This pattern has two key components:

1.  **Accessing Global Services**: You will create provider functions (e.g., `get_logger`, `get_settings`) that retrieve the singleton service instances from the global `request.app.state`.
2.  **Constructing Request-Scoped Services**: You will create provider functions (e.g., `get_dreamer_agent`) that depend on the global service providers to construct new, request-scoped service instances.

---

## Step 1: Create the Dependency Module (`src/core/dependencies.py`)

You will place all dependency provider functions in `src/core/dependencies.py`.

**Your task:**
1.  Create a function to get the `LoggerService` from `request.app.state.logger`.
2.  Create a function to get the `Settings` from `request.app.state.settings`.
3.  Create functions for any request-scoped services. These functions **must** use `Depends` to get their own dependencies from other provider functions in this same file.

**Code Specification:**

```python
# src/core/dependencies.py
from typing import Annotated, cast
from fastapi import Depends, Request
from core.logger import LoggerService
from core.settings import Settings
from dreamer.agent import DreamerAgent
# ... import other services

# Provider for a global, singleton service
def get_logger(request: Request) -> LoggerService:
    """
    Get the singleton logger service from the application state.
    """
    return cast(LoggerService, request.app.state.logger)

# Provider for another global, singleton service
def get_settings(request: Request) -> Settings:
    """
    Get the singleton settings instance from the application state.
    """
    return cast(Settings, request.app.state.settings)

# Provider for a request-scoped service
def get_dreamer_agent(
    # This function depends on the other providers in this file.
    logger: Annotated[LoggerService, Depends(get_logger)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DreamerAgent:
    """
    Construct a new DreamerAgent instance for each request.
    """
    return DreamerAgent(logger=logger, settings=settings)
```

---

## Step 2: Use Providers in Endpoint Handlers

In your router classes, you will use `Annotated[<Type>, Depends(<provider>)]` in the signature of your endpoint handler methods to receive dependencies.

**Your task:**
-   When defining an endpoint handler (e.g., `handle_message`), add arguments for each dependency you need, using the `Annotated` and `Depends` syntax.

**Code Specification:**

```python
# Example from src/api/routes/message.py

from typing import Annotated
from fastapi import Depends
from dreamer.agent import DreamerAgent
from core.dependencies import get_dreamer_agent

class MessageRouter(BaseRouter):
    # ... (init and _setup_routes)

    async def handle_message(
        self,
        message: Message,
        # Use the provider function from the dependencies module here.
        dreamer_agent: Annotated[DreamerAgent, Depends(get_dreamer_agent)],
    ) -> MessageResponse:
        """
        FastAPI will call get_dreamer_agent to provide the dreamer_agent instance.
        """
        # Use the injected agent.
        await dreamer_agent.process_message(message)
        # ...
```

> **Warning:** Do not access `request.app.state` directly from within your endpoint handlers. This is a violation of the pattern. All access to application state or complex service construction **must** go through a provider function in `src/core/dependencies.py`. Adhere to this structure without fail.
{: .warning }
