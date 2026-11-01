# ADR-0001: Record decisions as ADRs

Status: accepted
Date: 2026-11-01

## Context
Sparkgap is an open source project that relies on contributors who were not
present when earlier decisions were made. Without a written
record, the reasons behind choices are lost, and the same debates repeat.

## Decision
Every major decision gets a short ADR in docs/adr/, using the template in
0000-template.md. ADRs are never deleted. A reversed decision is marked
superseded and linked to its replacement.

## Alternatives considered
Decisions in commit messages only: they are hard to find and have no
structure. Decisions in a wiki: it drifts from the code and has no review.
A single decisions file: it grows without bound and loses per-decision history.

## Consequences
Decisions are reviewed in pull requests like code. Writing an ADR costs a few
minutes per decision. The first six commits on main (gitignore, license,
readme, scaffold, masking, CI) were pushed directly because branch protection
could not exist before CI did. That is the only exception.
