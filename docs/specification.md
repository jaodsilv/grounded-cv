# GroundedCV - Final Specification

## Executive Summary

**GroundedCV** is a three-phase resume tailoring system that creates personalized, ATS-optimized resumes by combining a Master Resume, company culture research, and job-specific tailoring using Claude Agent SDK.

*Tagline: "Your story. Truthfully tailored."*

**Key Differentiators:**
1. **Anti-Hallucination First** - Never generates content not in Master Resume
2. **Local-First Privacy** - All data stays on user's machine
3. **60-70% Tailoring Rule** - Optimal balance avoiding over-optimization
4. **User's Own API Quota** - No subscription, transparent costs

---

## Brainstorm Session Summary

| Phase | Status | Key Outcomes |
|-------|--------|--------------|
| Socratic Dialogue (8 rounds) | ✅ Complete | Core requirements, user needs, success criteria |
| Domain Exploration | ✅ Complete | Market analysis, ATS best practices, competitor gaps |
| Technical Analysis | ✅ Complete | FastAPI+React stack, Claude SDK patterns, LaTeX pipeline |
| Constraint Analysis | ✅ Complete | Simplified encryption, Docker deployment, cost controls |
| Requirements Synthesis | ✅ Complete | MoSCoW prioritization, 21 requirements, risk matrix |

---

## Problem Statement

**Pain Points:**
1. Time-consuming manual edits for each job application
2. Keyword mismatch causing ATS screening failures (75% never reach humans)
3. Unclear what skills/experiences to emphasize for each role

**Target Users:**
- Active job seekers applying to multiple positions
- Career changers transitioning industries/roles
- Tech professionals
- General professionals

**Success Metrics:**
- Resume tailoring in < 5 minutes (vs. 30-60 min manual)
- < $0.50 average cost per resume
- < 1% hallucination rate
- 30%+ increase in interview callbacks

---

## System Architecture

### Three-Phase Processing Model

```
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Master Resume (One-time per user)                         │
│ ─────────────────────────────────────────────────────────────────── │
│ Inputs:                                                             │
│   • Performance reviews + achievement documents                     │
│   • Existing resume                                                 │
│   • LinkedIn profile (optional)                                     │
│   • Interactive achievement builder (STAR method)                   │
│                                                                     │
│ Output: Comprehensive Master Resume (JSON/YAML/Markdown)            │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: Company Research (On-demand, cached 6 months)             │
│ ─────────────────────────────────────────────────────────────────── │
│ Data Sources:                                                       │
│   • Company website + careers page                                  │
│   • LinkedIn company page                                           │
│   • Glassdoor/Indeed reviews                                        │
│   • News/press releases                                             │
│   • Historical job posting patterns                                 │
│                                                                     │
│ Output: Company Culture Profile (shared across users - opt-in)      │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: Resume Tailoring (Per job description)                    │
│ ─────────────────────────────────────────────────────────────────── │
│ Inputs:                                                             │
│   • Master Resume                                                   │
│   • Company Research                                                │
│   • Job Description                                                 │
│                                                                     │
│ Tailoring Strategies:                                               │
│   • Keyword optimization                                            │
│   • Skills prioritization                                           │
│   • Experience relevance scoring                                    │
│   • Tone matching to company culture                                │
│                                                                     │
│ Output: Tailored Resume (LaTeX → PDF)                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Technical Specifications

### Recommended Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Backend** | FastAPI (Python) | Native Claude SDK integration, subprocess support |
| **Frontend** | React + TypeScript + Vite | Modern UI, TypeScript safety |
| **AI Engine** | Claude Agent SDK (Python) | Multi-step agent workflows, MCP tools |
| **Data Storage** | Local files (YAML/MD) + git-crypt | Version control + encryption, simple file-based |
| **PDF Generation** | XeTeX + Jinja2 templates | Professional output, font support |
| **Deployment** | Docker Compose | Simplified installation |
| **Authentication** | None (local-first) | Single-user, privacy-focused |

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│            User's Machine (localhost)                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    HTTP     ┌─────────────────────────┐    │
│  │  React Frontend │◄──────────►│    FastAPI Backend      │    │
│  │  (localhost:3000)│            │    (localhost:8000)     │    │
│  └─────────────────┘            │                         │    │
│                                  │  ┌──────────────────┐   │    │
│                                  │  │ Claude Agent SDK │   │    │
│                                  │  │ (user's API key) │   │    │
│                                  │  └──────────────────┘   │    │
│                                  │                         │    │
│                                  │  ┌──────────────────┐   │    │
│                                  │  │ XeTeX subprocess │   │    │
│                                  │  └──────────────────┘   │    │
│                                  └───────────┬─────────────┘    │
│                                              │                  │
│  ┌───────────────────────────────────────────▼──────────────┐   │
│  │         Git-Crypt Encrypted Local Repository             │   │
│  │  (YAML/Markdown files with version control)              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Storage (File-Based with Git-Crypt)

```
resume-data/ (git-crypt encrypted repo)
├── master-resume/
│   ├── profile.yaml           # Personal info
│   ├── experience.yaml        # Work history
│   ├── education.yaml         # Education & certifications
│   ├── skills.yaml            # Skills inventory
│   └── achievements.md        # STAR-formatted achievements
├── company-research/
│   └── {company-slug}.yaml    # Company culture + cache timestamp
├── tailored-resumes/
│   └── {company}-{job-id}/
│       ├── job-description.md # Original JD
│       ├── tailoring-log.md   # AI reasoning
│       ├── resume.tex         # Generated LaTeX
│       ├── resume.pdf         # Compiled PDF
│       └── cover-letter.md    # Generated cover letter (v1.0)
└── templates/
    └── ats-optimized.tex      # Single ATS-friendly template
```

**File Formats:**
- **YAML**: Structured data (profile, skills, company research)
- **Markdown**: Text content (achievements, cover letters, JDs)
- **Import/Export**: Markdown files for portability (NO DOCX)

---

## Feature Requirements

### Phase 1: Master Resume Builder

**Data Collection:**
1. Parse existing resume (PDF/Markdown)
2. Import LinkedIn profile (optional)
3. Process performance review documents
4. Interactive STAR method prompts for achievements
5. Metrics suggestion engine for quantification
6. Import/Export via Markdown files

**Hallucination Prevention (CRITICAL):**
- Resume sections dynamically determined based on ACTUAL Master Resume content
- If Master Resume lacks certifications → no certifications section generated
- Strict grounding to source material only

### Phase 2: Company Research Agent

**Trigger:** On-demand when first job from company is added
**Cache Duration:** 6 months (manual refresh available)
**Sharing Model:** Optional contribution to shared repository

**Research Scope:**
1. Values and mission statements
2. Tech stack and methodologies
3. Employee sentiment (Glassdoor/Indeed)
4. Interview patterns and expectations
5. Recent news/press releases
6. Historical job posting analysis

### Phase 3: Tailoring Engine

**Automation Level:** Fully automated

**Tailoring Strategies:**
1. **Keyword Optimization** - Match JD keywords, rephrase achievements
2. **Skills Prioritization** - Reorder skills by relevance
3. **Experience Scoring** - Highlight/hide based on relevance
4. **Tone Matching** - Adapt language to company culture

**Gap Analysis:**
1. Highlight transferable skills for gaps
2. Suggest learning resources
3. Provide honest fit percentage report

### Output Generation

**Template:** Single ATS-optimized LaTeX/XeTeX template
**Sections:** AI-determined based on:
- Job requirements
- Master Resume content (NO hallucination of missing sections)

**Version History:** Track generated resume versions (basic)

---

## Constraints & Considerations

### Anti-Hallucination Measures
1. Strict grounding: Only use content from Master Resume
2. Dynamic sections: Only include sections with actual content
3. Validation layer: Cross-check generated content against source
4. Reasoning log: Document AI decision-making for transparency

### Privacy & Security
1. Local-first architecture
2. Git-crypt for encrypted storage
3. User's own API keys (no central auth)
4. Optional data sharing (explicit opt-in)

### Dependencies
1. Local TeX Live/MiKTeX installation required
2. Claude API key required
3. Git + git-crypt for data management

---

## MoSCoW Prioritized Requirements

### MUST HAVE (MVP - Week 5-6)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-001 | Master Resume Data Entry | Form-based UI, STAR guidance, local storage |
| FR-002 | Git-Crypt Storage | YAML/Markdown files in git-crypt encrypted repo |
| FR-003 | Manual Company Info Entry | Form for company, job title, JD, requirements |
| FR-004 | Resume Tailoring Engine | Claude SDK, anti-hallucination validation |
| FR-005 | Single LaTeX Template | ATS-optimized, single-column, standard fonts |
| FR-006 | PDF Generation | XeTeX compilation, error handling, <10s |
| FR-007 | Basic Version History | Timestamp, company, file path tracking |
| NFR-001 | Cost Transparency | Pre/post cost display, running total |
| NFR-002 | Docker Deployment | Single `docker-compose up` startup |
| CC-001 | **Anti-Hallucination** | Zero fabrication, validation layer, diff view |

### SHOULD HAVE (v1.0 - Week 7-8)

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-008 | Automated Company Research | User-provided URLs, Claude extraction |
| FR-009 | 6-Month Research Cache | Auto-expire, manual refresh, sharing opt-in |
| FR-010 | Gap Analysis | Fit percentage, transferable skills, learning resources |
| FR-011 | Multiple Templates | 3-5 ATS-friendly template options |
| FR-012 | Cover Letter Generation | Tailored cover letters using master resume + company data |
| NFR-006 | Resume Import | Parse PDF/Markdown to populate Master Resume |
| IR-003 | LinkedIn Import | Parse LinkedIn data export ZIP |

### COULD HAVE (v1.5 - Week 9-10)

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-013 | AI Achievement Writer | STAR-formatted achievement suggestions |
| FR-015 | Application Tracking | Kanban board, reminders, CSV export |
| FR-017 | Multi-Language Support | Spanish, French, German, Portuguese |

### WON'T HAVE (Out of Scope)

- Auto-apply to jobs
- Cloud-hosted SaaS version
- AI interview prep
- Salary negotiation
- DOCX import/export (use Markdown instead)

---

## Critical Implementation Details

### Anti-Hallucination Controls (CRITICAL)

```python
# Prompt engineering
prompt = """
CRITICAL: Only rephrase existing content from the master resume.
NEVER invent new experiences, skills, or achievements.
Output JSON with source references for each tailored item.
"""

# Validation layer
def validate_output(tailored, master_resume):
    for item in tailored.items:
        if not has_source_in_master(item, master_resume):
            raise HallucinationError(f"No source for: {item}")
    return tailored
```

### LaTeX Template Strategy (Jinja2 + Modified Delimiters)

```latex
% Use \VAR{} instead of {{}} to avoid LaTeX conflicts
\documentclass[11pt]{article}
\newcommand{\name}{\VAR{personal_info.name}}

\begin{document}
\section*{\name}
\BLOCK{for exp in experiences}
  \textbf{\VAR{exp.title}} at \VAR{exp.company}
\BLOCK{endfor}
\end{document}
```

### Cost Management

```python
# Pre-flight estimation
estimated_tokens = len(prompt) / 4 + len(resume_data) / 4
estimated_cost = estimated_tokens * 0.000003  # Claude pricing

if estimated_cost > user_limit:
    raise CostLimitExceeded(f"Estimated ${estimated_cost:.4f} exceeds limit")
```

---

## Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| AI hallucination | HIGH | CRITICAL | P0 validation agent (#24) + strict prompts + output comparison against Master Resume |
| TeX installation complexity | MEDIUM | HIGH | Docker with TeX, 3-day timebox, HTML-to-PDF fallback |
| API rate limits | MEDIUM | HIGH | Local caching, retry logic |
| Cost overruns | MEDIUM | MEDIUM | Pre-flight estimates, spending caps, per-request budget cap ($0.50 default) |
| JD Parser quality | MEDIUM | HIGH | Confidence scoring, user verification fallback, 20+ JD test corpus |

---

## Final Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **TeX Distribution** | External install required | Smaller Docker image, user manages TeX separately |
| **AI Authentication** | Leverage local Claude Code | No API key management - uses existing Claude Code session |
| **Hallucination Tolerance** | Strict for facts, flexible for tone | Zero tolerance for skills/experiences, allow tone adjustments |
| **Data Storage** | Git-crypt encrypted YAML/Markdown | Version control + encryption, simple file-based |
| **File Formats** | PDF output, Markdown import/export | NO DOCX - use Markdown for portability |

---

## Implementation Roadmap

```
Week 1-2: Foundation
├── Docker + FastAPI skeleton
├── React + Vite frontend scaffold
├── Git-crypt encrypted file storage (YAML/Markdown)
└── Claude SDK integration (via Claude Code)

Week 3-4: Core Features
├── Master Resume CRUD (YAML/Markdown files)
├── LaTeX template + PDF generation (3-day timebox, HTML fallback)
├── Basic tailoring engine
└── Anti-hallucination validation (P0 critical)

Week 5-6: MVP Complete
├── All P0 issues (#17-#24) complete
├── End-to-end resume generation
├── PDF output functional
└── Validation agent ensuring no fabrication

Week 7-8: v1.0 Features
├── URL-based company research
├── 6-month caching
├── Gap analysis
└── Cost tracking + transparency
```

---

## Session Complete

**Status:** ✅ All 6 brainstorm phases complete + Final clarifications resolved

**Artifacts Generated:**
1. This specification document
2. Domain research (market, ATS, competitors)
3. Technical analysis (FastAPI+React, Claude SDK)
4. Constraint analysis (21 constraints identified)
5. Requirements synthesis (MoSCoW prioritized)

**Key Implementation Notes:**
1. Leverage existing Claude Code session for AI calls (no separate API key needed)
2. User must have TeX Live/MiKTeX installed locally
3. Anti-hallucination: Zero tolerance for facts, flexible for tone adjustments
4. Data storage: Git-crypt encrypted YAML/Markdown files (version controlled)
5. File formats: PDF output only, Markdown for import/export (NO DOCX)
6. Cover Letter Generation in SHOULD HAVE (v1.0)

**Ready for:** Implementation
