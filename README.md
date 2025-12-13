# GroundedCV

*Your story. Truthfully tailored.*

A three-phase resume tailoring system that creates personalized, ATS-optimized resumes by combining a Master Resume, company culture research, and job-specific tailoring.

## Key Differentiators

1. **Anti-Hallucination First** - Never generates content not in Master Resume
2. **Local-First Privacy** - All data stays on your machine
3. **60-70% Tailoring Rule** - Optimal balance avoiding over-optimization
4. **User's Own API Quota** - No subscription, transparent costs

## Three-Phase Processing

```
Phase 1: Master Resume (One-time per user)
    └── Sources: Performance reviews, existing resume, LinkedIn, interactive STAR builder
    └── Output: Comprehensive Master Resume (YAML/Markdown)

Phase 2: Company Research (On-demand, cached 6 months)
    └── Sources: Company website, LinkedIn, Glassdoor, news/press releases
    └── Output: Company Culture Profile

Phase 3: Resume Tailoring (Per job description)
    └── Inputs: Master Resume + Company Research + Job Description
    └── Output: Tailored Resume (LaTeX → PDF)
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Frontend | React + TypeScript + Vite |
| AI Engine | Claude Agent SDK |
| Data Storage | Local YAML/Markdown + git-crypt |
| PDF Generation | XeTeX + Jinja2 templates |
| Deployment | Docker Compose |

## Status

**In Development** - See `.thoughts/specification.md` for full specification.

## License

MIT
