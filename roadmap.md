# GroundedCV Project Roadmap

> Generated: 2025-12-18
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
- Data directory structure with git-crypt encryption

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
| #18 | [Backend] Implement Master Resume Data Models | Backend | Pending |
| #19 | [Backend] Implement Master Resume CRUD API | Backend | Pending |
| #20 | [Backend] Implement JD Parser Agent | Backend | Pending |
| #21 | [Backend] Implement Resume Writer Agent | Backend | Pending |
| #22 | [Backend] Implement PDF Generation Pipeline | Backend | Pending |
| #23 | [Frontend] Implement Master Resume Entry Form | Frontend | Pending |
| #24 | [Frontend] Implement Job Application Generation Page | Frontend | Pending |

**Goal:** User can input resume data, paste a job description, and receive a tailored PDF resume.

### P1 - High: Complete MVP

These issues complete the core feature set:

| Issue | Title | Component | Status |
|-------|-------|-----------|--------|
| #25 | [Backend] Implement Anti-Hallucination Validation Agent | Backend | Pending |
| #26 | [Backend] Implement Company Research Agent | Backend | Pending |
| #27 | [Backend] Implement Gap Analysis Agent | Backend | Pending |
| #28 | [Frontend] Implement Research Page | Frontend | Pending |
| #29 | [Backend] Add Cost Tracking and Display | Backend | Pending |

**Goal:** Full three-phase pipeline working with validation and transparency.

---

## Near-Term Goals (P2)

Important features and quality improvements:

| Issue | Title | Component | Status |
|-------|-------|-----------|--------|
| #30 | [Backend] Implement Document Import (PDF/Markdown) | Backend | Pending |
| #31 | [Backend] Implement Achievement Extractor Agent | Backend | Pending |
| #32 | [Frontend] Implement Import Page | Frontend | Pending |
| #33 | [Backend] Implement Cover Letter Writer Agent | Backend | Pending |
| #34 | [Backend] Add WebSocket Support for Real-Time Updates | Backend | Pending |

**Goal:** Streamlined import workflow and real-time generation feedback.

---

## Future Considerations (P3-P4)

### P3 - Low Priority (Nice-to-Have)

| Issue | Title | Component |
|-------|-------|-----------|
| #35 | [Backend] Implement A/B Variant Generation | Backend |
| #36 | [Frontend] Add Version History View | Frontend |
| #37 | [Backend] Implement LinkedIn Import | Backend |

### P4 - Backlog (Future Releases)

| Issue | Title | Component |
|-------|-------|-----------|
| #38 | [Backend] Implement Multiple LaTeX Templates | Backend |
| #39 | [Frontend] Implement Application Tracking Board | Frontend |
| #40 | [Backend] Add Multi-Language Support | Backend |

---

## Milestones

### Milestone 1: Minimum Viable Product (MVP)
- **Target:** Week 3-4
- **Issues:** All P0 issues (#18-#24)
- **Success Criteria:**
  - User can enter master resume data through web form
  - User can paste a job description
  - System generates a tailored resume
  - PDF output downloads successfully
  - No fabricated content in output

### Milestone 2: Complete v1.0
- **Target:** Week 5-6
- **Issues:** All P0 + P1 issues (#18-#29)
- **Success Criteria:**
  - Anti-hallucination validation working
  - Company research integrated into tailoring
  - Gap analysis provided to user
  - Cost transparency (pre/post display)
  - All core requirements from specification met

### Milestone 3: Enhanced Experience
- **Target:** Week 7-8
- **Issues:** All P2 issues (#30-#34)
- **Success Criteria:**
  - Can import existing resume documents
  - Cover letter generation working
  - Real-time progress updates via WebSocket
  - Achievement extraction with STAR formatting

### Milestone 4: Advanced Features
- **Target:** Week 9-12
- **Issues:** P3 issues (#35-#37)
- **Success Criteria:**
  - A/B variant comparison working
  - Version history accessible
  - LinkedIn import functional

---

## Dependencies & Risks

### Dependency Graph

```
P0 Tasks (Foundation):
  Master Resume Models ─────┬──► Master Resume API ──► Resume Writer Agent
  JD Parser Agent ──────────┘           │                    │
                                        │                    ▼
  PDF Generation Pipeline ◄─────────────┴────────── Tailored Resume

P1 Tasks (Validation & Research):
  Anti-Hallucination Agent ◄── Resume Writer (P0)
  Company Research Agent ──── Independent
  Gap Analysis Agent ◄─────── JD Parser (P0)

P2 Tasks (Import & Polish):
  Document Import ───────── Independent
  Achievement Extractor ◄── Document Import
  Cover Letter Writer ◄──── Company Research (P1)
```

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| AI Hallucination | HIGH | CRITICAL | P1 validation agent, strict prompts |
| TeX Installation | MEDIUM | HIGH | Docker with TeX Live, clear docs |
| API Rate Limits | MEDIUM | HIGH | Retry logic (implemented) |
| Cost Overruns | MEDIUM | MEDIUM | P1 cost tracking, spending limits |
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

To execute the prioritization plan:

1. **Run the setup script:**
   ```bash
   # From repository root
   chmod +x scripts/create-labels-and-issues.sh
   ./scripts/create-labels-and-issues.sh
   ```

   Or on Windows:
   ```powershell
   .\scripts\create-labels-and-issues.ps1
   ```

2. **View issues in GitHub:**
   ```bash
   gh issue list --label P0
   gh issue list --label P1
   ```

3. **Start with P0 issues in order:**
   - Begin with Master Resume Data Models (foundation for everything)
   - Then Master Resume CRUD API
   - Then JD Parser Agent and Resume Writer Agent in parallel
   - Then PDF Generation Pipeline
   - Finally, Frontend forms and pages

---

## Notes

1. **Anti-Hallucination is CRITICAL:** This is the key differentiator. P1 validation must be implemented before any production use.

2. **Local-First Architecture:** All data stays on user's machine. No cloud storage, no user accounts.

3. **Cost Transparency:** Users provide their own API keys. Cost tracking is essential for trust.

4. **Specification Reference:** See `.thoughts/specification.md` for full requirements and design decisions.

5. **Agent Patterns:** See `.thoughts/agents.md` for agent designs and `.thoughts/orchestration.md` for pipeline patterns.
