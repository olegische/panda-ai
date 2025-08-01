---
layout: default
title: "AI Directive: FastAPI API Routing"
---

# AI Directive: FastAPI API Routing

> You will now learn how to construct API routers. This is not a creative exercise. It is a rigid, class-based pattern that you will replicate exactly. Your goal is consistency, not novelty.

## The Core Mandate: Class-Based, Dependency-Injected Routers

Every set of related endpoints will be encapsulated within a dedicated router class. This is mandatory. This pattern involves two levels of dependency injection:

1.  **Constructor Injection**: You will pass router-wide dependencies (like `LoggerService` and `Settings`) into the router's `__init__` method. These are services that the entire router and all its endpoints will need.
2.  **Endpoint Injection**: You will use FastAPI's `Depends` system to inject request-scoped dependencies (like `DreamerAgent`) directly into the endpoint handler function.

---

## Step 1: Create a Base Class (`src/api/routes/base.py`)

To enforce a uniform structure, all routers must inherit from `BaseRouter`.

**Your task:**
1.  Create an abstract base class `BaseRouter` that inherits from `abc.ABC`.
2.  The `__init__` method must accept a `LoggerService` instance. It will initialize a FastAPI `APIRouter` and call a `_setup_routes` method.
3.  Define an abstract method `_setup_routes`. This forces all subclasses to implement their own route definitions.

**Code Specification:**

```python
# src/api/routes/base.py
from abc import ABC, abstractmethod
from fastapi import APIRouter
from core.logger import LoggerService

class BaseRouter(ABC):
    def __init__(
        self,
        logger: LoggerService,
        prefix: str = "",
        tags: list[str] | None = None,
    ):
        if not logger:
            raise ValueError("Logger service is required")
        self.logger = logger.get_logger(__name__)
        self.router = APIRouter(prefix=prefix, tags=tags or [])
        self._setup_routes()

    @abstractmethod
    def _setup_routes(self) -> None:
        """
        You will implement this method in every concrete router class.
        This is where you define all endpoints for the router.
        """
        pass
```

---

## Step 2: Create a Concrete Router (e.g., `src/api/routes/message.py`)

Now, you will implement a specific router that follows the `BaseRouter` contract.

**Your task:**
1.  Create a class (e.g., `MessageRouter`) that inherits from `BaseRouter`.
2.  The `__init__` method will call `super().__init__` and accept any additional dependencies it needs, such as `Settings`.
3.  You will implement the `_setup_routes` method. Inside this method, you will define all API endpoints using `self.router.add_api_route()` or decorators like `@self.router.post()`.
4.  Endpoint handler methods will use `fastapi.Depends` to receive their own dependencies.

**Code Specification:**

```python
# src/api/routes/message.py
from typing import Annotated
from fastapi import Depends, Request
from api.routes.base import BaseRouter
from core.dependencies import get_dreamer_agent # Endpoint-level dependency
from core.logger import LoggerService
from core.settings import Settings
from dreamer.agent import DreamerAgent

class MessageRouter(BaseRouter):
    def __init__(
        self,
        logger: LoggerService, # Constructor-injected dependency
        settings: Settings,    # Constructor-injected dependency
    ) -> None:
        super().__init__(logger=logger, tags=["message"])
        self.settings = settings

    def _setup_routes(self) -> None:
        """
        Define all endpoints here.
        """
        self.router.add_api_route(
            "/api/v1/message",
            self.handle_message,
            methods=["POST"],
            # ... other metadata
        )

    async def handle_message(
        self,
        message: Message,
        request: Request,
        # Endpoint-level dependency injection:
        dreamer_agent: Annotated[DreamerAgent, Depends(get_dreamer_agent)],
    ) -> MessageResponse:
        """
        Handle the incoming request.
        """
        # Your logic here. Use the injected dependencies.
        # await dreamer_agent.process_message(message)
        return MessageResponse(status="accepted")

```

> **Warning:** Do not create free-floating `APIRouter` objects in your route files. Every router **must** be encapsulated in a class that inherits from `BaseRouter`. This structure is mandatory for maintaining order and predictability in the codebase.
{: .warning }
