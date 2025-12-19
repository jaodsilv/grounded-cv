# New Agents, Commands, and Skills Design

## Executive Summary

This document captures the proposed agents, commands, output-styles, and skills for the GroundedCV system, synthesizing insights from the exploration phase.

---

## 1. Agent Categories

### 1.1 Import Phase Agents

| Agent | Purpose | Model | Input | Output |
|-------|---------|-------|-------|--------|
| `DocumentParser` | Extract text from PDFs | Haiku/Vision | PDF file | Structured text |
| `AchievementExtractor` | Extract STAR achievements | Sonnet | Raw text | STAR-formatted list |
| `MasterResumeBuilder` | Synthesize all sources | Opus | Documents + Profile | Master Resume YAML |
| `QAQuestionGenerator` | Identify gaps, generate questions | Opus | Master Resume draft | Question list |
| `QAResponseProcessor` | Integrate user answers | Sonnet | Answers + Draft | Updated Master Resume |

### 1.2 Research Phase Agents

| Agent | Purpose | Model | Input | Output |
|-------|---------|-------|-------|--------|
| `MarketResearcher` | Analyze job market trends | Sonnet | Role name | Market Report YAML |
| `CompanyResearcher` | Research company culture | Sonnet | Company name | Culture Report YAML |
| `TechStackAnalyzer` | Identify company technologies | Haiku | Company research | Tech list |
| `GapAnalyzer` | Compare skills to requirements | Sonnet | Master Resume + JD | Gap Report |

### 1.3 Generation Phase Agents

| Agent | Purpose | Model | Input | Output |
|-------|---------|-------|-------|--------|
| `JDParser` | Extract JD requirements | Haiku | Job description | Structured JD |
| `ResumeWriter` | Generate tailored resume | Sonnet | MR + JD + Research | Resume draft |
| `CoverLetterWriter` | Generate cover letter | Sonnet | MR + JD + Research | CL draft |
| `WhyCompanyWriter` | Generate "why this company" | Sonnet | Research + User input | Answer text |
| `VariantGenerator` | Create style variations | Sonnet | Base draft + Style | Styled variant |

### 1.4 Validation Phase Agents

| Agent | Purpose | Model | Input | Output |
|-------|---------|-------|-------|--------|
| `FactChecker` | Verify claims against MR | Sonnet | Draft + MR | Validation report |
| `ATSOptimizer` | Check ATS compatibility | Sonnet | Draft + JD | ATS score + fixes |
| `QualityEvaluator` | Multi-dimensional scoring | Sonnet | Draft | Quality report |
| `HallucinationDetector` | Find fabricated content | Sonnet | Draft + MR | Flag list |

### 1.5 Output Phase Agents

| Agent | Purpose | Model | Input | Output |
|-------|---------|-------|-------|--------|
| `LaTeXGenerator` | Fill templates | None | Content + Template | .tex file |
| `PDFCompiler` | Compile LaTeX | None | .tex file | .pdf file |
| `VersionManager` | Track document versions | None | Document | Version history |

---

## 2. Orchestrator Designs

### 2.1 ImportOrchestrator

```
┌─────────────────────────────────────────────────────────────────┐
│                      IMPORT ORCHESTRATOR                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Documents] → DocumentParser → [Text]                          │
│                     ↓                                            │
│  [Text] → AchievementExtractor → [STAR Items]                   │
│                     ↓                                            │
│  [All Sources] → MasterResumeBuilder → [Draft MR]               │
│                     ↓                                            │
│  [Draft MR] → QAQuestionGenerator → [Questions]                 │
│                     ↓                                            │
│  [User Answers] → QAResponseProcessor → [Final MR]              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 ResearchOrchestrator

```
┌─────────────────────────────────────────────────────────────────┐
│                     RESEARCH ORCHESTRATOR                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Request] → Check Cache                                        │
│       │                                                          │
│       ├── Cache Hit → Return Cached Report                      │
│       │                                                          │
│       └── Cache Miss → Run Research                             │
│                ↓                                                 │
│  [Role/Company] → MarketResearcher / CompanyResearcher          │
│                ↓                                                 │
│  [Research] → TechStackAnalyzer → [Tech Stack]                  │
│                ↓                                                 │
│  [All Data] → Cache & Return Report                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 GenerationOrchestrator

```
┌─────────────────────────────────────────────────────────────────┐
│                    GENERATION ORCHESTRATOR                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [JD] → JDParser → [Structured JD]                              │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 3 PARALLEL GENERATORS                      │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  ResumeWriter (Formal) ───────┐                           │  │
│  │  ResumeWriter (Dynamic) ──────┼──→ [3 Resume Variants]    │  │
│  │  ResumeWriter (Balanced) ─────┘                           │  │
│  │                                                            │  │
│  │  CoverLetterWriter (Formal) ──┐                           │  │
│  │  CoverLetterWriter (Dynamic) ─┼──→ [3 CL Variants]        │  │
│  │  CoverLetterWriter (Balanced) ┘                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [All Variants] → ValidationPipeline → [Scored Variants]        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 ValidationOrchestrator

```
┌─────────────────────────────────────────────────────────────────┐
│                   VALIDATION ORCHESTRATOR                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Draft] → FactChecker → [Fact Score + Issues]                  │
│       │                                                          │
│       ├─→ ATSOptimizer → [ATS Score + Fixes]                    │
│       │                                                          │
│       └─→ QualityEvaluator → [Quality Scores]                   │
│                                                                  │
│  [All Scores] → ScoreAggregator → [Final Score + Report]        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Slash Commands

### 3.1 /import
**Purpose:** Start document import process
```
Usage: /import [files...]
Example: /import resume.pdf review1.pdf review2.pdf
```

### 3.2 /research
**Purpose:** Request market or company research
```
Usage: /research <type> <name>
Example: /research company "Anthropic"
Example: /research market "Senior Software Engineer"
```

### 3.3 /generate
**Purpose:** Generate tailored application materials
```
Usage: /generate [options]
Options:
  --resume      Generate tailored resume
  --cover       Generate cover letter
  --why         Generate "why this company" answer
  --all         Generate all (default)
```

### 3.4 /validate
**Purpose:** Run validation on generated documents
```
Usage: /validate <document>
Example: /validate resume
```

### 3.5 /export
**Purpose:** Export to PDF
```
Usage: /export <document> [template]
Example: /export resume ats-optimized
```

---

## 4. Skills to Define

### 4.1 Resume Tailoring Skill

```markdown
# Resume Tailoring

## When to Invoke
- User asks to tailor resume
- User uploads job description
- User mentions job application

## Core Principles
1. **Truthfulness** - Only include verifiable claims
2. **Relevance** - Prioritize job-aligned content
3. **Impact** - Quantify achievements
4. **Brevity** - 1-2 pages maximum

## Tailoring Strategy
1. Extract JD requirements
2. Match to master resume content
3. Prioritize and reorder
4. Adjust language/tone
5. Validate claims
```

### 4.2 Cover Letter Writing Skill

```markdown
# Cover Letter Writing

## When to Invoke
- User asks for cover letter
- User mentions application submission

## Structure
1. Opening - Hook + position reference
2. Body 1 - Technical fit with examples
3. Body 2 - Cultural alignment
4. Closing - Call to action

## Quality Standards
- 250-400 words
- Company-specific content
- No resume repetition
- ATS-friendly format
```

### 4.3 Company Research Skill

```markdown
# Company Research

## When to Invoke
- New company in job application
- User asks about company culture
- Interview preparation

## Research Areas
1. Mission and values
2. Tech stack and methodologies
3. Employee sentiment
4. Recent news and developments
5. Interview patterns
```

---

## 5. Output Styles

### 5.1 Resume Output Style

```markdown
# Resume Output Style

## Format
- Single-column, ATS-friendly
- Standard fonts (Arial, Calibri)
- Clear section headings
- Bullet points for achievements

## Sections (Dynamic)
Only include sections with content:
- Summary (optional)
- Experience
- Skills
- Education
- Projects (if relevant)
- Certifications (if present)
```

### 5.2 Cover Letter Output Style

```markdown
# Cover Letter Output Style

## Format
- Professional business letter
- 3-4 paragraphs
- 250-400 words
- Standard fonts

## Tone
- Professional but personable
- Enthusiastic without being excessive
- Confident without arrogance
```

---

## 6. Agent Communication Patterns

### 6.1 Request/Response Format

```python
@dataclass
class AgentRequest:
    task_id: str
    input_data: dict
    context: dict
    options: dict

@dataclass
class AgentResponse:
    task_id: str
    status: str  # success, error, partial
    output_data: dict
    metadata: AgentMetadata
    errors: list[str]

@dataclass
class AgentMetadata:
    model_used: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    cost_usd: float
```

### 6.2 Event Streaming Format

```python
@dataclass
class AgentEvent:
    event_type: str  # start, progress, delta, complete, error
    agent_name: str
    task_id: str
    data: dict
    timestamp: datetime

# Events emitted:
# - agent_start: Agent begins processing
# - progress: Intermediate status update
# - delta: Streaming text chunk
# - complete: Agent finished successfully
# - error: Agent encountered error
```

---

## 7. Prompt Engineering Guidelines

### 7.1 System Prompt Structure

```
You are a [ROLE] specialized in [DOMAIN].

## Your Task
[Clear task description]

## Input Format
[Expected input structure]

## Output Format
[Required output structure]

## Constraints
1. [Constraint 1]
2. [Constraint 2]

## Quality Standards
[Quality criteria]

## Examples
[Optional examples]
```

### 7.2 Anti-Hallucination Prompt Pattern

```
CRITICAL: You must ONLY use information from the provided master resume.

For each claim you include:
1. Identify the source in the master resume
2. Quote the relevant text
3. Explain how you adapted it

If you cannot find a source for a claim, DO NOT include it.
Any fabricated content is unacceptable.
```

---

## 8. User Questions for Validation

**Questions asked and user responses captured in planning phase:**

1. **Integration:** Python SDK Only - Backend uses anthropic SDK exclusively
2. **Frontend:** React + TailwindCSS + Zustand
3. **A/B Testing:** 3 variants per generation
4. **Debug:** Full debugging (prompts, costs, step-by-step)
5. **Codebase:** Fresh start, cherry-pick patterns
6. **Doc Processing:** Hybrid (text + vision fallback)
7. **Q&A Style:** Conversational (one question at a time)
8. **Concurrency:** Parallel (3-5 jobs simultaneously)

All decisions documented and incorporated into system design.
