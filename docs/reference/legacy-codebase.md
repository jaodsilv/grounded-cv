# Original ATS-Research App Analysis

## Executive Summary

This document captures the architecture and patterns from the original ats-research application at `D:\src\ats-research\main\src`.

---

## 1. Project Structure

```
src/
├── __init__.py
├── main.py                 # Entry point
├── config.py               # Configuration
├── merger_main.py          # Best practices merger entry
│
├── agents/                 # Agent implementations
│   ├── __init__.py
│   ├── base_agent.py       # BaseAgent class
│   ├── agent_pool.py       # Concurrent agent management
│   │
│   ├── input_prep/         # Input processing
│   │   ├── document_fetcher.py
│   │   ├── input_reader.py
│   │   └── jd_parser.py
│   │
│   ├── matching/           # JD-Resume matching
│   │   ├── resume_jd_matcher.py
│   │   └── jds_ranker_selector.py
│   │
│   ├── writing/            # Document generation
│   │   ├── draft_writer.py
│   │   ├── revised_draft_writer.py
│   │   ├── document_evaluator.py
│   │   ├── document_polisher.py
│   │   ├── fact_checker.py
│   │   ├── issue_fixer.py
│   │   ├── version_manager.py
│   │   ├── ai_written_detector.py
│   │   └── draft_humanizer.py
│   │
│   ├── pruning/            # Length optimization
│   │   ├── tex_template_filler.py
│   │   ├── tex_compiler.py
│   │   ├── text_impact_calculator.py
│   │   ├── rewriting_evaluator.py
│   │   ├── removal_evaluator.py
│   │   ├── delta_calculator.py
│   │   ├── changes_ranker.py
│   │   └── change_executor.py
│   │
│   └── research/           # Research agents
│       └── best_practices_merger.py
│
├── orchestrators/          # Orchestra implementations
│   ├── __init__.py
│   ├── base_orchestra.py
│   ├── tailoring_orchestra.py
│   ├── input_preparation_orchestra.py
│   ├── jd_matching_orchestra.py
│   ├── writing_polishing_orchestra.py
│   ├── resume_writing_polishing_orchestra.py
│   ├── cover_letter_writing_polishing_orchestra.py
│   ├── fact_checking_loop_orchestra.py
│   └── pruning_orchestra.py
│
├── state/                  # State management
│   ├── __init__.py
│   ├── run_context.py
│   └── state_manager.py
│
├── human/                  # Human interaction
│   ├── __init__.py
│   ├── wizard.py           # Interactive CLI wizard
│   └── feedback.py         # Human feedback collection
│
├── merger/                 # Best practices merger
│   ├── __init__.py
│   ├── merger_engine.py
│   ├── validators.py
│   └── prompts.py
│
└── utils/                  # Utilities
    ├── __init__.py
    └── logging.py
```

---

## 2. Key Patterns to Cherry-Pick

### 2.1 BaseAgent Pattern (`agents/base_agent.py`)

```python
class BaseAgent:
    def __init__(self, context: RunContext, config: Config):
        self.context = context
        self.config = config
        self.client = AsyncAnthropic()

    async def run(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    async def _call_claude(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.7,
    ) -> str:
        response = await self.client.messages.create(
            model=model or self.config.default_model,
            max_tokens=self.config.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
```

### 2.2 BaseOrchestra Pattern (`orchestrators/base_orchestra.py`)

```python
class BaseOrchestra:
    def __init__(self, context: RunContext, agent_pool: AgentPool):
        self.context = context
        self.agent_pool = agent_pool
        self.stage = OrchestrationStage.INITIALIZATION

    async def run(self) -> dict:
        try:
            self.context.start_stage(self.stage)
            result = await self.execute()
            self.context.complete_stage(self.stage, result)
            return result
        except Exception as e:
            self.context.fail_stage(self.stage, e)
            raise

    async def execute(self) -> dict:
        raise NotImplementedError
```

### 2.3 AgentPool Pattern (`agents/agent_pool.py`)

```python
class AgentPool:
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_agents: dict[str, BaseAgent] = {}

    async def execute(self, agent: BaseAgent, *args) -> Any:
        async with self.semaphore:
            self.active_agents[agent.name] = agent
            try:
                return await agent.run(*args)
            finally:
                del self.active_agents[agent.name]

    async def execute_parallel(
        self,
        agents: list[tuple[BaseAgent, tuple]]
    ) -> list[Any]:
        return await asyncio.gather(
            *[self.execute(agent, *args) for agent, args in agents]
        )
```

### 2.4 RunContext Pattern (`state/run_context.py`)

```python
class RunContext:
    def __init__(self, run_id: str, output_dir: Path):
        self.run_id = run_id
        self.output_dir = output_dir
        self.checkpoints: dict[str, Any] = {}
        self.current_stage: OrchestrationStage = None
        self.stage_history: list[StageRecord] = []

    def start_stage(self, stage: OrchestrationStage):
        self.current_stage = stage
        self.stage_history.append(StageRecord(
            stage=stage,
            started_at=datetime.now(),
        ))

    def complete_stage(self, stage: OrchestrationStage, result: Any):
        record = self._find_record(stage)
        record.completed_at = datetime.now()
        record.result = result
        self._save_checkpoint(stage, result)

    def _save_checkpoint(self, stage: OrchestrationStage, data: Any):
        checkpoint_path = self.output_dir / "checkpoints" / f"{stage.value}.json"
        checkpoint_path.write_text(json.dumps(data, indent=2))
```

### 2.5 Interactive Wizard Pattern (`human/wizard.py`)

```python
class InteractiveWizard:
    def __init__(self):
        self.console = Console()

    async def run(self) -> WizardResult:
        self.console.print(Panel("Welcome to Resume Tailoring"))

        job_urls = await self._collect_job_urls()
        file_paths = await self._collect_file_paths()
        config = await self._collect_config()

        self._display_summary(job_urls, file_paths, config)

        if await self._confirm():
            return WizardResult(
                job_urls=job_urls,
                file_paths=file_paths,
                config=config,
            )
        return None

    async def _collect_job_urls(self) -> list[str]:
        urls = []
        while True:
            url = Prompt.ask(f"Job URL #{len(urls)+1} (or 'done')")
            if url.lower() == 'done':
                break
            urls.append(url)
        return urls
```

---

## 3. Configuration Pattern (`config.py`)

```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    # API
    anthropic_api_key: str

    # Models
    default_model: str = "claude-sonnet-4-5-20250929"
    fast_model: str = "claude-3-5-haiku-20241022"
    reasoning_model: str = "claude-opus-4-5-20251101"

    # Limits
    max_tokens: int = 4096
    max_iterations: int = 10
    quality_threshold: float = 0.8
    agent_pool_size: int = 5

    # Paths
    data_dir: Path = Path("data")
    templates_dir: Path = Path("templates")

    class Config:
        env_file = ".env"
```

---

## 4. Output Structure

```
data/
└── runs/
    └── run-{uuid}/
        ├── logs/
        │   └── run-{uuid}.log
        ├── checkpoints/
        │   ├── initialization.json
        │   ├── input_preparation.json
        │   ├── jd_matching.json
        │   ├── writing_polishing.json
        │   ├── pruning.json
        │   └── completed.json
        ├── inputs/
        │   └── job_descriptions/
        │       └── jd-{id}.json
        ├── drafts/
        │   ├── resumes/
        │   │   ├── {jd_id}_v1.tex
        │   │   ├── {jd_id}_v2.tex
        │   │   └── {jd_id}_final.tex
        │   └── cover_letters/
        │       └── ...
        └── release/
            ├── {jd_id}_resume.pdf
            └── {jd_id}_cover_letter.pdf
```

---

## 5. Logging Pattern (`utils/logging.py`)

```python
import logging
from rich.logging import RichHandler

def setup_logging(run_id: str, log_dir: Path) -> logging.Logger:
    logger = logging.getLogger(f"grounded-cv.{run_id}")
    logger.setLevel(logging.DEBUG)

    # Console handler (Rich)
    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler(log_dir / f"run-{run_id}.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
```

---

## 6. What to Adopt vs. Modify

### Adopt As-Is
1. BaseAgent pattern - Clean abstraction
2. BaseOrchestra pattern - Good stage management
3. AgentPool pattern - Concurrency control
4. RunContext pattern - Checkpoint management
5. Config pattern - Pydantic settings

### Modify for GroundedCV
1. **Wizard** - Replace CLI with web UI
2. **Output structure** - Add variants/ for A/B testing
3. **Checkpoints** - Add WebSocket progress events
4. **Logging** - Add cost tracking per agent call

### Skip/Replace
1. **CLI entry point** - Use FastAPI instead
2. **merger_main.py** - Not needed for MVP
3. **Human feedback CLI** - Use web interface

---

## 7. Key Learnings

### 7.1 Orchestration Best Practices
- Use stages with clear boundaries
- Save checkpoints after each stage
- Allow resumption from any checkpoint
- Log all agent calls with timing

### 7.2 Agent Best Practices
- Single responsibility per agent
- Consistent input/output contracts
- Error handling with context
- Model selection per task complexity

### 7.3 State Management Best Practices
- Immutable state updates
- Versioned documents
- Rollback capability
- Progress persistence

---

## 8. Implementation Priority

For GroundedCV, implement in this order:

1. **Core Infrastructure**
   - Config, BaseAgent, BaseOrchestra, RunContext
   - FastAPI skeleton with WebSocket

2. **Import Pipeline**
   - DocumentParser, MasterResumeBuilder
   - Conversational Q&A

3. **Generation Pipeline**
   - JDParser, ResumeWriter, CoverLetterWriter
   - A/B variant generation

4. **Validation Pipeline**
   - FactChecker, ATSOptimizer, QualityEvaluator

5. **Output Pipeline**
   - LaTeXGenerator, PDFCompiler
   - CRUD operations
