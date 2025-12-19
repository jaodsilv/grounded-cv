# GroundedCV Documentation

This directory contains the design documentation for the GroundedCV resume tailoring system.

## Overview

GroundedCV is a three-phase resume tailoring system that creates personalized, ATS-optimized resumes by combining a Master Resume, company culture research, and job-specific tailoring using Claude Agent SDK.

## Documentation Structure

### Product Specification

- **[specification.md](specification.md)** - Complete product specification including requirements, architecture, and implementation roadmap

### Architecture

Design documents detailing system components and patterns:

- **[architecture/agents.md](architecture/agents.md)** - Agent design, orchestrators, commands, and skills definitions
- **[architecture/orchestration.md](architecture/orchestration.md)** - Pipeline orchestration patterns and workflow design
- **[architecture/sdk-patterns.md](architecture/sdk-patterns.md)** - Claude SDK usage patterns and integration strategies

### Reference

Analysis of existing implementations and patterns to adopt:

- **[reference/legacy-codebase.md](reference/legacy-codebase.md)** - Analysis of the original ats-research application
- **[reference/evaluator-patterns.md](reference/evaluator-patterns.md)** - Patterns from existing cover letter evaluator agents

## Key Concepts

1. **Anti-Hallucination First** - Never generates content not in Master Resume
2. **Local-First Privacy** - All data stays on user's machine
3. **Three-Phase Processing** - Master Resume → Company Research → Resume Tailoring
4. **Multi-Model Strategy** - Haiku for parsing, Sonnet for writing, Opus for complex reasoning
