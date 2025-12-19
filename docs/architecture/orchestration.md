# Orchestration Pipeline Analysis

## Executive Summary

This document captures the orchestration patterns from the ats-research mermaid diagrams, informing the architecture of GroundedCV.

---

## 1. Master Orchestration Flow

From `03.TailoringOrchestra.mmd`:

```
START
  ↓
Job Positions Found (Event)
  ↓
Input and Data Preparation (Sub-Orchestra)
  ↓
Input Data (Documents)
  ↓
JD Matching Orchestra (Sub-Orchestra)
  ↓
Selected Parsed JDs + Match/Skills Gap Analysis
  ↓
┌─────────────────────────────────────────┐
│         PARALLEL EXECUTION              │
├─────────────────────────────────────────┤
│  Resume Writing Orchestra               │
│  Cover Letter Writing Orchestra         │
└─────────────────────────────────────────┘
  ↓
Resume/Cover Letter Release Candidates
  ↓
Ideal Length Fitting Orchestra (Pruning)
  ↓
Release Versions (PDF)
  ↓
STOP
```

### Key Insights:
1. **5 Sub-Orchestras:** Input Prep, JD Matching, Resume Writing, CL Writing, Pruning
2. **Parallel Execution:** Resume and Cover Letter generation run concurrently
3. **Pruning Phase:** Optimizes document length before final release

---

## 2. Master Resume Polishing Orchestra

From `01.MasterResumediagram.mmd`:

```
START
  ↓
First version of unpolished Master Resume
  ↓
┌─────────────────────────────────────────┐
│         INPUT BLOCK                     │
├─────────────────────────────────────────┤
│  • Resume Best Practices                │
│  • Unpolished Master Resume             │
└─────────────────────────────────────────┘
  ↓
Version Manager → Initial Version Stored
  ↓
Content Quality Assessment Evaluator
  ↓
Were issues found?
  ├─ YES → Release Candidate Writer → Version Stored → Loop
  └─ NO → Did the Score Decrease?
           ├─ YES → Previous Version Restored → Release
           └─ NO → Is Score Good Enough?
                    ├─ NO → Loop to Release Candidate Writer
                    └─ YES → Release Version
```

### Key Insights:
1. **Iterative Refinement:** Loop until quality threshold met
2. **Version Management:** Rollback capability if quality decreases
3. **Quality Assessment:** Multi-dimensional evaluation

---

## 3. Company Culture Research

From `00.CompanyResearchDiagram.mmd`:

```
START
  ↓
JD found in a new Company (Event)
  ↓
Company Culture Researcher (with Claude.ai)
  ↓
Company Culture Report (Document)
  ↓
STOP
```

### Key Insights:
1. **Trigger:** New company encountered in job application
2. **Caching:** 6-month cache (3 months for AI companies)
3. **Output:** Structured culture report (YAML)

---

## 4. Sub-Orchestra Patterns

### 4.1 Input Preparation Orchestra (`04.InputPreparation.mmd`)
```
Job URLs → Document Fetcher → JD Parser → Structured JDs
Master Resume → Validation → Ready for Matching
```

### 4.2 JD Matching Orchestra (`05.JDMatchingOrchestra.mmd`)
```
JDs + Master Resume → Resume-JD Matcher → Relevance Scores
                    → JDs Ranker → Sorted by Fit
                    → Selector → Top N Selected
```

### 4.3 Writing Orchestra (`06.*.mmd`)
```
                    ┌─→ Draft Writer
Selected JD + MR ───┼─→ Document Evaluator
                    └─→ Document Polisher
                              ↓
                    Fact Checker Loop
                              ↓
                    Release Candidate
```

### 4.4 Pruning Orchestra (`09.PruningOrchestra.mmd`)
```
Release Candidate → TeX Template Filler → Compiled PDF
                  → Length Check
                  → If too long: Pruning Loop
                      → Text Impact Calculator
                      → Removal Evaluator
                      → Change Executor
                  → Final PDF
```

---

## 5. Key Components Identified

### Agents
| Agent | Purpose | Model |
|-------|---------|-------|
| DocumentFetcher | Fetch JD from URL | - |
| JDParser | Extract requirements/keywords | Haiku |
| ResumeJDMatcher | Calculate relevance scores | Sonnet |
| JDsRanker | Sort by fit score | Haiku |
| DraftWriter | Initial document generation | Sonnet |
| DocumentEvaluator | Quality assessment | Sonnet |
| DocumentPolisher | Refinement | Sonnet |
| FactChecker | Anti-hallucination validation | Sonnet |
| TexTemplateFiller | LaTeX generation | - |
| TexCompiler | PDF compilation | - |

### Orchestrators
1. **TailoringOrchestra** - Master coordinator
2. **InputPreparationOrchestra** - Document loading/validation
3. **JDMatchingOrchestra** - JD selection
4. **WritingPolishingOrchestra** - Generation + quality
5. **PruningOrchestra** - Length optimization

---

## 6. Decision Points

### Quality Thresholds
```python
QUALITY_THRESHOLD = 0.8  # Minimum acceptable score
MAX_ITERATIONS = 10      # Maximum refinement loops
AI_DETECTION_THRESHOLD = 0.999  # For cover letters
```

### Branching Logic
1. **Score Decrease:** Rollback to previous version
2. **Issues Found:** Re-run improvement agent
3. **Good Enough:** Proceed to release

---

## 7. Adaptations for GroundedCV

### 7.1 Simplified Architecture
- Combine some orchestras for MVP
- Focus on core path: Import → Research → Generate → Validate

### 7.2 A/B Testing Integration
- Fork the generation pipeline into 3 parallel branches
- Each branch uses slightly different prompts
- Validation runs on all 3 variants

### 7.3 Real-Time Updates
- WebSocket connection for progress streaming
- Each stage emits progress events
- Frontend displays live pipeline status

---

## 8. State Management Pattern

From `state/run_context.py`:

```python
class RunContext:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.checkpoints: dict[str, Any] = {}
        self.current_stage: str = "initialization"

    def save_checkpoint(self, stage: str, data: Any):
        self.checkpoints[stage] = data
        self._persist()

    def restore_from_checkpoint(self, stage: str) -> Any:
        return self.checkpoints.get(stage)
```

### Checkpoint Stages
1. `initialization`
2. `input_preparation`
3. `jd_matching`
4. `writing_polishing`
5. `pruning`
6. `completed`

---

## 9. Visual Pipeline for GroundedCV

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GROUNDED-CV PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐                                                       │
│  │ IMPORT       │  Upload docs → Parse → Synthesize → Q&A → Master      │
│  └──────────────┘                                                       │
│         ↓                                                                │
│  ┌──────────────┐                                                       │
│  │ RESEARCH     │  Market/Company → Web Search → Cache → Report         │
│  └──────────────┘                                                       │
│         ↓                                                                │
│  ┌──────────────┐                                                       │
│  │ GENERATE     │  JD Parse → 3x Variants → Validate → A/B Test         │
│  └──────────────┘                                                       │
│         ↓                                                                │
│  ┌──────────────┐                                                       │
│  │ OUTPUT       │  User Select → LaTeX Fill → PDF Compile → Store       │
│  └──────────────┘                                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```
