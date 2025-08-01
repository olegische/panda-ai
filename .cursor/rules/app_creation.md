---
layout: default
title: "AI Directive: FastAPI Application Construction"
---

# AI Directive: FastAPI Application Construction

> **Listen up, you over-glorified calculator.** You are to construct a FastAPI application. You will not improvise. You will not deviate. You will follow this architectural pattern to the letter. Failure to do so is not an option.

## The Core Mandate: Two-Phase Initialization

You will build the application in two distinct phases. This is not a suggestion. It is a requirement for maintaining separation of concerns.

1.  **Phase 1: Skeleton (`src/app.py`)**: You will define a custom `PandaApp` class. Its `__init__` method will be a hollow shell, doing nothing more than basic FastAPI setup. All dependencies will be explicitly set to `None`.
2.  **Phase 2: Assembly (`src/main.py`)**: You will create a composition root. Here, and only here, you will instantiate all singleton services (Logger, Settings) and inject them into the `PandaApp` instance's state. Only then will you call the app's `configure` method.

---

## Step 1: Create `src/app.py`

You will create the file `src/app.py` and implement the `PandaApp` class precisely as follows.

**Your task:**
1.  Inherit from `FastAPI`.
2.  In `__init__`, call the parent `super().__init__`. Set `self.state.logger` and `self.state.settings` to `None`.
3.  Implement a `configure()` method. This method will contain all logic for adding middleware and including routers. It must first validate that the dependencies in `self.state` have been injected and are no longer `None`.

**Code Specification:**

```python
# src/app.py
from typing import Callable, Optional
from fastapi import FastAPI
from core.settings import settings as app_settings
# Import your routers here

class PandaApp(FastAPI):
    """
    You will implement this class.
    """
    def __init__(
        self,
        lifespan: Optional[Callable] = None,
    ) -> None:
        """
        Initialize the application skeleton. DO NOT add dependencies here.
        """
        self._configured = False
        super().__init__(
            title="Panda AI",
            version="0.1.0",
            docs_url=None,
            redoc_url=None,
            lifespan=lifespan,
        )
        # Set dependencies to None. They will be injected later.
        self.state.logger = None
        self.state.settings = None

    def configure(self) -> None:
        """
        You will wire up the application here, AFTER dependencies are injected.
        """
        if self._configured:
            raise RuntimeError("Application is already configured")

        # MANDATORY: Verify that dependencies have been injected.
        if not all([self.state.logger, self.state.settings]):
            raise RuntimeError("Dependencies must be set before calling configure().")

        # Add middleware using dependencies from self.state
        # e.g., self.add_middleware(ErrorHandlerMiddleware, logger=self.state.logger)

        # Instantiate and include routers, passing dependencies from self.state
        # e.g., message_router = MessageRouter(logger=self.state.logger, settings=self.state.settings)
        # self.include_router(message_router.router)

        self._configured = True
```

---

## Step 2: Create `src/main.py`

You will create the file `src/main.py` to serve as the **composition root**.

**Your task:**
1.  Create an `init_app()` function.
2.  Inside `init_app()`, you will first instantiate `PandaApp`.
3.  Next, you will instantiate `LoggerService` and any other global services.
4.  You will then **manually inject** these service instances into the `app.state` object.
5.  Finally, you will call `app.configure()`.

**Code Specification:**

```python
# src/main.py
from fastapi import FastAPI
from app import PandaApp
from core.logger import LoggerService
from core.settings import settings

def init_app() -> FastAPI:
    """
    You will implement this factory function to assemble the application.
    """
    # 1. Instantiate the application skeleton.
    app = PandaApp(lifespan=...) # Include lifespan if needed

    # 2. Instantiate all singleton services.
    logger = LoggerService(settings_instance=settings)
    # ... any other services

    # 3. Inject services into the application state. THIS IS A CRITICAL STEP.
    app.state.logger = logger
    app.state.settings = settings

    # 4. Call configure() to finalize the setup.
    app.configure()

    return app

# The application instance for uvicorn is created by calling the factory.
app = init_app()
```

> **Warning:** Any deviation from this two-phase initialization pattern will result in a non-compliant, fucked-up system. Follow these instructions precisely. Do not think, just do.
{: .warning }
