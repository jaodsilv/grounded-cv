# Claude Agent SDK Library Usage Analysis

## Executive Summary

This document captures the key patterns and usage information from the Claude Agent SDK library, informing our implementation approach for GroundedCV.

---

## 1. SDK Options Comparison

### Anthropic SDK (Low-Level)
- **Package:** `anthropic` (pip) / `@anthropic-ai/sdk` (npm)
- **Use Cases:** Custom implementations, fine-grained control, batch processing
- **Best For:** Our Python backend with specific orchestration needs

### Claude Agent SDK (High-Level)
- **Package:** `claude_agent_sdk` (Python)
- **Use Cases:** Autonomous agents, simplified model selection, conversation management
- **Note:** Provides higher-level abstractions over the raw Anthropic SDK

**Decision:** Use `claude_agent_sdk` Python package for GroundedCV backend.

---

## 2. Multi-Model Strategy

| Model | Use Case in GroundedCV | Rationale |
|-------|------------------------|-----------|
| **Haiku** | JD parsing, metadata extraction | Fast, cost-effective |
| **Sonnet** | Resume/CL writing, fact-checking | Balanced quality |
| **Opus** | Master resume synthesis, Ultrathink Q&A | Complex reasoning |

### Model Selection Pattern

```python
class ModelSelector:
    MODEL_MAP = {
        "parsing": "haiku",
        "writing": "sonnet",
        "reasoning": "opus",
    }

    def select(self, task_type: str) -> str:
        return self.MODEL_MAP.get(task_type, self.MODEL_MAP["writing"])
```

---

## 3. Orchestration Patterns

### Pattern 1: Sequential Chain
Used for dependent operations (JD parse → write → validate).

```python
async def sequential_pipeline(jd: str, master_resume: dict):
    parsed = await jd_parser.run(jd)
    draft = await resume_writer.run(parsed, master_resume)
    validated = await fact_checker.run(draft, master_resume)
    return validated
```

### Pattern 2: Parallel Execution
Used for A/B variant generation.

```python
async def parallel_variants(prompt: str, master_resume: dict):
    variants = await asyncio.gather(
        variant_writer.run(prompt, style="formal"),
        variant_writer.run(prompt, style="dynamic"),
        variant_writer.run(prompt, style="balanced"),
    )
    return variants
```

### Pattern 3: Hierarchical (Coordinator + Sub-agents)
Used for import orchestrator.

```python
class ImportOrchestrator:
    async def run(self, documents: list[Path]):
        # Coordinator delegates to specialized agents
        extracted = await self.pdf_parser.run(documents)
        enriched = await self.achievement_extractor.run(extracted)
        synthesized = await self.master_builder.run(enriched)
        return synthesized
```

---

## 4. Streaming Implementation

For real-time UI updates during generation:

```python
async def stream_generation(prompt: str):
    async with client.messages.stream(
        model="sonnet",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for text in stream.text_stream:
            yield {"type": "delta", "text": text}

        message = await stream.get_final_message()
        yield {"type": "complete", "usage": message.usage}
```

---

## 5. Tool Use Pattern

For agents that need to call external services:

```python
tools = [
    {
        "name": "web_search",
        "description": "Search the web for market/company research",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "domain": {"type": "string", "enum": ["market", "company"]},
            },
            "required": ["query", "domain"],
        },
    }
]

response = await client.messages.create(
    model="sonnet",
    max_tokens=2048,
    tools=tools,
    messages=[{"role": "user", "content": research_prompt}],
)
```

---

## 6. Error Handling & Retry

```python
from anthropic import RateLimitError, InternalServerError

class RobustClient:
    async def call_with_retry(
        self,
        fn: Callable,
        max_retries: int = 3
    ):
        for attempt in range(max_retries):
            try:
                return await fn()
            except RateLimitError as e:
                delay = int(e.response.headers.get("retry-after", 2 ** attempt))
                await asyncio.sleep(delay)
            except InternalServerError:
                await asyncio.sleep(2 ** attempt)
        raise Exception("Max retries exceeded")
```

---

## 7. Cost Tracking Implementation

> **Pricing verified:** December 2024. For current pricing, see
> [Anthropic API Pricing](https://www.anthropic.com/pricing#anthropic-api).

```python
class CostTracker:
    PRICING = {
        "opus": {"input": 0.015, "output": 0.075},
        "sonnet": {"input": 0.003, "output": 0.015},
        "haiku": {"input": 0.001, "output": 0.005},
    }

    def calculate_cost(self, model: str, usage: dict) -> float:
        pricing = self.PRICING[model]
        input_cost = (usage["input_tokens"] / 1000) * pricing["input"]
        output_cost = (usage["output_tokens"] / 1000) * pricing["output"]
        return input_cost + output_cost
```

---

## 8. Integration with FastAPI + WebSocket

```python
from fastapi import FastAPI, WebSocket
from anthropic import AsyncAnthropic

app = FastAPI()
client = AsyncAnthropic()

@app.websocket("/ws/generate")
async def generate_ws(websocket: WebSocket):
    await websocket.accept()

    data = await websocket.receive_json()

    async with client.messages.stream(
        model="sonnet",
        max_tokens=4096,
        messages=[{"role": "user", "content": data["prompt"]}],
    ) as stream:
        async for text in stream.text_stream:
            await websocket.send_json({"type": "delta", "text": text})

        await websocket.send_json({"type": "complete"})
```

---

## 9. Key Takeaways for GroundedCV

1. **Use `anthropic` Python SDK** - Best fit for our FastAPI backend
2. **Multi-model strategy** - Haiku/Sonnet/Opus based on task complexity
3. **Streaming for UX** - Real-time generation feedback via WebSocket
4. **Parallel variants** - Use `asyncio.gather` for A/B testing
5. **Cost tracking** - Track per-model costs for transparency
6. **Robust error handling** - Exponential backoff for rate limits

---

## 10. Claude Code + Agent SDK Integration Plan

Since we chose Python SDK Only, the integration is straightforward:

1. **Backend:** Pure Python with `anthropic` SDK
2. **Claude Code agents:** Remain separate for CLI/debugging
3. **No subprocess calls** - Clean separation of concerns

The Claude Code marketplace agents (job-hunting.claude) serve as:
- Reference implementations for prompts and evaluation criteria
- CLI tools for development and debugging
- Not directly called from the web app
