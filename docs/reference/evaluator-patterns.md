# Existing Agents Analysis

## Executive Summary

This document captures the patterns and capabilities from the existing job-hunting.claude agents that can inform GroundedCV development.

---

## 1. Cover Letter Evaluator Agents (14 Agents)

Located at: `D:\src\claudius\main\job-hunting.claude\agents\cover-letter-evaluator\`

> **Note:** These evaluator patterns will be available as a Claude Code plugin at [github.com/jaodsilv/claudius](https://github.com/jaodsilv/claudius).

### 1.1 ATS Compatibility Agent (`ats.md`)
**Purpose:** Evaluate ATS friendliness
**Model:** Sonnet
**Key Features:**
- Standard formatting assessment
- Keyword optimization analysis
- Terminology consistency check
- Strategic keyword placement
- Parsing compatibility

**Scoring:** 10-point scale
- 9-10: Excellent ATS compatibility
- 7-8: Good, minor optimizations needed
- 5-6: Moderate, significant improvements needed
- 3-4: Poor, major issues
- 1-2: Very poor, likely filtered out

**Critical Rule:** Recommendations must align with candidate's actual resume - no hallucinated skills.

### 1.2 Other Evaluator Agents

| Agent | Focus Area | Key Metrics |
|-------|------------|-------------|
| communication.md | Writing quality | Clarity, conciseness, tone |
| false-assertion-cleaner.md | Hallucination detection | Source verification |
| impact.md | Achievement impact | Quantified results |
| keywords.md | Keyword coverage | JD alignment score |
| overlap.md | Resume/CL redundancy | Uniqueness ratio |
| personalization.md | Company-specific content | Customization score |
| presentation.md | Visual/format quality | Readability score |
| relevance.md | Job relevance | Match percentage |
| result-combiner.md | Aggregate all scores | Weighted average |
| skills.md | Technical skills match | Gap analysis |
| tech-positioning.md | Tech expertise showcase | Positioning score |
| terminology.md | Industry vocabulary | Consistency check |
| true-gaps.md | Skill gaps identification | Gap severity |

### 1.3 Pattern: Multi-Evaluator Architecture

```
Document Input
      ↓
┌─────────────────────────────────────────┐
│         PARALLEL EVALUATORS             │
├─────────────────────────────────────────┤
│  ATS ─────────────┐                     │
│  Communication ───┼─→ Result Combiner   │
│  Impact ─────────┤    │                 │
│  Keywords ───────┤    ↓                 │
│  Personalization ┤  Aggregate Score     │
│  Relevance ──────┤    │                 │
│  Skills ─────────┘    ↓                 │
│                    Recommendations      │
└─────────────────────────────────────────┘
```

---

## 2. Job-Related Agents

### 2.1 Cover Letter Improver (`cover-letter-improver.md`)
**Purpose:** Suggest improvements based on evaluation
**Input:** Evaluation results + original cover letter
**Output:** Improved version with change explanations

### 2.2 Cover Letter Shortener (`cover-letter-shortener.md`)
**Purpose:** Reduce length while maintaining impact
**Target:** 250-400 words (one page)
**Strategy:** Prioritize high-impact content, remove redundancy

### 2.3 Interview Company Researcher (`interview-company-researcher.md`)
**Purpose:** Deep-dive company research
**Output:** Culture report, interview tips, talking points

---

## 3. Commands Analysis

### 3.1 Eval Cover Letter (`eval-cover-letter.md`)
**Flow:**
1. Parse inputs (CL, JD, resume)
2. Launch all evaluator agents in parallel
3. Combine results
4. Generate recommendations

### 3.2 Improve Cover Letter (`improve-cover-letter.md`)
**Flow:**
1. Run evaluation
2. Identify improvement areas
3. Apply improver agent
4. Validate improvements

### 3.3 Overlap Analysis (`overlap-analysis.md`)
**Purpose:** Identify resume/CL redundancy
**Goal:** Ensure CL adds unique value beyond resume

---

## 4. Skills Definition (`SKILL.md`)

### Core Principles
1. **Authenticity** - No false claims
2. **Relevance** - Tailor to each position
3. **Impact** - Demonstrate concrete results
4. **Clarity** - Communicate concisely
5. **Research** - Understand the company and role

### Cover Letter Structure
1. **Opening** - Hook and position reference (grab attention)
2. **Body 1** - Technical fit with concrete examples
3. **Body 2** - Cultural/value alignment
4. **Closing** - Call to action and thank you

### Quality Checklist
- Specific position referenced
- Company name correct
- 2-3 concrete examples with metrics
- Demonstrates understanding of company/role
- No generic statements
- No false claims
- 250-400 words

---

## 5. Templates

### Personal Info Template (`personal-info.example.yaml`)
```yaml
name: "Full Name"
email: "email@example.com"
phone: "+1 (555) 123-4567"
location: "City, State"
linkedin: "linkedin.com/in/username"
github: "github.com/username"
portfolio: "portfolio.example.com"
```

---

## 6. Patterns to Adopt for GroundedCV

### 6.1 Multi-Evaluator Pattern
- Run multiple specialized evaluators in parallel
- Combine scores with weighted average
- Generate prioritized recommendations

### 6.2 Anti-Hallucination Pattern
```python
def validate_claim(claim: str, master_resume: dict) -> bool:
    """Verify every claim traces back to master resume."""
    sources = extract_sources(master_resume)
    return any(claim_matches_source(claim, source) for source in sources)
```

### 6.3 Scoring Methodology
- Use consistent 10-point scales
- Define clear criteria for each score range
- Provide actionable recommendations per score level

### 6.4 Output Structure
```xml
<evaluation>
  <analysis>
    [Detailed evaluation]
    Score: [X/10]
    Issues: [List]
  </analysis>

  <recommendations>
    **HIGH PRIORITY:**
    [Critical changes]

    **MEDIUM PRIORITY:**
    [Important changes]

    **LOW PRIORITY:**
    [Minor enhancements]
  </recommendations>
</evaluation>
```

---

## 7. Agents to Create for GroundedCV

Based on analysis, we need:

### Import Phase
1. **DocumentParser** - PDF text extraction + Vision fallback
2. **AchievementExtractor** - STAR format extraction
3. **MasterResumeBuilder** - Synthesize all sources
4. **QAQuestionGenerator** - Identify missing info

### Research Phase
5. **MarketResearcher** - Role trends and technologies
6. **CompanyResearcher** - Culture and tech stack
7. **GapAnalyzer** - Skills gap identification

### Generation Phase
8. **JDParser** - Extract requirements/keywords
9. **ResumeWriter** - Generate tailored resume
10. **CoverLetterWriter** - Generate tailored cover letter
11. **WhyCompanyWriter** - Generate answer

### Validation Phase
12. **FactChecker** - Anti-hallucination validation
13. **ATSOptimizer** - ATS compatibility check
14. **QualityEvaluator** - Multi-dimensional scoring

### Output Phase
15. **LaTeXGenerator** - Fill templates
16. **PDFCompiler** - XeTeX compilation

---

## 8. Agent Configuration Pattern

```python
@dataclass
class AgentConfig:
    name: str
    model: str  # haiku, sonnet, opus
    tools: list[str]  # Read, Write, WebSearch, etc.
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = ""

# Example
fact_checker_config = AgentConfig(
    name="fact_checker",
    model="claude-sonnet-4-5-20250929",
    tools=["Read"],
    temperature=0.2,  # Lower for factual accuracy
    system_prompt=FACT_CHECKER_PROMPT,
)
```
