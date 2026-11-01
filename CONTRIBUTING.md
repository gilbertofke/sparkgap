# Contributing to Sparkgap

Sparkgap is an independent, open source tool for testing and debugging M-Pesa
Daraja integrations. It is not affiliated with Safaricom. This guide explains
how to propose a change so that it can be reviewed and merged quickly.

## Ground rules

- Sandbox only. Never use real money, real customer data or production
  credentials, in code, tests, fixtures, issues or logs.
- Never commit secrets. The repository ignores `.env`; copy `.env.example` for
  local use. All output must pass through `sparkgap.masking.mask`.
- Every Daraja fact (endpoint, code, limit, rule) is labelled `verified` or
  `community-reported`, with a source or a recorded sandbox result. If you
  cannot show where a fact came from, label it community-reported or leave it
  out.

## Setup

Requirements: Python 3.10 or newer and [uv](https://docs.astral.sh/uv/).

    git clone https://github.com/gilbertofke/sparkgap.git
    cd sparkgap
    uv sync

Run the same checks that CI runs before you push:

    uv run ruff check .
    uv run ruff format --check .
    uv run mypy src
    uv run pytest

## Workflow

1. Branch from an up-to-date `main`. Name the branch `type/short-description`,
   for example `feat/stk-query-check`.
2. Write a failing test first, then the smallest implementation that passes
   it. See [ADR-0003](docs/adr/0003-test-driven-development.md).
3. Commit each logical change separately, following the commit standard below.
4. Open a pull request against `main`. Fill in the template, including the
   tradeoffs section.
5. CI must pass. Pull requests are merged with rebase and merge, so your
   commits land on `main` exactly as you submit them. Tidy your history
   (`git rebase -i`) before asking for review.

## Commit standard

    type(scope): imperative summary

Types are feat, fix, test, docs, refactor, build, ci, chore and perf. The
summary is lowercase, in the imperative mood, at most 72 characters, with no
trailing period. Add a body when the reason for the change is not obvious.

Two rules matter most: one logical change per commit, and every commit leaves
lint, type checks and tests passing. The reasoning and the alternatives are in
[ADR-0002](docs/adr/0002-commit-convention-and-history.md).

Good: `feat(masking): mask secrets to first and last two characters`

Not good: `fixed stuff and added tests`

## Tests

Production code under `src/` is written test first, and a test and its
implementation go in the same commit. Unit tests must not use the network;
mock HTTP with respx. Tests that call the real sandbox carry the `live` marker
and are excluded from CI. Exploratory scripts under `scripts/` and
`docs/research/` are exempt, but must not be imported by `src/`.

## Decisions

A significant decision gets an ADR in `docs/adr/`. Copy
`docs/adr/0000-template.md`, use the next free number, and include the
alternatives you considered and what gets harder as a result. Open the ADR in
the same pull request as the change, or in an earlier one. Decisions are
never deleted; a reversed decision is marked superseded and linked to its
replacement.

## Reporting problems

Open an issue describing what you expected and what happened. Remove every key,
secret, token and phone number first. A security policy will be added before
the first release; until then, do not post anything sensitive in a public issue.
