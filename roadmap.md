# GroundedCV Project Roadmap

> Generated: 2025-12-18
> Updated: 2025-12-28 (Roadmap Review)
> Project Stage: Initial/Non-Working (Sprint 1 Foundation in progress)

## Executive Summary

GroundedCV is a three-phase resume tailoring system that creates personalized, ATS-optimized resumes using Claude Agent SDK. This roadmap outlines the path from current foundation to a fully functional MVP and beyond.

**Key Differentiators:**
1. Anti-Hallucination First - Never generates content not in Master Resume
2. Local-First Privacy - All data stays on user's machine
3. 60-70% Tailoring Rule - Optimal balance avoiding over-optimization
4. User's Own API Quota - No subscription, transparent costs

## Current State

### Completed (Sprint 1 Foundation)
- FastAPI backend skeleton with health endpoints
- BaseAgent class with Claude Agent SDK integration
- Retry logic with exponential backoff
- React + TypeScript + Vite frontend setup
- Basic layout components and Dashboard page
- Docker Compose configuration
- CI/CD workflows
- LaTeX templates (resume_ats.tex, cover_letter.tex)
- Data directory structure with git-crypt configuration

### Not Yet Implemented
- Master Resume data entry and storage
- AI agents for parsing, writing, and validation
- API routes for core functionality
- Frontend pages beyond Dashboard
- PDF generation pipeline

---

## Current Sprint / Immediate Focus (P0-P1)

### P0 - Critical: Minimum Viable Path

These issues must be completed for the system to function at all:

| Issue | Title | Component | Status |
|-------|-------|-----------|--------|
| #17 | [Backend] Implement Master Resume Data Models | Backend | Done |
| #18 | [Backend] Implement Master Resume CRUD API | Backend | Pending |
| #19 | [Backend] Implement JD Parser Agent | Backend | Pending |
| #20 | [Backend] Implement Resume Writer Agent | Backend | Pending |
| #21 | [Backend] Implement PDF Generation Pipeline | Backend | Pending |
| #22 | [Frontend] Implement Master Resume Entry Form | Frontend | Pending |
| #23 | [Frontend] Implement Job Application Generation Page | Frontend | Pending |
| #24 | [Backend] Implement Anti-Hallucination Validation Agent | Backend | Pending |

**Goal:** User can input resume data, paste a job description, and receive a validated, tailored PDF resume with no fabricated content.

#### P0 Infrastructure (Prerequisites)

These are implicit but critical foundations:

| Component | Approach | Notes |
|-----------|----------|-------|
| Master Resume storage | File-based YAML/Markdown with git-crypt | Leverages existing data directory setup |
| Error handling framework | Retry logic + user-facing messages | Retry logic exists; add error display |
| Deployment target | Docker Compose | Already configured in Sprint 1 |
| Testing strategy | Unit tests for agents, E2E for flow | Integrated into each issue |

#### PDF Generation Strategy

**Approach:** TeX/LaTeX (professional quality output)

**Risk Mitigation:**
- Timebox TeX setup to 3 days maximum
- Docker container with TeX Live pre-installed (reduces environment issues)
- Fallback: If TeX blocked after 3 days, pivot to Puppeteer HTML-to-PDF for P0
- Template: Use existing `resume_ats.tex` from Sprint 1 foundation

### P1 - High: Complete MVP

These issues complete the core feature set with research and analytics:

| Issue | Title | Component | Status |
|-------|-------|-----------|--------|
| #25 | [Backend] Implement Company Research Agent | Backend | Pending |
| #26 | [Backend] Implement Gap Analysis Agent | Backend | Pending |
| #27 | [Frontend] Implement Research Page | Frontend | Pending |
| #28 | [Backend] Add Cost Tracking and Display | Backend | Pending |

**Goal:** Full three-phase pipeline with company research, gap analysis, and cost transparency.

---

## Near-Term Goals (P2)

Important features and quality improvements:

| Issue | Title | Component | Status |
|-------|-------|-----------|--------|
| #29 | [Backend] Implement Document Import (PDF/Markdown) | Backend | Pending |
| #30 | [Backend] Implement Achievement Extractor Agent | Backend | Pending |
| #31 | [Frontend] Implement Import Page | Frontend | Pending |
| #32 | [Backend] Implement Cover Letter Writer Agent | Backend | Pending |
| #33 | [Backend] Add WebSocket Support for Real-Time Updates | Backend | Pending |

**Goal:** Streamlined import workflow and real-time generation feedback.

---

## Future Considerations (P3-P4)

### P3 - Low Priority (Nice-to-Have)

| Issue | Title | Component |
|-------|-------|-----------|
| #34 | [Backend] Implement A/B Variant Generation | Backend |
| #35 | [Frontend] Add Version History View | Frontend |
| #36 | [Backend] Implement LinkedIn Import | Backend |

### P4 - Backlog (Future Releases)

| Issue | Title | Component |
|-------|-------|-----------|
| #37 | [Backend] Implement Multiple LaTeX Templates | Backend |
| #38 | [Frontend] Implement Application Tracking Board | Frontend |
| #39 | [Backend] Add Multi-Language Support | Backend |

---

## Milestones

### Milestone 1: Minimum Viable Product (MVP)
- **Target:** Week 5-6 (solo dev + AI assistance)
- **Issues:** All P0 issues (#17-#24)
- **Resource:** Solo developer with Claude Code agents
- **Success Criteria:**
  - User can enter master resume data through web form
  - User can paste a job description
  - System generates a tailored resume
  - Anti-hallucination validation confirms no fabricated content
  - PDF output downloads successfully

### Milestone 2: Complete v1.0
- **Target:** Week 7-8 (assumes M1 complete by end of Week 6)
- **Buffer:** 1 week contingency for P0 slippage
- **Issues:** All P1 issues (#25-#28)
- **Success Criteria:**
  - Company research integrated into tailoring
  - Gap analysis provided to user
  - Cost transparency (pre/post display)
  - All core requirements from specification met

### Milestone 3: Enhanced Experience
- **Target:** Week 9-10
- **Issues:** All P2 issues (#29-#33)
- **Success Criteria:**
  - Can import existing resume documents
  - Cover letter generation working
  - Real-time progress updates via WebSocket
  - Achievement extraction with STAR formatting

### Milestone 4: Advanced Features
- **Target:** Week 11-14
- **Issues:** P3 issues (#34-#36)
- **Success Criteria:**
  - A/B variant comparison working
  - Version history accessible
  - LinkedIn import functional

---

## Dependencies & Risks

### Dependency Graph

```
P0 Tasks (Foundation + Validation):
  Master Resume Models (#17) ─────┬──► Master Resume API (#18) ──► Resume Writer Agent (#20)
  JD Parser Agent (#19) ──────────┘           │                           │
                                              │                           ▼
                                              │                  Anti-Hallucination (#24)
                                              │                           │
  PDF Generation Pipeline (#21) ◄─────────────┴───────────────────────────┘
                    │
                    ▼
  Frontend Form (#22) + Job Application Page (#23)

P1 Tasks (Research & Analytics):
  Company Research Agent (#25) ◄──── JD text (external input)
  Gap Analysis Agent (#26) ◄──────── JD Parser (#19) + Master Resume (#17)
  Cost Tracking (#28) ◄───────────── All agent calls
  Research Page (#27) ◄───────────── Company Research (#25)

P2 Tasks (Import & Polish):
  Document Import (#29) ───────── Independent
  Achievement Extractor (#30) ◄── Document Import (#29)
  Cover Letter Writer (#32) ◄──── Company Research (#25)

Critical Path: #17 → #18 → #20 → #24 → #21 → #23
Parallelizable: #19 (independent), #22 (after #18), #25 (after P0)
```

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| AI Hallucination | HIGH | CRITICAL | P0 validation agent (#24) + strict prompts + output comparison against Master Resume |
| TeX Installation | MEDIUM | HIGH | Docker with TeX Live, 3-day timebox, HTML-to-PDF fallback |
| API Rate Limits | MEDIUM | HIGH | Retry logic (implemented), request caching |
| Cost Overruns | MEDIUM | MEDIUM | P1 cost tracking (#28), per-request budget cap ($0.50 default) |
| JD Parser Quality | MEDIUM | HIGH | Confidence scoring, user verification fallback, 20+ JD test corpus |
| Complex PDFs Import | MEDIUM | MEDIUM | Vision model fallback |

---

## Priority Labels

| Label | Color | Description |
|-------|-------|-------------|
| P0 | ![#B60205](https://via.placeholder.com/15/B60205/B60205.png) Red | Critical: Blocking/Security/System Down |
| P1 | ![#D93F0B](https://via.placeholder.com/15/D93F0B/D93F0B.png) Orange | High: Core functionality/Major bugs |
| P2 | ![#FBCA04](https://via.placeholder.com/15/FBCA04/FBCA04.png) Yellow | Medium: Important features/Improvements |
| P3 | ![#0E8A16](https://via.placeholder.com/15/0E8A16/0E8A16.png) Green | Low: Nice-to-have/Minor issues |
| P4 | ![#C5DEF5](https://via.placeholder.com/15/C5DEF5/C5DEF5.png) Light Blue | Backlog: Future considerations |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Resume tailoring time | < 5 minutes | End-to-end from JD input to PDF |
| Cost per resume | < $0.50 | Token usage tracking |
| Hallucination rate | < 1% | Validation agent detection |
| Interview callback increase | 30%+ | User-reported (future) |
| ATS pass rate | > 80% | ATS compatibility scoring |

---

## Getting Started

1. **View issues in GitHub:**
   ```bash
   gh issue list --label P0
   gh issue list --label P1
   ```

2. **Start with P0 issues in order:**
   - Begin with Master Resume Data Models (foundation for everything)
   - Then Master Resume CRUD API
   - Then JD Parser Agent and Resume Writer Agent in parallel
   - Then PDF Generation Pipeline
   - Finally, Frontend forms and pages

---

## Notes

1. **Anti-Hallucination is CRITICAL:** This is the key differentiator. Validation agent (#24) is now in P0 to ensure no fabricated content from MVP launch.

2. **Local-First Architecture:** All data stays on user's machine. No cloud storage, no user accounts.

3. **Cost Transparency:** Users provide their own API keys. Cost tracking is essential for trust.

4. **Specification Reference:** See `../.thoughts/specification.md` for full requirements and design decisions.

5. **Agent Patterns:** See `../.thoughts/agents.md` for agent designs and `../.thoughts/orchestration.md` for pipeline patterns.

6. **JD Parser Acceptance Criteria:**
   - Successfully extracts: job title, company, required skills, responsibilities, qualifications
   - Handles 90%+ of common JD formats (LinkedIn, Indeed, company career pages)
   - Returns confidence score (0-1) for each extracted field
   - Test corpus: 20+ real job descriptions from varied sources
   - Fallback: If confidence < 0.7, prompt user to verify/correct extraction

7. **Roadmap Review (2025-12-28):** Multi-agent review identified hallucination contradiction (resolved by moving #24 to P0), timeline adjustment (Week 5-6 realistic for solo dev + AI), and infrastructure gaps (documented in P0 Prerequisites).
