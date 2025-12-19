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

## Project Structure

```
grounded-cv/
├── backend/                       # FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI entry point
│   │   ├── config.py             # Configuration management
│   │   ├── agents/               # AI agent implementations
│   │   ├── orchestrators/        # Agent orchestration
│   │   ├── api/                  # API routes
│   │   ├── models/               # Pydantic models
│   │   └── services/             # Business logic
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                      # React frontend
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── pages/                # Page components
│   │   ├── stores/               # Zustand stores
│   │   └── services/             # API clients
│   ├── package.json
│   └── Dockerfile
├── config/                        # Public configuration templates
│   ├── personal_info.example.yaml
│   └── preferences.yaml
├── templates/                     # LaTeX templates (public)
│   ├── resume_ats.tex
│   └── cover_letter.tex
├── data/                          # Junction to private data repo (see Setup)
│   ├── master-resume/             # Master resume files
│   ├── market-research/           # Cached market research
│   ├── company-research/          # Cached company research
│   ├── base-resumes/              # Profession-specific resumes
│   ├── tailored/                  # Job-specific applications
│   └── config/                    # User configuration (private)
├── docker-compose.yml
└── .thoughts/                     # Design documentation
```

## Quick Start

### Prerequisites

1. Docker and Docker Compose
2. Anthropic API key
3. git-crypt (for encrypted data)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/grounded-cv.git
   cd grounded-cv
   ```

2. Set up the private data repository:

   The `data/` directory is a junction (Windows) or symlink (Linux/macOS) pointing to a separate private repository
   that stores your personal resume data. This separation ensures private data is never committed to the main repo.

   **Windows:**
   ```cmd
   git clone https://github.com/yourusername/grounded-cv-data.git ../grounded-cv-data
   mklink /J data ..\grounded-cv-data
   ```

   **Linux/macOS:**
   ```bash
   git clone https://github.com/yourusername/grounded-cv-data.git ../grounded-cv-data
   ln -s ../grounded-cv-data data
   ```

3. Copy environment configuration:
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

4. Set up git-crypt (for data encryption):
   ```bash
   git-crypt init
   git-crypt add-gpg-user YOUR_GPG_KEY_ID
   ```

5. Copy personal info template:
   ```bash
   cp config/personal_info.example.yaml data/config/personal_info.yaml
   # Edit with your personal information
   ```

6. Start the services:
   ```bash
   docker-compose up -d
   ```

7. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Setup

For local development without Docker:

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Multi-Model Strategy

| Task Type | Model | Rationale |
|-----------|-------|-----------|
| Parsing/Extraction | Haiku | Fast, cost-effective |
| Writing/Generation | Sonnet | Balanced quality |
| Complex Reasoning | Opus | Deep analysis |
| Fact Checking | Sonnet | Accuracy critical |

## Status

**In Development** - Sprint 1: Foundation

See `.thoughts/specification.md` for full specification and the plan file for detailed implementation roadmap.

## License

MIT
