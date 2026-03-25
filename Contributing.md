# Contributing to ClinIQ

Thanks for your interest in contributing to ClinIQ.

ClinIQ is an open-source clinical document question-answering app built with a Flask backend, a React frontend, and a retrieval-augmented generation (RAG) pipeline with hybrid search and intelligent reranking. We welcome improvements across the codebase, documentation, bug reports, design feedback, and workflow polish.

Before you start, read the relevant section below. It helps keep contributions focused, reviewable, and aligned with the current project setup.

---

## Quick Setup Checklist

Before you dive in, make sure you have these installed:

```bash
# Check Python (3.10+ recommended)
python --version

# Check Node.js (18+ recommended)
node --version

# Check npm
npm --version

# Check Docker
docker --version
docker compose version

# Check Git
git --version
```

New to contributing?

1. Open an issue or pick an existing one to work on.
2. Fork the repo and create a branch from `main`.
3. Follow the local setup guide below.
4. Run the app locally and verify your change before opening a PR.

## Table of contents

- [How do I...?](#how-do-i)
  - [Get help or ask a question?](#get-help-or-ask-a-question)
  - [Report a bug?](#report-a-bug)
  - [Suggest a new feature?](#suggest-a-new-feature)
  - [Fork and clone the repo?](#fork-and-clone-the-repo)
  - [Set up ClinIQ locally?](#set-up-cliniq-locally)
  - [Start contributing code?](#start-contributing-code)
  - [Improve the documentation?](#improve-the-documentation)
  - [Submit a pull request?](#submit-a-pull-request)
- [Branching model](#branching-model)
- [Commit conventions](#commit-conventions)
- [Code guidelines](#code-guidelines)
- [Pull request checklist](#pull-request-checklist)
- [Thank you](#thank-you)

---

## How do I...

### Get help or ask a question?

- Start with the main project docs in [`README.md`](./README.md), [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md), [`SECURITY.md`](./SECURITY.md), and [`Docs/QUICKSTART.md`](./Docs/QUICKSTART.md).
- If something is unclear, open a GitHub issue with your question and the context you already checked.

### Report a bug?

1. Search existing issues first.
2. If the bug is new, open a GitHub issue.
3. Include your environment, what happened, what you expected, and exact steps to reproduce.
4. Add screenshots, logs, request details, or response payloads if relevant.

### Suggest a new feature?

1. Open a GitHub issue describing the feature.
2. Explain the problem, who it helps, and how it fits ClinIQ.
3. If the change is large, get alignment in the issue before writing code.

### Fork and clone the repo?

All contributions should come from a **fork** of the repository. This keeps the upstream repo clean and lets maintainers review changes via pull requests.

#### Step 1: Fork the repository

Click the **Fork** button at the top-right of the [ClinIQ repo](https://github.com/cld2labs/ClinIQ) to create a copy under your GitHub account.

#### Step 2: Clone your fork

```bash
git clone https://github.com/<your-username>/ClinIQ.git
cd ClinIQ
```

#### Step 3: Add the upstream remote

```bash
git remote add upstream https://github.com/cld2labs/ClinIQ.git
```

This lets you pull in the latest changes from the original repo.

#### Step 4: Create a branch

Always branch off `main`. See [Branching model](#branching-model) for naming conventions.

```bash
git checkout main
git pull upstream main
git checkout -b <type>/<short-description>
```

### Set up ClinIQ locally?

#### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Git
- Docker with Docker Compose v2
- OpenAI API key (set via environment variable in backend/.env)

#### Option 1: Local development

##### Step 1: Configure environment variables

Create a backend `.env` file for the API key:

```bash
cd backend
echo "OPENAI_API_KEY=your_api_key_here" > .env
cd ..
```

Or configure your API key through environment variables at runtime.

##### Step 2: Install backend dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

##### Step 3: Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

##### Step 4: Start the backend

```bash
cd backend
python api.py
```

The backend runs at `http://localhost:5000`.

##### Step 6: Start the frontend

Open a second terminal:

```bash
cd frontend
npm run dev
```

The frontend runs at `http://localhost:3000`.

##### Step 7: Access the application

- Frontend: `http://localhost:3000`
- Backend health check: `http://localhost:5000/api/health`

#### Option 2: Docker

From the repository root:

```bash
docker compose up --build
```

This starts:

- Frontend on `http://localhost:3000`
- Backend on `http://localhost:5000`

#### Common troubleshooting

- If ports `3000` or `5000` are already in use, stop the conflicting process before starting ClinIQ.
- If document processing fails, confirm your OpenAI API key is valid and has available quota.
- If Docker fails to build, rebuild with `docker-compose -f configuration/docker-compose.yml up --build`.
- If Python packages fail to install, confirm you are using a supported Python version.

### Start contributing code?

1. Open or choose an issue.
2. [Fork the repo](#fork-and-clone-the-repo) and create a feature branch from `main`.
3. Keep the change focused on a single problem.
4. Run the app locally and verify the affected workflow.
5. Update docs when behavior, setup, configuration, or architecture changes.
6. Open a pull request back to upstream `main`.

### Improve the documentation?

Documentation updates are welcome. Relevant files currently live in:

- [`README.md`](./README.md)
- [`Docs/QUICKSTART.md`](./Docs/QUICKSTART.md)
- [`Docs/PROJECT_DOCUMENTATION.md`](./Docs/PROJECT_DOCUMENTATION.md)
- [`frontend/README.md`](./frontend/README.md)

### Submit a pull request?

1. Push your branch to your fork.
2. Go to the [ClinIQ repo](https://github.com/cld2labs/ClinIQ) and click **Compare & pull request**.
3. Set the base branch to `main`.
4. Fill in the PR template (it loads automatically).
5. Submit the pull request.

A maintainer will review your PR. You may be asked to make changes — push additional commits to the same branch and they will be added to the PR automatically.

Before opening your PR, sync with upstream to avoid merge conflicts:

```bash
git fetch upstream
git rebase upstream/main
```

Follow the checklist below and the [Pull request checklist](#pull-request-checklist) section.

---

## Branching model

- Fork the repo and base new work from `main`.
- Open pull requests against upstream `main`.
- Use descriptive branch names with a type prefix:

| Prefix | Use |
|---|---|
| `feat/` | New features or enhancements |
| `fix/` | Bug fixes |
| `docs/` | Documentation changes |
| `refactor/` | Code restructuring (no behavior change) |
| `chore/` | Dependency updates, CI changes, tooling |

Examples: `feat/add-pdf-support`, `fix/embedding-timeout`, `docs/update-quickstart`

---

## Commit conventions

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<optional scope>): <short description>
```

Examples:

```bash
git commit -m "feat(api): add hybrid search support"
git commit -m "fix(ui): resolve citation rendering issue"
git commit -m "docs: update troubleshooting guide"
```

Keep commits focused — one logical change per commit.

---

## Code guidelines

- Follow the existing project structure and patterns before introducing new abstractions.
- Keep frontend changes consistent with the React + Vite + Tailwind setup already in use.
- Keep backend changes consistent with the Flask service structure in `backend/`.
- Avoid unrelated refactors in the same pull request.
- Do not commit secrets, API keys, uploaded files, local `.env` files, or generated artifacts.
- Prefer clear, small commits and descriptive pull request summaries.
- Update documentation when contributor setup, behavior, environment variables, or API usage changes.

---

## Pull request checklist

Before submitting your pull request, confirm the following:

- You tested the affected flow locally.
- The application still starts successfully in the environment you changed.
- You removed debug code, stray logs, and commented-out experiments.
- You documented any new setup steps, environment variables, or behavior changes.
- You kept the pull request scoped to one issue or topic.
- You added screenshots for UI changes when relevant.
- You did not commit secrets or local generated data.
- You are opening the pull request against `main`.

If one or more of these are missing, the pull request may be sent back for changes before review.

---

## Thank you

Thanks for contributing to ClinIQ. Whether you're fixing a bug, improving the docs, or refining the product experience, your work helps make the project more useful and easier to maintain.
