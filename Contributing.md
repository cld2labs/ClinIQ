# Contributing to ClinIQ

Thanks for your interest in contributing to ClinIQ.

ClinIQ is an open-source clinical document question-answering app built with a Flask backend, a React frontend, and a retrieval-augmented generation pipeline. We welcome improvements across the codebase, documentation, bug reports, design feedback, and workflow polish.

Before you start, please read the relevant section below. It helps keep contributions focused, reviewable, and aligned with the current project setup.

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

# Check Git
git --version
```

New to contributing?

1. Open an issue or pick an existing one to work on.
2. Sync your branch from `dev`.
3. Follow the local setup guide below.
4. Run the app locally and verify your change before opening a PR.

## Table of contents

- [How do I...?](#how-do-i)
  - [Get help or ask a question?](#get-help-or-ask-a-question)
  - [Report a bug?](#report-a-bug)
  - [Suggest a new feature?](#suggest-a-new-feature)
  - [Set up ClinIQ locally?](#set-up-cliniq-locally)
  - [Start contributing code?](#start-contributing-code)
  - [Improve the documentation?](#improve-the-documentation)
  - [Submit a pull request?](#submit-a-pull-request)
- [Code guidelines](#code-guidelines)
- [Pull request checklist](#pull-request-checklist)
- [Branching model](#branching-model)
- [Thank you](#thank-you)

---

## How do I...

### Get help or ask a question?

- Start with the main project docs in [`README.md`](./README.md), [`Docs/QUICKSTART.md`](./Docs/QUICKSTART.md), and [`Docs/PROJECT_DOCUMENTATION.md`](./Docs/PROJECT_DOCUMENTATION.md).
- If something is unclear, open a GitHub issue with your question and the context you already checked.

### Report a bug?

1. Search existing issues first.
2. If the bug is new, open a GitHub issue.
3. Include the environment, what happened, what you expected, and exact steps to reproduce.
4. Add screenshots, logs, or request/response details if relevant.

### Suggest a new feature?

1. Open a GitHub issue describing the feature.
2. Explain the problem, who it helps, and how it fits ClinIQ.
3. If the change is large, get alignment in the issue before writing code.

### Set up ClinIQ locally?

#### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Git
- An OpenAI API key

#### Option 1: Local development

##### Step 1: Clone the repository

```bash
git clone git@github-work:cld2labs/ClinIQ.git
cd ClinIQ
```

##### Step 2: Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

##### Step 3: Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

##### Step 4: Configure environment variables

Create `configuration/.env` from `configuration/.env.example` if you want to provide an API key through environment variables:

```bash
cp configuration/.env.example configuration/.env
```

Minimum example:

```env
OPENAI_API_KEY=your_api_key_here
```

You can also enter the API key in the app's configuration panel at runtime.

##### Step 5: Start the backend

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
docker-compose -f configuration/docker-compose.yml up --build
```

Or from the `configuration` directory:

```bash
cd configuration
docker-compose up --build
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
2. Create a feature branch from `dev`.
3. Keep the change focused on a single problem.
4. Run the app locally and verify the affected workflow.
5. Update docs when behavior, setup, or architecture changes.
6. Open a pull request back to `dev`.

### Improve the documentation?

Documentation updates are welcome. Relevant files currently live in:

- [`README.md`](./README.md)
- [`Docs/QUICKSTART.md`](./Docs/QUICKSTART.md)
- [`Docs/PROJECT_DOCUMENTATION.md`](./Docs/PROJECT_DOCUMENTATION.md)
- [`frontend/README.md`](./frontend/README.md)

### Submit a pull request?

Follow the checklist below before opening your PR. Your pull request should:

- Stay focused on one issue or topic.
- Explain what changed and why.
- Include manual verification steps.
- Include screenshots or short recordings for UI changes.
- Reference the related GitHub issue when applicable.

Note: this repository currently includes automated security scanning on pull requests via GitHub Actions. If your PR triggers a scan failure, address it before requesting review.

---

## Code guidelines

- Follow the existing project structure and patterns before introducing new abstractions.
- Keep frontend changes consistent with the React + Vite + Tailwind setup already in use.
- Keep backend changes consistent with the Flask API and utility modules in `backend/utils`.
- Avoid unrelated refactors in the same pull request.
- Do not commit secrets, API keys, uploaded documents, or generated local database files.
- Prefer clear, small commits and descriptive pull request summaries.
- Update documentation when contributor setup, behavior, or API usage changes.

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
- You are opening the pull request against `dev`.
- You reviewed any GitHub Action scan failures and resolved them.

If one or more of these are missing, the pull request may be sent back for changes before review.

---

## Branching model

- Base new work from `dev`.
- Open pull requests against `dev`.
- Use descriptive branch names such as `fix/upload-error-handling` or `docs/update-contributing-guide`.
- Rebase or merge the latest `dev` before opening your PR if your branch has drifted.

---

## Thank you

Thanks for contributing to ClinIQ. Whether you're fixing a bug, improving the docs, or refining the product experience, your work helps make the project more useful and easier to maintain.
