# CLAUDE.md

This file provides guidance to AI assistants (Claude and others) working in this repository. Keep this file updated as the project evolves.

## Repository Status

This repository is newly initialized. This document will be updated as the project structure is established.

**Remote**: `elliwash/bug-free-palm-tree`
**Development branch pattern**: `claude/<task-description>`

---

## Git Workflow

### Branch conventions
- Work on the branch specified at session start (e.g., `claude/add-claude-documentation-H0A3x`)
- Never push directly to `main` or `master` without explicit permission
- Use descriptive branch names: `claude/<short-task-description>-<id>`

### Commit conventions
- Write clear, imperative commit messages (e.g., "Add user authentication module")
- Lead with the "why" when it's not obvious from the change itself
- Do not amend published commits; create new ones instead
- Never skip commit hooks (`--no-verify`)

### Push instructions
```bash
git push -u origin <branch-name>
```
Retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s) on network failures.

---

## General Development Principles

### Code quality
- Do not add features, refactors, or improvements beyond what was explicitly asked
- Do not add docstrings, comments, or type annotations to code you didn't change
- Only add comments where logic is non-obvious
- Avoid backwards-compatibility hacks for code that is provably unused — delete it

### Security
- Never introduce command injection, XSS, SQL injection, or other OWASP Top 10 vulnerabilities
- Validate input only at system boundaries (user input, external APIs); trust internal code
- Never commit secrets, credentials, or `.env` files

### Abstractions and complexity
- Match complexity to the task — no speculative abstractions
- Three similar lines of code is better than a premature helper
- Do not create helpers or utilities for one-time operations

### Error handling
- Do not add error handling for scenarios that cannot happen
- Trust framework and internal code guarantees

---

## Working with AI Assistants

### What to update in this file
Whenever significant decisions are made about this project, update the relevant sections:
- Add build/test/lint commands under a "Development Commands" section
- Document architectural decisions and their rationale
- Record key conventions specific to this codebase
- Note any third-party integrations and how they are configured

### What NOT to do
- Do not create a PR unless the user explicitly requests one
- Do not push to a branch other than the one designated for the session
- Do not perform destructive git operations (force push, reset --hard, branch -D) without explicit confirmation
- Do not take actions that affect shared state (posting comments, triggering deploys) without confirmation

---

## Project Structure

> **TODO**: Update this section once the project is initialized with source code.

```
(empty — project not yet scaffolded)
```

---

## Development Commands

> **TODO**: Add commands once the project stack is decided.

```bash
# Example placeholders — replace with actual commands:
# npm install       # Install dependencies
# npm run dev       # Start dev server
# npm test          # Run tests
# npm run lint      # Lint code
# npm run build     # Production build
```

---

## Architecture and Key Conventions

> **TODO**: Document architecture, key modules, and conventions as the project develops.

---

## Dependencies and Integrations

> **TODO**: List major dependencies and any external services/APIs this project integrates with.
